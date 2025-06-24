from dice_game_functions import *

qc = createCircuit()
counts = ideal_simulator(qc)[0]
selected = returnSelectedState(counts)

decimal_number = int(selected, 2)
print(f"The dice has rolled. The number is {decimal_number}")  # Output: 3