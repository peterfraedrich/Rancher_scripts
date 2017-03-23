# Rancher Crap

## remove_stopped_containers_v2-beta.py
Will remove stopped containers via the Rancher API (v2-beta). Doesn't use any auth, feel free to extend to include auth.

#### 3rd pary Requires:
* Requests

#### Takes the following arguments:
* `--url, -u [str]` The base URL of your Rancher server (ex. `http://rancher`)
* `--port, -p [int]` The port your Rancher server is running on (ex. `8080`). Defaults to `8080`
* `--project, -r [str]` The Rancher project ID (ex. `1a7`). Found in the URI.
* `--batch, -b [int]` The number of stopped containers to remove in a single batch. Default is 100
* `--dryrun, -d` Performs a dry-run of the tasks. Takes no real action.
* `--exclude_images, -i [str/regex]` Excludes images with the [escaped] regex or string in them
* `--exclude_names, -n [str/regex]` Excludes containers with names of the [escaped] regex or string in them
* `--debug` Prints debug info; don't do this

#### TO DO
* API authentication
* Actual error handling