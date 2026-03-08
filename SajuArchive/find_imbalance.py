
import re

def find_imbalance(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    state = False # False = closed, True = open
    
    for i, line in enumerate(lines):
        line_num = i + 1
        # In actual Python, """ in comments or single-line strings doesn't toggle triple quote state
        # but the simple count might reveal the issue if the user didn't use those.
        # Let's count them carefully.
        
        # We need to skip cases where """ is escaped or inside other strings... 
        # But in many of these Saju files, they are just blocks of f-strings.
        
        count = line.count('"""')
        if count % 2 != 0:
            state = not state
            print(f"Line {line_num:5d}: {line.strip()[:50]}")
            print(f"      State changed to: {'OPEN' if state else 'CLOSED'}")

if __name__ == "__main__":
    find_imbalance('c:/Users/sungw/OneDrive/Desktop/manse.py')
