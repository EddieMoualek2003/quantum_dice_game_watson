import threading
import queue
import sys
from time import sleep

from dice_game_functions import *
from ibm_qc_interface import *
# from llm_interface import query_llm
# from wake_word_listener import active_listen  # still available for GUI button
from watson_stt import *

# ========== OUTPUT METHODS ==========

def display_on_leds(selected):
    try:
        print("[INFO] Attempting LED output...")
        raise NotImplementedError("LEDs not available.")
    except Exception as e:
        print(f"[WARNING] LED display failed: {e}")
        return False

def display_on_emulator(selected):
    print("[INFO] Attempting Sense HAT emulator output...")
    print(selected)
    try:
        from sense_emu import SenseHat
        sense = SenseHat()
        sense.clear()
        BLUE = (0, 0, 255)
        RED = (255, 0, 0)
        row = 3
        start_col = 2
        for i, bit in enumerate(selected):
            bit = int(bit)
            color = BLUE if bit else RED
            sense.set_pixel(start_col + i, row, color)
        sleep(3)
        sense.clear()
        raise NotImplementedError("SenseHAT emulator not working.")
    except Exception as e:
        print(f"[WARNING] Emulator display failed: {e}")
        return False

def display_cli(selected):
    print(f"[CLI OUTPUT] Quantum Dice Result: {selected}")

# ========== GAME LOGIC ==========

def run_dice(display_mode="cli"):
    qc = createCircuit()
    counts = ideal_simulator(qc)[0]
    selected = returnSelectedState(counts)

    if display_mode == "leds":
        if not display_on_leds(selected):
            print("[FALLBACK] Falling back to emulator.")
            if not display_on_emulator(list(str(selected))):
                display_cli(selected)
    elif display_mode == "emulator":
        if not display_on_emulator(list(str(selected))):
            display_cli(selected)
    else:
        display_cli(selected)

    return counts

# ========== CLI FALLBACK INTERFACE ==========

def fallback_worker(command_queue):
    print("[INFO] Running CLI fallback worker. Awaiting commands...")
    while True:
        cmd = command_queue.get()
        if cmd == "roll":
            run_dice(display_mode="cli")
        elif cmd == "exit":
            print("Exiting fallback worker.")
            break
        else:
            print(f"[WARNING] Unknown command: {cmd}")

# ========== GUI OR FALLBACK STARTER ==========

def start_game_thread(command_queue):
    try:
        from dice_game_ui import run_dice_gui_controlled as gui_runner
        gui_runner(command_queue)
    except Exception as e:
        print(f"[INFO] GUI not available or failed: {e}")
        fallback_worker(command_queue)

# ========== ENTRY POINT ==========

def dice_game_main():
    q = queue.Queue()
    start_game_thread(q)

if __name__ == "__main__":
    dice_game_main()
