
import sys

def trace_quotes(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pos = 0
    in_triple_double = False
    stack = []
    
    import re
    # Find all occurrences of triple quotes
    matches = list(re.finditer(r'"""|\'\'\'', content))
    
    state_double = False
    state_single = False
    
    for m in matches:
        q = m.group()
        line = content.count('\n', 0, m.start()) + 1
        if q == '"""':
            state_double = not state_double
            print(f"Line {line:5d}: Double Triple Toggle -> {'OPEN' if state_double else 'CLOSED'}")
        else:
            state_single = not state_single
            print(f"Line {line:5d}: Single Triple Toggle -> {'OPEN' if state_single else 'CLOSED'}")

if __name__ == "__main__":
    trace_quotes('c:/Users/sungw/OneDrive/Desktop/manse.py')
