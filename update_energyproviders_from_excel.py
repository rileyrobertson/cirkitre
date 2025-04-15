import pandas as pd
import json
import os

# File paths
EXCEL_FILE = "data/Public_Utility_Map_with_City.xlsx"
JSON_FILE = "energyproviders.json"

def generate_energy_providers_json(excel_file, json_file):
    """
    Reads the Excel file, processes the data, and generates the JSON file
    with the required structure.
    """
    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(excel_file, engine="openpyxl")
        
        # Ensure required columns exist
        required_columns = ["Utility Name", "city", "state_full", "Zip Code"]
        if not all(column in df.columns for column in required_columns):
            raise KeyError(f"One or more required columns are missing: {required_columns}")

        # Convert ZIP codes to strings with leading zeros
        df["Zip Code"] = df["Zip Code"].apply(lambda x: str(x).zfill(5) if not pd.isna(x) else "")

        # Group data by provider, city, and state
        grouped = df.groupby(["Utility Name", "city", "state_full"])["Zip Code"].apply(list).reset_index()

        # Create the JSON structure
        providers = []
        for provider_name, group in grouped.groupby("Utility Name"):
            service_areas = []
            for _, row in group.iterrows():
                service_areas.append({
                    "city": row["city"],
                    "state": row["state_full"],
                    "zip_codes": sorted(set(row["Zip Code"]))  # Ensure unique and sorted ZIP codes
                })
            providers.append({
                "provider": provider_name,
                "service_areas": service_areas
            })

        # Save the JSON structure to a file
        if os.path.dirname(json_file):  # Check if a directory path exists
            os.makedirs(os.path.dirname(json_file), exist_ok=True)
        with open(json_file, "w") as file:
            json.dump(providers, file, indent=4)
        print(f"Successfully updated {json_file}")
    
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    # Generate the JSON file
    generate_energy_providers_json(EXCEL_FILE, JSON_FILE)
