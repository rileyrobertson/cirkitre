import os
import json
import pandas as pd
from uszipcode import SearchEngine

# File paths
LOCAL_EXCEL_FILE = "List of Utility Companies.xlsx"  # Local file in the main repo
UPDATED_EXCEL_FILE = "data/Public_Utility_Map_with_City.xlsx"
ENERGY_PROVIDERS_JSON = "energyproviders.json"

# Mapping of state abbreviations to full state names
STATE_ABBREVIATIONS = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

def add_city_and_full_state_to_excel(file_path, updated_file_path):
    """
    Reads an Excel file, adds 'city' and 'state_full' columns using ZIP codes and state abbreviations, and saves the updated file.
    """
    # Initialize ZIP code search engine
    search = SearchEngine(simple_zipcode=True)

    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Debug: Print column names
        print("Columns in the Excel file:", df.columns)

        # Ensure "Zip Code" and "State" columns exist
        zip_column_name = "Zip Code"  # Updated to look for "Zip Code"
        state_column_name = "State"  # Column with state abbreviations
        if zip_column_name not in df.columns or state_column_name not in df.columns:
            print(f"The expected '{zip_column_name}' or '{state_column_name}' column is not present in the Excel file.")
            return

        # Add new "city" and "state_full" columns
        cities = []
        full_states = []
        for _, row in df.iterrows():
            # Process ZIP code
            zip_code = row[zip_column_name]
            if pd.isna(zip_code):
                cities.append("")
            else:
                zip_info = search.by_zipcode(str(zip_code).zfill(5).strip())
                if zip_info and zip_info.major_city:
                    cities.append(zip_info.major_city)
                else:
                    cities.append("")

            # Process state abbreviation to full state name
            state_abbreviation = row[state_column_name]
            full_states.append(STATE_ABBREVIATIONS.get(state_abbreviation, "Unknown"))

        # Add the "city" and "state_full" columns to the DataFrame
        df["city"] = cities
        df["state_full"] = full_states
        print(df.head())  # Debugging: Check if the "city" and "state_full" columns exist

        # Save the updated DataFrame to a new Excel file
        os.makedirs(os.path.dirname(updated_file_path), exist_ok=True)
        df.to_excel(updated_file_path, index=False, engine="openpyxl")
        print(f"File saved successfully at {updated_file_path}")
    except Exception as e:
        print(f"Error processing Excel file: {e}")

def parse_excel_file(file_path):
    """
    Parses the Excel file to extract energy providers and their service areas.
    """
    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(file_path, engine="openpyxl")

        # Extract relevant columns (adjust columns based on the actual structure of the file)
        providers_data = []
        for _, row in df.iterrows():
            provider = {
                "name": row.get("Utility Name", "Unknown").strip(),
                "service_areas": [
                    {
                        "city": row.get("city", "").strip(),
                        "state": row.get("state_full", "Unknown").strip(),
                        "zip_codes": [str(row.get("Zip Code", "Unknown")).zfill(5)]  # Ensure ZIP codes have leading zeros
                    }
                ]
            }
            providers_data.append(provider)

        print("Parsed Excel file successfully.")
        return providers_data
    except Exception as e:
        print(f"Error parsing Excel file: {e}")
        return []

def update_energy_providers():
    """
    Updates the energyproviders.json file with data from the Excel file.
    """
    # Add "city" and "state_full" columns to the Excel file
    add_city_and_full_state_to_excel(LOCAL_EXCEL_FILE, UPDATED_EXCEL_FILE)

    # Parse the updated Excel file
    new_providers = parse_excel_file(UPDATED_EXCEL_FILE)

    # Load existing energy providers data
    try:
        with open(ENERGY_PROVIDERS_JSON, "r") as file:
            energy_providers = json.load(file)
    except FileNotFoundError:
        energy_providers = []

    # Merge new data into the existing data
    for provider in new_providers:
        if provider not in energy_providers:
            energy_providers.append(provider)

    # Save the updated data to the JSON file
    with open(ENERGY_PROVIDERS_JSON, "w") as file:
        json.dump(energy_providers, file, indent=4)
    print(f"Updated {ENERGY_PROVIDERS_JSON} successfully!")

if __name__ == "__main__":
    update_energy_providers()
