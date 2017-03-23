#!/usr/bin/python

import requests
import json
import argparse
from pprint import pprint
from threading import Thread, Lock, current_thread

LOCK = Lock()
THREADS = []
NO_THREADS = 10
OK = 0
ERR = 0

parser = argparse.ArgumentParser(description='Prunes stopped containers from Rancher')
parser.add_argument('--url', '-u', required=True, help='URL of the Rancher server')
parser.add_argument('--port', '-p', required=False, help='The port Rancher server is running on (default 8080)', default=8080)
parser.add_argument('--project', '-r', required=True, help='the Rancher project code to delete from (ex. 1a7)')
parser.add_argument('--batch', '-b', required=False, help='The batch size, default is 100', default=100)
parser.add_argument('--dryrun', '-d', required=False, help='Perform no action', default=False, action='store_true')
args = parser.parse_args()

URL = args.url
PORT = args.port
PROJECT = args.project
BATCH = args.batch 
if args.dryrun == True:
    DRY = '(dry run)'
else:
    DRY = ''

def get_stopped_containers():
    uri = '{}:{}/v2-beta/projects/{}/containers/?state=stopped&limit={}'.format(URL, PORT, PROJECT, BATCH)
    return requests.get(uri).text

class res_proto:
    status_code = 200

def remove_containers(container_list):
    global OK
    global ERR
    for c in container_list:
        if args.dryrun == False:
            res = requests.delete(c['url'])
        if args.dryrun == True:
            res = res_proto
        LOCK.acquire()
        if res.status_code and int(res.status_code) != 200:
            ERR += 1
        else:
            OK += 1 
        print '{:3} {:24} {:30}'.format(res.status_code, c['id'], c['image'])
        LOCK.release()

def spawn_threads(container_list):
    clist = [ container_list[i::NO_THREADS] for i in xrange(NO_THREADS) ]
    for t in range(NO_THREADS):
        thr = Thread(target=remove_containers, args=(clist[t],))
        thr.start()
        THREADS.append(thr)
    for t in THREADS:
        t.join()
    print 'Done. {} OK, {} ERR. {}'.format(OK, ERR, DRY)

if __name__ == '__main__':
    stopped_list = []
    containers = get_stopped_containers()
    c = json.loads(containers)
    for x in c['data']:
        stopped_list.append({'url': x['actions']['remove'], 'id' : x['name'], 'image' : x['imageUuid'] })
    print 'Removing {} stopped containers...{}'.format(len(stopped_list), DRY)
    spawn_threads(stopped_list)