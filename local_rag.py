import chromadb
from chromadb.utils import embedding_functions
import ollama

# 1. Connect to your local vault folder
client = chromadb.PersistentClient(path="./aware_chroma_db")

# 2. Wake up the "Translator" (The Embedding Model)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Open your specific medical collection
collection = client.get_collection(name="aware_medical_collection", embedding_function=sentence_transformer_ef)

# 4. Get the user's question
user_query = input("\nAsk A.W.A.R.E: ")

# 5. Search the vault (A1 Priority)
results = collection.query(
    query_texts=[user_query],
    n_results=3
)

# 6. Extract the textbook text (The Glue)
# This joins the 3 best paragraphs into one big string
context = " ".join(results['documents'][0])

# 7. The Final Prompt (The Instructions for Mistral)
prompt = f"Using only this medical context: {context}. Answer this: {user_query}"

# 8. The Handshake (Talking to Mistral)
response = ollama.chat(model='mistral', messages=[
    {'role': 'user', 'content': prompt}
])

# 9. The Result!
print("\n--- A.W.A.R.E RESPONSE ---")
print(response['message']['content'])