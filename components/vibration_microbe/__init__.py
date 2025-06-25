from state import Bacteria, State


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
    current_strength = 50
    client.publish("event/microbe-on", f"{map[state.bacteria]}:{current_strength}")

