import os
import json
import pandas as pd
from uszipcode import SearchEngine

# File paths
LOCAL_EXCEL_FILE = "List of Utility Companies.xlsx"  # Local file in the main repo
UPDATED_EXCEL_FILE = "data/Public_Utility_Map_with_City.xlsx"
ENERGY_PROVIDERS_JSON = "energyproviders.json"

def add_city_to_excel(file_path, updated_file_path):
    """
    Reads an Excel file, adds a 'city' column using ZIP codes, and saves the updated file.
    """
    # Initialize ZIP code search engine
    search = SearchEngine(simple_zipcode=True)

    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Debug: Print column names
        print("Columns in the Excel file:", df.columns)

        # Ensure "Zip Codes" column exists
        zip_column_name = "Zip Codes"  # Adjust this if the name is different
        if zip_column_name not in df.columns:
            print(f"The expected '{zip_column_name}' column is not present in the Excel file.")
            return

        # Add a new "city" column
        cities = []
        for zip_code in df[zip_column_name]:
            if pd.isna(zip_code):
                cities.append("")
                continue

            # Get city name using the ZIP code
            zip_info = search.by_zipcode(str(zip_code).strip())
            if zip_info and zip_info.major_city:
                cities.append(zip_info.major_city)
                print(f"ZIP: {zip_code} -> City: {zip_info.major_city}")  # Debugging line
            else:
                cities.append("")
                print(f"ZIP: {zip_code} -> City: Not found")  # Debugging line

        # Add the "city" column to the DataFrame
        df["city"] = cities
        print(df.head())  # Debugging: Check if the "city" column exists

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
                        "state": row.get("State", "Unknown").strip(),
                        "zip_codes": [row.get("Zip Codes", "Unknown")]
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
    # Add "city" column to the Excel file
    add_city_to_excel(LOCAL_EXCEL_FILE, UPDATED_EXCEL_FILE)

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
