import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import ollama
import numpy as np
from sentence_transformers import CrossEncoder

# =====================================================================
# 1. INITIALIZE SYSTEM
# =====================================================================
print("[ ⚙️ BOOTING A.W.A.R.E. V6.0 (THE DEEP AUDITOR) ENGINE... ]")

# The Semantic Retriever (Fast Math)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./aware_chroma_db") 
collection = client.get_collection(name="aware_medical_collection", embedding_function=sentence_transformer_ef)

# The Bouncer (Deep Reader)
print("⏳ Loading Cross-Encoder Model (This might take a few seconds)...")
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

print("[ ✅ SYSTEM ONLINE: Two-Stage Pipeline Ready ]\n")

# =====================================================================
# 2. THE TWO-STAGE PIPELINE
# =====================================================================
def run_cross_encoder_pipeline(user_query):
    print("\n" + "="*60)
    print("🔍 INITIATING TWO-STAGE SEARCH (COSINE + CROSS-ENCODER)...")
    print("="*60)

    # --- STAGE 1: THE WIDE NET (Fast Retrieval) ---
    print("🎣 STAGE 1: Casting a wide net (Pulling top 15 chunks via Cosine)...")
    results = collection.query(
        query_texts=[user_query], 
        n_results=15, 
        include=["documents", "distances"] 
    )
    raw_chunks = results['documents'][0]

    # --- STAGE 2: THE DEEP AUDITOR (Re-Ranking) ---
    print("🧠 STAGE 2: Cross-Encoder is reading and grading chunks...")
    
    # CrossEncoder requires input as pairs: [[query, chunk1], [query, chunk2], ...]
    pairs = [[user_query, chunk] for chunk in raw_chunks]
    
    # Get the logical scores
    cross_scores = cross_encoder.predict(pairs)
    
    # Sort the chunks based on the new Cross-Encoder scores (Highest is best)
    # np.argsort returns indices from lowest to highest, so we reverse it [::-1]
    ranked_indices = np.argsort(cross_scores)[::-1]
    
    # 🚨 THE SHIELD: Keep only the absolute best 3 chunks!
    top_n = 3
    best_indices = ranked_indices[:top_n]
    best_chunks = [raw_chunks[i] for i in best_indices]
    best_scores = [cross_scores[i] for i in best_indices]

    # --- STEP 3: THE RE-RANKER LEADERBOARD ---
    print("\n[ 📊 CROSS-ENCODER RANKING (TOP 3 SURVIVORS) ]")
    print("Note: Cross-Encoder uses Logits. HIGHER score = Better match.\n")
    
    for i in range(len(best_chunks)):
        print(f"  🏆 Rank {i+1} [Re-Ranker Score: {best_scores[i]:.4f}]")
        print(f"     {best_chunks[i][:100].replace('/n', ' ')}...")
        print("     -")

    # --- STEP 4: DIRECT LLM GENERATION ---
    print("\n[ 🧠 GENERATING STRICT EXTRACTION... ]")
    context = "\n\n".join(best_chunks)
    
    user_prompt = f"""
You are a strict data-extraction script. Your only job is to extract text from the REFERENCE MATERIAL and format it.

--- REFERENCE MATERIAL ---
{context}

--- USER QUERY ---
{user_query}

--- REQUIRED OUTPUT FORMAT ---
You MUST respond using exactly this template. Do not add intro or outro text.

**Identified Herbs/Treatments:** [Extract names of herbs/oils from the text]
**Instructions:** [Extract how to use them from the text]
**Warning:** [Extract any warnings from the text, or say "None"]
"""
    
    response = ollama.chat(model='mistral', messages=[
        {'role': 'user', 'content': user_prompt.strip()}
    ], options={
        'temperature': 0.0, 
        'top_k': 1          
    })
    
    print("\n==========================================")
    print("🏥 FINAL ASSESSMENT:")
    print("==========================================")
    print(response['message']['content'])
    print("==========================================\n")

# =====================================================================
# 3. INTERACTIVE TERMINAL LOOP
# =====================================================================
while True:
    try:
        user_input = input("\nEnter Patient Query (or type 'exit' to quit): ")
        
        if user_input.lower() == 'exit':
            print("Shutting down Engine...")
            break
        if user_input.strip() == "":
            continue
            
        run_cross_encoder_pipeline(user_input)
        
    except KeyboardInterrupt:
        print("\nForce Quitting...")
        break