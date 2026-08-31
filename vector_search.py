import chromadb
from chromadb.utils import embedding_functions

def run_smart_search():
    print("🧠 A.W.A.R.E. Vector Search Terminal 🧠")
    print("Loading AI Embedding Engine... (This takes a few seconds)")

    # 1. Connect to the ChromaDB folder you just built
    chroma_client = chromadb.PersistentClient(path="./aware_chroma_db")

    # 2. Load the EXACT same math model we used to build the database
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    # 3. Open the medical collection
    collection = chroma_client.get_collection(
        name="aware_medical_collection",
        embedding_function=sentence_transformer_ef
    )
    
    print("\n✅ Brain loaded! Type 'quit' to exit.")

    while True:
        query = input("\nAsk A.W.A.R.E. a medical concept or symptom: ")
        
        if query.lower() == 'quit':
            break
            
        print(f"Translating '{query}' into vectors and searching...")

        # 4. The Magic: Querying by meaning, not just exact spelling
        # n_results=3 means we want the top 3 most relevant 500-word chunks
        results = collection.query(
            query_texts=[query],
            n_results=3
        )

        # 5. Display the results cleanly
        if not results['documents'][0]:
            print("❌ No matches found.")
        else:
            for i, doc in enumerate(results['documents'][0]):
                print(f"\n--- 📄 SMART CHUNK {i+1} ---")
                print(doc)
            print("\n" + "="*50)

if __name__ == "__main__":
    run_smart_search()