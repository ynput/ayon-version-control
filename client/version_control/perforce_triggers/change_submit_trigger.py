import urllib.request
import json
import os
import sys
import datetime

AYON_SERVER_URL = os.environ.get("AYON_SERVER_URL")
AYON_API_KEY = os.environ.get("AYON_API_KEY")

if not all(AYON_SERVER_URL, AYON_API_KEY):
    raise ValueError("Both AYON_SERVER_URL and AYON_API_KEY env vars "
                     "must be set")

ADDON_NAME = "version_control"

headers = {
    'x-api-key': AYON_API_KEY,
    'Content-Type': 'application/json',  # Optional: Specify content type if needed
}


def get_json_response_data(url, headers):
    global data

    req = urllib.request.Request(url, headers=headers)
    # Make a GET request
    with urllib.request.urlopen(req) as response:
        # Read and decode the response data
        data = response.read().decode()

        ret_code = response.getcode()
        if ret_code != 200:
            raise ValueError(f"Call failed:{ret_code}")

        # Optionally, parse JSON data if applicable
        try:
            return json.loads(data)

        except json.JSONDecodeError:
            print("Response is not in JSON format.")


def get_addon_version():
    # Define the URL
    url = f"{AYON_SERVER_URL}/api/bundles"
    bundle_data = get_json_response_data(url, headers)

    production_bundle_name = bundle_data["productionBundle"]
    bundle_addons = None
    for bundle in bundle_data["bundles"]:
        if bundle["name"] == production_bundle_name:
            bundle_addons = bundle["addons"]
            break
    if not bundle_addons:
        raise ValueError(f"Cannot find {production_bundle_name}")

    bundle_version = bundle_addons.get(ADDON_NAME)
    if not bundle_version:
        raise ValueError(
            f"{ADDON_NAME} not installed in {production_bundle_name}")
    return bundle_version


def call_change_submit_endpoint(
        addon_name, addon_version, user, changelist, client):
    url = f"{AYON_SERVER_URL}/api/addons/{addon_name}/{addon_version}/change_submit"

    payload = {
        "user": user,
        "changelist": changelist,
        "client": client
    }
    json_data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(url, data=json_data, headers=headers)
    req.add_header('Content-Type', 'application/json; charset=utf-8')

    # Send the request and get the response
    with urllib.request.urlopen(req) as response:
        response_body = response.read().decode()  # Read and decode the
        print(response_body)


def log_to_file(message):
    with open("/tmp/trigger.log", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()}: {message}\n")


def main():
    if len(sys.argv) < 4:
        log_to_file("Error: Not enough arguments provided.")
        return 1

    changelist_id = sys.argv[1]  # %change%
    user = sys.argv[2]   # %user%
    client = sys.argv[3]  # %client%

    # Log the changelist submission details
    log_to_file(f"Changelist {changelist_id} submitted by {user}")

    addon_version = get_addon_version()
    call_change_submit_endpoint(
        ADDON_NAME, addon_version, user, changelist_id, client)

    return 0  # Return 0 to indicate success


if __name__ == "__main__":
    exit(main())
