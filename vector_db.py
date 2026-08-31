import sqlite3
import chromadb
from chromadb.utils import embedding_functions

# 1. Connect to our SQLite brain to grab the perfectly sized chunks
print("Fetching the 500-word chunks from SQLite...")
sqlite_conn = sqlite3.connect("AWARE_knowledge_base.db")
cursor = sqlite_conn.cursor()
cursor.execute("SELECT id, text_chunk FROM medical_data")
rows = cursor.fetchall()
sqlite_conn.close()

print(f"Loaded {len(rows)} chunks. Time to vectorize... 🧠")

# 2. Setup ChromaDB (This creates a folder called 'aware_chroma_db' in your project)
chroma_client = chromadb.PersistentClient(path="./aware_chroma_db")

# Use Chroma's default embedding model (Sentence Transformers: all-MiniLM-L6-v2)
# It is fast, highly accurate, and runs completely locally.
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Create or open the vector collection
collection = chroma_client.get_or_create_collection(
    name="aware_medical_collection",
    embedding_function=sentence_transformer_ef
)

# 4. Prepare the data for ChromaDB
documents = []
ids = []
metadatas = []

for row in rows:
    chunk_id = str(row[0]) # Chroma demands IDs be strings, not integers
    text = row[1]
    
    documents.append(text)
    ids.append(chunk_id)
    # We can add metadata so we know exactly where this came from
    metadatas.append({"source": "medical_textbooks"}) 

# 5. Inject into ChromaDB in batches
# Turning 6000 chunks into vectors takes a lot of CPU power, so we feed it 500 at a time.
batch_size = 500
total_chunks = len(documents)

print("\nConverting text to mathematical vectors.")
print("This might take a minute or two depending on your CPU. Grab a coffee... ☕\n")

for i in range(0, total_chunks, batch_size):
    end = min(i + batch_size, total_chunks)
    collection.add(
        documents=documents[i:end],
        metadatas=metadatas[i:end],
        ids=ids[i:end]
    )
    print(f"✅ Embedded and saved chunks {i} to {end}...")

print("\n🚀 BOOM! A.W.A.R.E. is now officially running on a Vector Database!")