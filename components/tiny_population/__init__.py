import os
import pandas as pd
from state import State, Country, Bacteria


# Mapping from enums to strings used in data files
country_map = {
    Country.NL: 'Netherlands',
    Country.ES: 'Spain',
    Country.BG: 'Bulgaria',
}

bacteria_map = {
    Bacteria.ECOLI: 'E.coli',
    Bacteria.KLEBSIA: 'Klebsiella',
    Bacteria.PSEUDO: 'Pseudomonas',
}

available_data_types = [
    'Percentage of people resistant',
    'Amount of deaths per 10,000 people',
    'TBD'
]

def get_population_data(state: State, data_type: str):
    """
    Retrieves and displays population data based on the given state and data type.
    """
    if not all([state.country, state.bacteria, state.year, data_type]):
        print("Incomplete state for tiny_population data retrieval.")
        return

    folder = data_type
    country = country_map.get(state.country)
    bacteria = bacteria_map.get(state.bacteria)
    year = state.year
    
    if not all([country, bacteria, year]):
        print("Invalid state values provided for data retrieval.")
        return

    value_result = None
    associated_value = None
    susceptible_value = None

    try:
        # NOTE: The paths to data files might need adjustment.
        base_data_path = 'data/tiny_population'

        if folder == "Percentage of people resistant":
            file_path = os.path.join(base_data_path, folder, f"{bacteria}.csv")
            df = pd.read_csv(file_path)
            filtered = df[(df["RegionName"] == country) & (df["Time"] == year)]
            if not filtered.empty:
                value_result = filtered.iloc[0]["NumValue"]

        elif folder == "TBD":
            # Assuming TBD data is in a file within a 'TBD' subdirectory of data
            tbd_folder_path = os.path.join(base_data_path, folder)
            if os.path.exists(tbd_folder_path) and os.listdir(tbd_folder_path):
                file_path = os.path.join(tbd_folder_path, os.listdir(tbd_folder_path)[0])
                df = pd.read_csv(file_path)
                filtered = df[(df["CountryName"] == country) & (df["Year"] == year)]
                if not filtered.empty:
                    value_result = filtered.iloc[0]["Percentage"]

        elif folder == "Amount of deaths per 10,000 people":
            deaths_folder_path = os.path.join(base_data_path, folder)
            found_file = False
            if os.path.exists(deaths_folder_path):
                for file in os.listdir(deaths_folder_path):
                    if file.lower().endswith('.csv') and country.lower() in file.lower():
                        file_path = os.path.join(deaths_folder_path, file)
                        found_file = True
                        break
            
            if found_file:
                df = pd.read_csv(file_path)
                filtered = df[(df["Pathogen"] == bacteria) & (df["Year"] == year)]
                if not filtered.empty:
                    try:
                        associated_value = filtered[filtered["Infectious"] == "Associated"].iloc[0]["Value"]
                        susceptible_value = filtered[filtered["Infectious"] == "Susceptible"].iloc[0]["Value"]
                    except IndexError:
                        print("Warning: One of the Infectious types was not found.")
            else:
                 print(f"Warning: No data file found for country '{country}' in '{deaths_folder_path}'")


        # --- Display Results ---
        print("\n🔍 Result for Tiny Population:")
        if folder == "Amount of deaths per 10,000 people":
            print(f"  Associated: {associated_value}")
            print(f"  Susceptible: {susceptible_value}")
        else:
            print(f"  Value: {value_result}")

    except FileNotFoundError:
        print(f"\n❌ Error: Data file not found. Checked in path starting with 'data/{folder}'")
    except Exception as e:
        print(f"\n❌ Error processing the data: {e}")

def run_tiny_population(state: State, client):
    p1 = get_population_data(state, "Percentage of people resistant")
    p2 = get_population_data(state, "Amount of deaths per 10,000 people")
    p3 = get_population_data(state, "TBD")

    client.publish("event/tiny-population-on", f"{state.country}/{state.bacteria}/{state.year}/{p1},{p2},{p3}")
