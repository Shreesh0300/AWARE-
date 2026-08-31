import re

print("🔍 Scanning 31.8 GB vault for 'cold', 'cough', and 'fever'...\n")

file_path = "HF_MEDICAL_DATA.txt"
max_results = 1 
found_count = 0
current_chunk = ""

keywords = [r'\bcold\b', r'\bcough\b', r'\bfever\b']

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # FIXED: Now it catches ALL dividers, with or without brackets
            if line.startswith("---"):
                if current_chunk:
                    chunk_lower = current_chunk.lower()
                    
                    # Check if ALL keywords exist in this single abstract
                    if all(re.search(kw, chunk_lower) for kw in keywords):
                        print(current_chunk.strip())
                        print("\n" + "="*80 + "\n") 
                        found_count += 1
                        
                        if found_count >= max_results:
                            break
                            
                # Reset for the new chunk
                current_chunk = line
            else:
                # Add the current line to the chunk we are building
                current_chunk += line

    if found_count == 0:
        print("CHUNKS NOT FOUND")
    else:
        print(f"✅ Found {found_count} highly specific chunks. Scanner stopped.")

except Exception as e:
    print(f"❌ Error reading file: {e}")