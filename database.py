import sqlite3

input_file = "CLEANED_ALL_IN_ONE.txt"
db_file = "AWARE_knowledge_base.db"

# --- THE NEW WORD-BASED CHUNKING SETTINGS ---
WORDS_PER_CHUNK = 500  # 500 words is roughly equivalent to our old 1000 characters
WORD_OVERLAP = 100     # 100-word overlap so we don't lose the context of the sentence

print("Connecting to the A.W.A.R.E. Database to rewire the brain...")

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 1. Nuke the old character-based table and start fresh
cursor.execute('DROP TABLE IF EXISTS medical_data')
cursor.execute('''
    CREATE TABLE medical_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_chunk TEXT
    )
''')

print("Reading the Master File...")
try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    print("Splitting 16 million characters into individual words...")
    # .split() automatically handles spaces, newlines, and tabs!
    all_words = text.split()
    total_words = len(all_words)
    
    print(f"Total words found: {total_words}. Slicing into smart chunks...")
    
    chunks_to_insert = []
    start = 0

    # 2. The New Word-Chunking Loop
    while start < total_words:
        end = start + WORDS_PER_CHUNK
        
        # Grab the specific slice of words from the list
        chunk_slice = all_words[start:end]
        
        # Glue those words back together into a readable paragraph with spaces
        chunk_text = " ".join(chunk_slice)
        
        chunks_to_insert.append((chunk_text,))
        
        # Move forward, but step back for the overlap
        start += (WORDS_PER_CHUNK - WORD_OVERLAP)

    print(f"Created {len(chunks_to_insert)} perfectly sized word-chunks! Injecting into database...")

    cursor.executemany('INSERT INTO medical_data (text_chunk) VALUES (?)', chunks_to_insert)
    conn.commit()
    conn.close()

    print(f"\n✅ Crisis averted! Database successfully rebuilt by WORD count in '{db_file}'.")

except Exception as e:
    print(f"\n❌ Oops, something went wrong:\n{e}")