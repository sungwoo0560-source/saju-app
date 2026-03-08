
import sys

def check_mismatched_quotes(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_triple_double = False
    in_triple_single = False
    triple_double_start = -1
    triple_single_start = -1
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # This is a very simple check and doesn't handle escaping or nested quotes perfectly,
        # but it should give us a clue for large f-string blocks.
        
        if '"""' in line:
            # Toggle (simple count)
            count = line.count('"""')
            for _ in range(count):
                if in_triple_double:
                    in_triple_double = False
                else:
                    in_triple_double = True
                    triple_double_start = line_num
                    
        if "'''" in line:
            count = line.count("'''")
            for _ in range(count):
                if in_triple_single:
                    in_triple_single = False
                else:
                    in_triple_single = True
                    triple_single_start = line_num
                    
    if in_triple_double:
        print(f"Unclosed triple double quotes starting at line {triple_double_start}")
    if in_triple_single:
        print(f"Unclosed triple single quotes starting at line {triple_single_start}")
    if not in_triple_double and not in_triple_single:
        print("All triple quotes appear balanced (simple check)")

if __name__ == "__main__":
    check_mismatched_quotes('c:/Users/sungw/OneDrive/Desktop/manse.py')
