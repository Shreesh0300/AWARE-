import os

print("⏩ Fast-forwarding past 31.8 GB to the absolute end...\n")

file_path = "HF_MEDICAL_DATA.txt"

try:
    # 'rb' opens the file in binary mode, allowing us to seek backwards
    with open(file_path, 'rb') as f:
        # Jump directly to the very last byte of the file
        f.seek(0, os.SEEK_END)
        
        # Jump backward by 3000 bytes (enough for the last few paragraphs)
        f.seek(-3000, os.SEEK_END)
        
        # Read those final bytes and decode them back into text
        # (errors='ignore' prevents crashes if we chopped a word in half when jumping)
        tail_bytes = f.read()
        tail_text = tail_bytes.decode('utf-8', errors='ignore')
        
        # Split into lines and grab the last 20
        lines = tail_text.splitlines()
        
        for line in lines[-20:]:
            if line.strip(): # Skip blank lines for cleaner reading
                print(line.strip())

    print("\n✅ End of file reached successfully!")

except Exception as e:
    print(f"❌ Error reading file: {e}")