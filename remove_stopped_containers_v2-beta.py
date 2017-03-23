#!/usr/bin/python

# imports
import requests
import json
import argparse
from pprint import pprint
from threading import Thread, Lock, current_thread
import re

# declare vars
URL = None
PORT = None
PROJECT = None
BATCH = None
DRY = None
EIMAGE = ''
ENAME = ''
DEBUG = None
LOCK = Lock()
THREADS = []
NO_THREADS = 10
OK = 0
ERR = 0

# parse args
parser = argparse.ArgumentParser(description='Prunes stopped containers from Rancher')
parser.add_argument('--url', '-u', required=True, help='URL of the Rancher server')
parser.add_argument('--port', '-p', required=False, help='The port Rancher server is running on (default 8080)', default=8080)
parser.add_argument('--project', '-r', required=True, help='the Rancher project code to delete from (ex. 1a7)')
parser.add_argument('--batch', '-b', required=False, help='The batch size, default is 100', default=100)
parser.add_argument('--dryrun', '-d', required=False, help='Perform no action', default=False, action='store_true')
parser.add_argument('--exclude_images', '-i', required=False, help='A regex to exclude images from removal')
parser.add_argument('--exclude_names', '-n', required=False, help='A regex to exclude container names from removal')
parser.add_argument('--debug', required=False, help='Enable debug output', action='store_true')
args = parser.parse_args()

class colors:
    HEADER = '\033[95m'
    DEBUG = '\033[38;5;240m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OKBLUE = '\033[38;5;30m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def debug(text, msg):
    if DEBUG:
        print '{}DEBUG: {:32} :: {}{}'.format(colors.DEBUG, text, msg, colors.ENDC) 

def conform_inputs(args):
    '''make sure our inputs are correct and make adjustments if we need'''
    global URL
    global PORT
    global PROJECT
    global BATCH
    global DRY
    global ENAME
    global EIMAGE
    global DEBUG
    DEBUG = args.debug
    URL = args.url
    if 'http://' not in URL and 'https://' not in URL:
        URL = 'http://' + URL
    try:
        PORT = int(args.port)
    except ValueError:
        print '{}--port type mismatch (must be int), defaulting to 8080{}'.format(colors.WARNING, colors.ENDC)
        PORT = 8080
    PROJECT = args.project
    try:
        BATCH = int(args.batch )
    except ValueError:
        print '{}--batch type mismatch (must be int), defaulting to 100{}'.format(colors.WARNING, colors.ENDC)
        BATCH = 100
    if args.dryrun == True:
        DRY = '(dry run)'
    else:
        DRY = ''
    if args.exclude_names:
        ENAME = args.exclude_names
    if args.exclude_images:
        EIMAGE = args.exclude_images
    debug('URL', URL)
    debug('PORT', PORT)
    debug('PROJECT', PROJECT)
    debug('BATCH', BATCH)
    debug('DRYRUN', DRY)
    debug('ENAME', ENAME)
    debug('EIMAGE', EIMAGE)
    debug('DEBUG', DEBUG)
    return

def get_stopped_containers():
    '''return a list of stopped containers'''
    uri = '{}:{}/v2-beta/projects/{}/containers/?state=stopped&limit={}'.format(URL, PORT, PROJECT, BATCH)
    debug('URI', uri)
    return requests.get(uri).text

class res_proto:
    '''this is so we can re-use the args.status_code class object with --dryrun'''
    status_code = 999

def remove_containers(container_list):
    '''performs the DELETE op for stopped containers'''
    global OK
    global ERR
    for c in container_list:
        if args.dryrun == False:
            res = requests.delete(c['url'])
        if args.dryrun == True:
            res = res_proto
        LOCK.acquire()
        if res.status_code and int(res.status_code) not in [200, 999]:
            ERR += 1
        elif re.match('2.*', str(res.status_code)):
            OK += 1 
        print '{}{:3} {:24} {:30}{}'.format(colors.OKGREEN, res.status_code, c['id'], c['image'], colors.ENDC)
        LOCK.release()

def spawn_threads(container_list):
    '''spawns threads'''
    clist = [ container_list[i::NO_THREADS] for i in xrange(NO_THREADS) ]
    debug('CLIST', clist)
    for t in range(NO_THREADS):
        thr = Thread(target=remove_containers, args=(clist[t],))
        thr.start()
        THREADS.append(thr)
    for t in THREADS:
        t.join()
    print 'Done. {} OK, {} ERR. {}'.format(OK, ERR, DRY)

if __name__ == '__main__':
    '''do the thing'''
    conform_inputs(args)
    stopped_list = []
    containers = get_stopped_containers()
    debug('CONTAINERS', containers)
    c = json.loads(containers)
    for x in c['data']:
        if args.exclude_names: 
            n = re.search(ENAME, x['name'], re.IGNORECASE)
        else:
            n = None
        if args.exclude_images:
            i = re.search(EIMAGE, x['imageUuid'], re.IGNORECASE)
        else:
            i = None
        if not n and not i:
            stopped_list.append({'url': x['actions']['remove'], 'id' : x['name'], 'image' : x['imageUuid'] })
        else:
            if n:
                print '{}{} matches name regex /{}/ -- excluding{}'.format(colors.OKBLUE, x['name'], ENAME, colors.ENDC)
            if i:
                print '{}{} matches image regex /{}/ -- excluding{}'.format(colors.OKBLUE, x['imageUuid'], EIMAGE, colors.ENDC)
    if len(stopped_list) < 1:
        print 'Found 0 stopped containers. Nothing to do. Exiting.'
    else:
        print 'Removing {} stopped containers...{}'.format(len(stopped_list), DRY)
        debug('STOPPED LIST', stopped_list)
        spawn_threads(stopped_list)

#EOF