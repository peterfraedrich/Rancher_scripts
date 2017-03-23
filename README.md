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

#### TO DO
* API authentication
* Exclusion regex for container name or image
* Actual error handling