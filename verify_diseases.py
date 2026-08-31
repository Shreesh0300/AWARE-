import re

print("🔍 Scanning 31.8 GB vault for general diseases...\n")

file_path = "HF_MEDICAL_DATA.txt"

# Dictionary to track which conditions we've found
targets = {
    "heart attack": False,
    "eye pain": False,
    "headache": False,
    "skin disease": False
}

current_chunk = ""

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("---"):
                if current_chunk:
                    chunk_lower = current_chunk.lower()
                    
                    # Check our target list
                    for condition in list(targets.keys()):
                        # If we haven't found a chunk for this condition yet
                        if not targets[condition]: 
                            # Using \b to ensure we match the exact phrase
                            if re.search(r'\b' + condition + r'\b', chunk_lower):
                                print(f"🎯 MATCH FOUND FOR: [ {condition.upper()} ]")
                                print(current_chunk.strip())
                                print("\n" + "="*80 + "\n")
                                
                                # Mark it as found so we don't print 1,000 headaches
                                targets[condition] = True
                                
                    # If all targets are found (all values are True), stop scanning
                    if all(targets.values()):
                        break
                            
                # Reset for the new chunk
                current_chunk = line
            else:
                current_chunk += line

    print("✅ Scan complete! Final Report:")
    for condition, found in targets.items():
        status = "Found" if found else "NOT FOUND"
        print(f"- {condition.capitalize()}: {status}")

except Exception as e:
    print(f"❌ Error reading file: {e}")