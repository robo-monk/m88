from state import Bacteria, State


def vibration_microbe(state: State, client):
    map = {
        Bacteria.KLEBSIA: "K",
        Bacteria.PSEUDO: "P",
        Bacteria.ECOLI: "E",
    }
    current_strength = 50
    client.send("event/microbe-on", f"{map[state.bacteria]}:{current_strength}")

