import pandas as pd
from state import Bacteria, State, Country  # Assuming Country is also in state.py

# Function to retrieve the value


def get_value_from_csv(state: State) -> float | None:
    if not (state.bacteria and state.country and state.year):
        raise ValueError("State must have all fields set (bacteria, country, year).")

    # Map enum to file path
    file_map = {
        Bacteria.PSEUDO: "data/vibration_microbe/Pseudomonas-aeruginosa-resistance-data.csv",
        Bacteria.KLEBSIA: "data/vibration_microbe/Klebsiella-pneumoniae-resistance-data.csv",
        Bacteria.ECOLI: "data/vibration_microbe/Ecoli-resistance-data.csv"
    }

    file_path = file_map[state.bacteria]

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    try:
        row = df[(df["Year"] == state.year) & (df["Country"] == state.country.value)]
        if row.empty:
            print(f"No data for year {state.year} and country {state.country.value}")
            return None
        value = row["VibValue"].values[0]
        return value
    except KeyError as e:
        raise KeyError(f"Missing column in CSV: {e}")

def vibration_microbe(state: State, client):
    file_bacteria_map = {
        Bacteria.KLEBSIA: "klebsia",
        Bacteria.PSEUDO: "pseudo",
        Bacteria.ECOLI: "ecoli",
    }
    file_name = f"data/vibration-microbe/{file_bacteria_map[state.bacteria]}.csv"


    map = {
        Bacteria.KLEBSIA: "K",
        Bacteria.PSEUDO: "P",
        Bacteria.ECOLI: "E",
    }



    value = get_value_from_csv(state)
    current_strength = value if value is not None else 0  # fallback to 0 if no value
    client.publish("event/microbe-on", f"{map[state.bacteria]}:{current_strength}")
