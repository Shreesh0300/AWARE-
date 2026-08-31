import os

# Your custom mega-file name
master_filename = "ALL IN ONE.txt"

# Find all text files in the folder
all_files = os.listdir('.')
txt_files = [f for f in all_files if f.endswith('.txt')]

# Make sure we don't accidentally copy the ALL IN ONE file into itself!
if master_filename in txt_files:
    txt_files.remove(master_filename)

print(f"Found {len(txt_files)} textbook files. Stitching them together...")

# Open the ALL IN ONE file and start pasting everything inside
with open(master_filename, "w", encoding="utf-8") as master_file:
    for txt_file in txt_files:
        print(f"Adding: {txt_file}...")
        
        # Add a clear header for each new book
        master_file.write(f"\n\n{'='*50}\n")
        master_file.write(f"📖 SOURCE TEXTBOOK: {txt_file}\n")
        master_file.write(f"{'='*50}\n\n")
        
        # Read the individual textbook and append it
        with open(txt_file, "r", encoding="utf-8") as current_book:
            master_file.write(current_book.read())

print(f"\n✅ BOOM! All textbooks merged into '{master_filename}'.")