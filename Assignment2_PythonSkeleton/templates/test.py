import sys
import input_parser
from emitter import Emitter
from receiver import Receiver
from mirror import Mirror
from laser_circuit import LaserCircuit

'''
Name:   Javier Herrera Saavedra
SID:    540159552
Unikey: jher0112

run - Runs the entire program. It needs to take in the inputs and process them
into setting up the circuit. The user can specify optional flags to perform
additional steps, such as -RUN-MY-CIRCUIT to run the circuit and -ADD-MY-MIRRORS
to include mirrors in the circuit.

You are free to add more functions, as long as you aren't modifying the
existing scaffold.
'''


def is_run_my_circuit_enabled(args: list[str]) -> bool:
    # only requires implementation once you reach RUN-MY-CIRCUIT
    '''
    Returns whether or not '-RUN-MY-CIRCUIT' is in args.

    Parameters
    ----------
    args - the command line arguments of the program
    '''
    i = 0
    while i < len(args):
        if "-RUN-MY-CIRCUIT" == args[i]:
            return True
        i += 1
    return False


def is_add_my_mirrors_enabled(args: list[str]) -> bool:
    # only requires implementation once you reach ADD-MY-MIRRORS
    '''
    Returns whether or not '-ADD-MY-MIRRORS' is in args.

    Parameters
    ----------
    args - the command line arguments of the program
    '''
    i = 0
    while i < len(args):
        if "-ADD-MY-MIRRORS" == args[i]:
            return True
        i += 1
    return False


def initialise_circuit(colour_frequency_ranges: dict = None) -> LaserCircuit:
    # only requires implementation once you reach GET-MY-INPUTS
    '''
    Gets the inputs for the board size, emitters and receivers and processes
    it to create a LaserCircuit instance and return it. You should be using
    the functions you have implemented in the input_parser module to handle
    validating each input.

    Returns
    -------
    A LaserCircuit instance with a width and height specified by the user's
    inputted size. The circuit should also include each emitter and receiver
    the user has inputted.
    '''
    # 1 Get input for board
    print("Creating circuit board...")

    while True:
        board_user = input("> ")
        board_call = input_parser.parse_size(board_user)
        if isinstance(board_call, tuple):
            break
    new_circuit = LaserCircuit(board_call[0], board_call[1], colour_frequency_ranges)
    print(f"{board_call[0]}x{board_call[1]} board created.\n")

    # 2 Get emitters MAX 10 or END EMITTERS
    print("Adding emitter(s)...")

    max_times = 10
    while True:
        # Check MAX 10
        if len(new_circuit.get_emitters()) == max_times:
            break
        emitter_user = input("> ")
        # Check END EMITTERS
        if emitter_user == "END EMITTERS":
            break
        emitter_call = input_parser.parse_emitter(emitter_user)
        # ADD EMITTERS
        if isinstance(emitter_call, Emitter):
            new_circuit.add_emitter(emitter_call)

    print(f"{len(new_circuit.get_emitters())} emitter(s) added.\n")

    # 3 Get receivers MAX 10 or END RECEIVERS
    print("Adding receiver(s)...")

    max_times = 10
    while True:
        # Check MAX 10
        if len(new_circuit.get_receivers()) == max_times:
            break
        receiver_user = input("> ")
        # Check END RECEIVERS
        if receiver_user == "END RECEIVERS":
            break
        receiver_call = input_parser.parse_receiver(receiver_user)
        # ADD RECEIVERS
        if isinstance(receiver_call, Receiver):
            new_circuit.add_receiver(receiver_call)

    print(f"{len(new_circuit.get_receivers())} receiver(s) added.\n")
    return new_circuit


def set_pulse_sequence(circuit: LaserCircuit, file_obj) -> None:
    # only requires implementation once you reach RUN-MY-CIRCUIT
    '''
    Handles setting the pulse sequence of the circuit.
    The lines for the pulse sequence will come from the a file named
    /home/input/<file_name>.in.
    You should be using the functions you have implemented in the input_parser module
    to handle validating lines from the file.

    Parameter
    ---------
    circuit - The circuit to set the pulse sequence for.
    file_obj - A file like object returned by the open()
    '''
    print("Setting pulse sequence...")

    # Emitters not set
    def emitters_not_set():
        print_tuple = "-- ("
        i = 0
        while i < len(circuit.emitters):
            if not circuit.emitters[i].is_pulse_sequence_set():
                print_tuple += circuit.emitters[i].get_symbol()
                if circuit.emitters[i] != circuit.emitters[-1]:
                    print_tuple += ', '
            i += 1
        print_tuple += ')'
        return print_tuple

    lines = file_obj.readlines()
    i = 0
    while i < len(lines):
        # list emitters not sequence set
        print(emitters_not_set())
        print(f"Line {i + 1}: {lines[i]}", end='')
        tuple_sequence = input_parser.parse_pulse_sequence(lines[i])  # tuple|None
        if isinstance(tuple_sequence, tuple):
            # NEED to check if the emitter exists in circuit
            exist_in_circuit = False
            k = 0
            while k < len(circuit.emitters):
                if tuple_sequence[0] == circuit.emitters[k].get_symbol():
                    exist_in_circuit = True
                    break
                k += 1
            if not exist_in_circuit:
                print(f"Error: emitter '{tuple_sequence[0]}' does not exist")
                i += 1
                continue

            # NEED to check if already set
            set_already = False
            j = 0
            while j < len(circuit.emitters):
                if tuple_sequence[0] == circuit.emitters[j].get_symbol():
                    if circuit.emitters[j].is_pulse_sequence_set():
                        print(f"Error: emitter '{tuple_sequence[0]}' already its pulse sequence set")
                        set_already = True
                        break
                    else:  # SET pulse
                        circuit.emitters[j].set_pulse_sequence(tuple_sequence[1], tuple_sequence[2])
                j += 1
            if set_already:
                i += 1
                continue
        i += 1  # this is when the input is correct
    print("\nPulse sequence set.\n")


