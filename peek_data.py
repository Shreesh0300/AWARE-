print("🔬 Opening the 31.8 GB vault... reading the first 50 lines...\n")

file_path = "HF_MEDICAL_DATA.txt"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        for i in range(50):
            line = f.readline()
            if not line:
                break
            print(line.strip())
            
    print("\n✅ Peek complete! The file was safely closed.")

except Exception as e:
    print(f"❌ Error reading file: {e}")