import threading
import queue
import argparse
import sys
from time import sleep
import os

from dice_game_functions import *
from ibm_qc_interface import *
from wake_word_listener import passive_listen, active_listen
from watson_stt import *

# ========== INTERFACE CHECK ==========

def is_gui_available():
    """Check if GUI display is available (e.g., X11 or similar)."""
    return os.environ.get('DISPLAY') is not None

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

# ========== MAIN GAME LOGIC ==========

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

# ========== FALLBACK CLI WORKER ==========

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

# ========== GAME THREAD LAUNCHER ==========

def start_game_thread(command_queue):
    if is_gui_available():
        try:
            from dice_game_ui import run_dice_gui_controlled as gui_runner
            gui_runner(command_queue)
            return
        except Exception as e:
            print(f"[INFO] GUI failed to load: {e}")
    else:
        print("[INFO] No GUI environment detected.")

    fallback_worker(command_queue)

# ========== WAKE-WORD + SPEECH-TO-TEXT CONTROL ==========

def simulate_chatbot_loop(command_queue):
    while True:
        try:
            passive_listen()
            record_audio("test.wav", duration=5)
            spoken = transcribe_ibm("test.wav")

            if not spoken:
                print("[INFO] No speech detected.")
                continue

            print("LLM:", spoken)  # Or use query_llm(spoken) if enabled

            if any(k in spoken.lower() for k in ["roll", "dice", "throw"]):
                command_queue.put("roll")
            elif any(k in spoken.lower() for k in ["exit", "stop"]):
                command_queue.put("exit")
                sys.exit()

        except KeyboardInterrupt:
            command_queue.put("exit")
            break

# ========== ENTRY POINT ==========

def dice_game_main():
    q = queue.Queue()
    game_thread = threading.Thread(target=start_game_thread, args=(q,))
    game_thread.start()
    simulate_chatbot_loop(q)
    game_thread.join()

if __name__ == "__main__":
    dice_game_main()