def add_mirrors(circuit: LaserCircuit) -> None:
    # only requires implementation once you reach ADD-MY-MIRRORS
    '''
    Handles adding the mirrors into the circuit. You should be using the
    functions you have implemented in the input_parser module to handle
    validating each input.

    Parameters
    ----------
    circuit - the laser circuit to add the mirrors into
    '''
    print("Adding mirror(s)...")
    while True:
        user_input = input("> ")
        if user_input == "END MIRRORS":
            break
        checked_mirror = input_parser.parse_mirror(user_input)  # Mirror
        if isinstance(checked_mirror, Mirror):
            circuit.add_mirror(checked_mirror)
    print("{} mirror(s) added.".format(len(circuit.mirrors)))


def is_rgb_my_circuit_enabled(args: list[str]) -> bool:
    i = 0
    while i < len(args):
        if "-RGB-MY-CIRCUIT" == args[i]:
            return True
        i += 1
    return False


def load_colour_frequency_ranges() -> dict[str, tuple[int, int]] | None:
    file_name = '/home/input/visible_light_spectrum.in'
    try:
        with open(file_name, 'r')as f:
            colour_order = ['violet', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red']
            dict_colours = {}

            # Check 1 #Check line by line
            lines = f.readlines()
            if len(lines) != 7:
                print(f"Error: expected 7 lines, got {len(lines)}")
                return None

            # Check 2
            i = 0
            last_low_frequency = 0
            while i < len(lines):
                line = lines[i]
                line_num = i + 1
                parts_split_colon = line.strip().split(':')
                # Check 2.1 parts equal 2
                if len(parts_split_colon) != 2:
                    print(f"Error: line {line_num} - must be in format <color>: <high frequency>-<low frequency>")
                    return None
                colour = parts_split_colon[0].strip()
                frequency_range = parts_split_colon[1].strip().split('-')
                # Check 2.2 parts2 equals 2
                if len(frequency_range) != 2:
                    print(f"Error: line {line_num} - must be in format <color>: <high frequency>-<low frequency>")
                    return None
                high_frequency = frequency_range[0]
                low_frequency = frequency_range[1]
                # Check 3
                if colour != colour_order[i]:
                    print(f"Error: line {line_num} - colour must be {colour_order[i]}")
                    return None
                # Check 4
                try:
                    high_frequency = int(high_frequency)
                except ValueError:
                    print(f"Error: line {line_num} - both frequencies must be integers")
                    return None
                try:
                    low_frequency = int(low_frequency)
                except ValueError:
                    print(f"Error: line {line_num} - both frequencies must be integers")
                    return None
                # Check 5
                if high_frequency <= low_frequency:
                    print(f"Error: line {line_num} - high frequency must be higher than low frequency")
                    return None
                # Check 6
                if line_num > 1:
                    if last_low_frequency != high_frequency:
                        print(f"Error: line {line_num} - high frequency must equal to low frequency of previous colour")
                        return None
                last_low_frequency = low_frequency
                dict_colours[colour] = (high_frequency, low_frequency)
                i += 1
        return dict_colours
    except FileNotFoundError:
        print(f"-RGB-MY-CIRCUIT flag detected but input file {file_name} does not exist")
        return None



def main(args: list[str]) -> None:
    # only requires implementation once you reach GET-MY-INPUTS
    # will require extensions in RUN-MY-CIRCUIT and ADD-MY-MIRRORS
    '''
    Responsible for running all code related to the program.

    Parameters
    ----------
    args - the command line arguments of the program
    '''
    # Set up RGB
    dict_colors = None
    if is_rgb_my_circuit_enabled(args):
        print("<RGB-MY-CIRCUIT FLAG DETECTED!>") # \n
        dict_colors = load_colour_frequency_ranges()
        if dict_colors == None:
            exit(0)
        circuit = initialise_circuit(dict_colors)
    else:
        circuit = initialise_circuit()

    if is_add_my_mirrors_enabled(args):
        print("<ADD-MY-MIRRORS FLAG DETECTED!>\n")
        add_mirrors(circuit)
        print()
    circuit.print_board()
    print()

    if is_run_my_circuit_enabled(args):  # -RUN-MY-CIRCUIT
        print("<RUN-MY-CIRCUIT FLAG DETECTED!>\n")

        try:
            with open('/home/input/pulse_sequence.in', 'r') as file_obj:
                set_pulse_sequence(circuit, file_obj)
                circuit.run_circuit()
        except FileNotFoundError:
            print("Error: -RUN-MY-CIRCUIT flag detected but /home/input/pulse_sequence.in does not exist")
            return


if __name__ == '__main__':
    '''
    Entry point of program. We pass the command line arguments to our main
    program. We do not recommend modifying this.
    '''
    main(sys.argv)