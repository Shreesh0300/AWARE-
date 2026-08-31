import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import ollama

# =====================================================================
# 1. INITIALIZE SYSTEM (Run once at boot)
# =====================================================================
print("[ ⚙️ BOOTING PURE COSINE ENGINE... ]")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./aware_chroma_db") 
collection = client.get_collection(name="aware_medical_collection", embedding_function=sentence_transformer_ef)
print("[ ✅ SYSTEM ONLINE ]\n")

# =====================================================================
# 2. THE MASTER PIPELINE (WITH X-RAY & RANKING)
# =====================================================================
def run_cosine_pipeline(user_query):
    print("\n" + "="*60)
    print("🔍 INITIATING SEMANTIC SEARCH...")
    print("="*60)

    # --- STEP 1: FETCH TOP 10 CANDIDATES & THEIR SCORES ---
    results = collection.query(
        query_texts=[user_query], 
        n_results=10,
        include=["documents", "distances"] 
    )
    
    best_chunks = results['documents'][0]
    distances = results['distances'][0]

    # --- STEP 2: THE X-RAY PREVIEW (RAW TEXT) ---
    print("\n[ 📥 X-RAY PREVIEW (RAW DB OUTPUT) ]")
    for i, chunk in enumerate(best_chunks):
        print(f"  [{i+1}] {chunk[:250].replace('/n', ' ')}...")
    print("-" * 60)

    # --- STEP 3: THE MATH LEADERBOARD ---
    print("\n[ 📊 COSINE SIMILARITY RANKING ]")
    print("Note: ChromaDB uses L2 Distance. Lower score = Better match.\n")
    
    for i in range(len(best_chunks)):
        print(f"  🏆 Rank {i+1} [Distance Score: {distances[i]:.4f}]")
        print(f"     {best_chunks[i][:80].replace('/n', ' ')}...")
        print("     -")

   # --- STEP 4: DIRECT LLM GENERATION ---
    print("\n[ 🧠 GENERATING STRICT ASSESSMENT... ]")
    context = "\n\n".join(best_chunks)
    
    # 🔥 THE NUCLEAR EXTRACTION PROMPT 🔥
    user_prompt = f"""
You are a strict data-extraction algorithm. You do NOT give general medical advice. You do NOT have outside knowledge.

TASK: Read the REFERENCE MATERIAL below. Extract the exact Ayurvedic herbs, treatments, or dosages mentioned that relate to the USER QUERY.

CRITICAL RULES:
1. If the REFERENCE MATERIAL says "use herb X for symptom Y", you must output that exactly.
2. DO NOT suggest over-the-counter drugs, antacids, or exercise unless they are literally printed in the REFERENCE MATERIAL.
3. If the answer is completely missing from the REFERENCE MATERIAL, output exactly: "I do not have enough verified medical data in my database to answer this safely."

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
    
    # Notice we dropped the 'system' role entirely. 
    # We shove everything into the 'user' prompt to force Mistral's attention.
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
# 3. INTERACTIVE TERMINAL LOOP (THE STEERING WHEEL)
# =====================================================================
while True:
    try:
        user_input = input("\nEnter Patient Query (or type 'exit' to quit): ")
        
        if user_input.lower() == 'exit':
            print("Shutting down Engine...")
            break
        if user_input.strip() == "":
            continue
            
        run_cosine_pipeline(user_input)
        
    except KeyboardInterrupt:
        print("\nForce Quitting...")
        break