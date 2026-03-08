
import re

def check_narrative_blocks(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = [
        "report", "lifeline", "past", "future", "future3", "money", "relations",
        "ai", "bihang", "daily", "monthly", "yearly"
    ]
    
    for sec in sections:
        # Look for elif section == "sec" followed by what looks like a block
        pattern = rf'elif section == "{sec}":\s+result = \[\](.*?)(elif|except|def|if __name__)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            block = match.group(1)
            line_offset = content[:match.start()].count('\n') + 1
            if 'result.append(f"""' not in block and 'result.append("""' not in block:
                print(f"Section {sec} at line ~{line_offset} appears BROKEN (missing append)")
            else:
                # Check for balance
                if block.count('"""') % 2 != 0:
                    print(f"Section {sec} at line ~{line_offset} has UNBALANCED triple double quotes")
                if block.count("'''") % 2 != 0:
                    print(f"Section {sec} at line ~{line_offset} has UNBALANCED triple single quotes")
        else:
            # Maybe it's not result = [] but just starting
            pass

if __name__ == "__main__":
    check_narrative_blocks('c:/Users/sungw/OneDrive/Desktop/manse.py')
