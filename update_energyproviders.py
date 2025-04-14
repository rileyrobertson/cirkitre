import json
import requests

# Path to the APIs configuration file and energy providers JSON file
APIS_FILE = "apis.json"
ENERGY_PROVIDERS_FILE = "energyproviders.json"

def fetch_data_from_api(api_url):
    """
    Fetch data from a given API URL.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from {api_url}: {e}")
        return None

def update_energy_providers():
    """
    Fetch data from multiple APIs and update the energyproviders.json file.
    """
    # Load the list of APIs
    with open(APIS_FILE, "r") as apis_file:
        apis = json.load(apis_file)
    
    # Load existing energy providers data
    with open(ENERGY_PROVIDERS_FILE, "r") as energy_file:
        energy_providers = json.load(energy_file)

    # Fetch data from each API and update the JSON file
    for api in apis:
        print(f"Fetching data from {api['name']}...")
        data = fetch_data_from_api(api["url"])
        if data:
            # Normalize and integrate data into energy_providers
            for provider in data:
                # Assuming API data matches the schema; otherwise, normalize here
                energy_providers.append(provider)

    # Save the updated data
    with open(ENERGY_PROVIDERS_FILE, "w") as energy_file:
        json.dump(energy_providers, energy_file, indent=4)
    print(f"Updated {ENERGY_PROVIDERS_FILE} successfully!")

if __name__ == "__main__":
    update_energy_providers()