import chromadb
import ollama
import re
from rank_bm25 import BM25Okapi

# =====================================================================
# 1. INITIALIZE SYSTEM & THE "STOPWORD" FILTER
# =====================================================================
print("[ ⚙️ BOOTING A.W.A.R.E. V5.1 (KEYWORD + FILTER) ENGINE... ]")

# A master list of words that BM25 should completely ignore
STOPWORDS = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "should", "now", "im", "really", "bad"
])

def tokenize(text):
    # 1. Remove all punctuation using Regex
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    # 2. Split into words and delete any word in the STOPWORDS list
    return [word for word in clean_text.split() if word and word not in STOPWORDS]

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./aware_chroma_db") 
collection = client.get_collection(name="aware_medical_collection")

# Pull database into memory
all_data = collection.get()
corpus = all_data['documents']

# 🚨 THE FIX: We tokenize the entire database using our new filter
tokenized_corpus = [tokenize(doc) for doc in corpus]
bm25_engine = BM25Okapi(tokenized_corpus)

print(f"[ ✅ SYSTEM ONLINE: Loaded & Filtered {len(corpus)} chunks ]\n")

# =====================================================================
# 2. THE BM25 PIPELINE
# =====================================================================
def run_bm25_pipeline(user_query):
    print("\n" + "="*60)
    print("🔍 INITIATING EXACT KEYWORD SEARCH (BM25)...")
    print("="*60)

    # 🚨 THE FIX: We filter the user's query before searching
    tokenized_query = tokenize(user_query)
    print(f"   [Filtered Search Terms: {tokenized_query}]") # Let's print this so we can see it working!
    
    doc_scores = bm25_engine.get_scores(tokenized_query)
    top_n = 5
    best_chunks = bm25_engine.get_top_n(tokenized_query, corpus, n=top_n)
    top_scores = sorted(doc_scores, reverse=True)[:top_n]

    # --- STEP 2: THE X-RAY PREVIEW ---
    print("\n[ 📥 X-RAY PREVIEW (RAW TEXT) ]")
    for i, chunk in enumerate(best_chunks):
        print(f"  [{i+1}] {chunk[:250].replace('/n', ' ')}...")
    print("-" * 60)

    # --- STEP 3: THE MATH LEADERBOARD ---
    print("\n[ 📊 BM25 ALGORITHM RANKING ]")
    print("Note: BM25 uses TF-IDF logic. HIGHER score = Better match.\n")
    
    for i in range(len(best_chunks)):
        if top_scores[i] == 0:
            print(f"  ❌ Rank {i+1} [Score: 0.0000] - NO KEYWORD MATCH FOUND.")
        else:
            print(f"  🏆 Rank {i+1} [BM25 Score: {top_scores[i]:.4f}]")
            print(f"     {best_chunks[i][:80].replace('/n', ' ')}...")
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
            
        run_bm25_pipeline(user_input)
        
    except KeyboardInterrupt:
        print("\nForce Quitting...")
        break