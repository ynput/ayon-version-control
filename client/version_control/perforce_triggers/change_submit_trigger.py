import urllib.request
import json
import sys

AYON_SERVER_URL = ""   # SET HERE!
AYON_API_KEY = ""  # SET HERE!

ADDON_NAME = "version_control"

TRIGGER_SCRIPT_VERSION = "0.1.0"
PAYLOAD_SCHEMA_VERSION = "0.1.0"

headers = {
    'x-api-key': AYON_API_KEY,
    'Content-Type': 'application/json',
}


def get_json_response_data(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = response.read().decode()

        ret_code = response.getcode()
        if ret_code != 200:
            print(f"Call failed:{ret_code}")
            return 1
        try:
            return json.loads(data)

        except json.JSONDecodeError:
            print("Response is not in JSON format.")
            return 1


def get_addon_version():
    url = f"{AYON_SERVER_URL}/api/bundles"
    bundle_data = get_json_response_data(url, headers)

    production_bundle_name = bundle_data["productionBundle"]
    bundle_addons = None
    for bundle in bundle_data["bundles"]:
        if bundle["name"] == production_bundle_name:
            bundle_addons = bundle["addons"]
            break
    if not bundle_addons:
        print(f"Cannot find {production_bundle_name}")
        return 1

    bundle_version = bundle_addons.get(ADDON_NAME)
    if not bundle_version:
        print(
            f"{ADDON_NAME} not installed in {production_bundle_name}")
        return 1
    return bundle_version


def call_change_submit_endpoint(
        addon_name, addon_version, user, changelist, client):
    """Calls endpoint on AYON server to spawn event per submit"""
    url = f"{AYON_SERVER_URL}/api/addons/{addon_name}/{addon_version}/change_submit"

    payload = {
        "payload_schema_version": PAYLOAD_SCHEMA_VERSION,
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


def main():
    if len(sys.argv) < 4:
        print("Error: Not enough arguments provided. "
                    "Expected arguments %change% %user% %client%")
        return 1

    if not all([AYON_SERVER_URL, AYON_API_KEY]):
        print("Both AYON_SERVER_URL and AYON_API_KEY constants "
                    "must be set")
        return 1

    changelist_id = sys.argv[1]  # %change%
    user = sys.argv[2]   # %user%
    client = sys.argv[3]  # %client%

    # Log the changelist submission details
    print(f"Changelist {changelist_id} submitted by {user}")

    addon_version = get_addon_version()
    call_change_submit_endpoint(
        ADDON_NAME, addon_version, user, changelist_id, client)

    return 0  # Return 0 to indicate success


if __name__ == "__main__":
    exit(main())
