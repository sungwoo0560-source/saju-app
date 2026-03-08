
import sys

def find_first_imbalance(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    state_double = False # True = inside """
    state_single = False # True = inside '''
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # We only care about triple quotes that toggle the state.
        # This is a bit complex if there are both types, but usually they don't nest.
        
        # Count triple double quotes
        cd = line.count('"""')
        # Count triple single quotes
        cs = line.count("'''")
        
        if cd % 2 != 0:
            state_double = not state_double
            print(f"L{line_num:5d} [DOUBLE]: {'OPENED' if state_double else 'CLOSED'} - {line.strip()[:60]!r}")
            
        if cs % 2 != 0:
            state_single = not state_single
            print(f"L{line_num:5d} [SINGLE]: {'OPENED' if state_single else 'CLOSED'} - {line.strip()[:60]!r}")

if __name__ == "__main__":
    find_first_imbalance('c:/Users/sungw/OneDrive/Desktop/manse.py')
