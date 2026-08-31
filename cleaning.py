import re

input_file = "ALL IN ONE.txt"
output_file = "CLEANED_ALL_IN_ONE.txt"

print("Firing up the Master Cleaner (Maximum Power)...")

try:
    with open(input_file, "r", encoding="utf-8") as f:
        # Read the file line-by-line instead of one giant chunk
        lines = f.readlines()

    cleaned_lines = []
    
    for line in lines:
        line = line.strip() # Remove invisible newlines/spaces at the ends
        
        # 1. NUKE THE HEADERS & PAGE DIVIDERS COMPLETELY
        # If the line contains these specific words or symbols, skip it entirely.
        if "SOURCE TEXTBOOK:" in line or "📖" in line:
            continue
        if line.startswith("=====") or line.endswith("====="):
            continue
        if line.startswith("----- PAGE") and line.endswith("-----"):
            continue
        
        # 2. NUKE STRAY PAGE NUMBERS
        # If the line is literally just a number, skip it.
        if line.isdigit():
            continue

        # 3. NUKE WEIRD BORDERS LIKE "/ cHarter \\"
        # This deletes slashes, backslashes, pipes, dashes, equals, and asterisks from the edges
        line = re.sub(r'^[\\/\|\-_=\*]+', '', line)  # Clean the left edge
        line = re.sub(r'[\\/\|\-_=\*]+$', '', line)  # Clean the right edge
        line = line.strip() # Clean any spaces left behind

        # Keep the line if it's an intentional blank line, or if it has actual words left
        if line == '' or len(line) > 2:
            cleaned_lines.append(line)

    # 4. Join it all back together and fix massive blank gaps
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text.strip())

    print(f"\n✅ DONE! Checked every single line. Saved to '{output_file}'!")

except Exception as e:
    print(f"\n❌ Oops, something went wrong:\n{e}")