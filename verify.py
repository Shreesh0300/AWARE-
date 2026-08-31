import requests
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

# --- LOAD MODELS ---
print("Initializing Security Models...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
encoder_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# ==========================================
# STAGE 1: LOCAL COSINE RE-VERIFICATION
# ==========================================
def stage1_cosine_verify(user_query, chunks, threshold=0.35): # Lowered slightly for variety
    print("\n--- 🛡️ Stage 1: Local Cosine Re-Verification ---")
    if not chunks: return []
    query_emb = embed_model.encode([user_query])
    chunk_embs = embed_model.encode(chunks)
    scores = cosine_similarity(query_emb, chunk_embs)[0]
    
    survivors = []
    for i, score in enumerate(scores):
        if score > threshold:
            print(f"✅ Cosine Match ({score:.2f}) -> {chunks[i][:40]}...")
            survivors.append(chunks[i])
        else:
            print(f"❌ Cosine Too Low ({score:.2f}) -> {chunks[i][:40]}...")
    return survivors

# ==========================================
# STAGE 2: BM25 (Keyword Lock)
# ==========================================
def stage2_lexical_bm25(user_query, chunks, threshold=0.05): # TWEAKED: Much more inclusive
    print("\n--- 🛡️ Stage 2: BM25 Lexical Lock ---")
    if not chunks: return []
    tokenized_corpus = [c.lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(user_query.lower().split())
    
    survivors = []
    for i, score in enumerate(scores):
        if score > threshold:
            print(f"✅ Keyword Match ({score:.2f}) -> {chunks[i][:40]}...")
            survivors.append(chunks[i])
        else:
            print(f"❌ Keyword Missing ({score:.2f}) -> {chunks[i][:40]}...")
    return survivors

# ==========================================
# STAGE 3: CROSS-ENCODER (Logic Filter)
# ==========================================
def stage3_cross_encoder(user_query, chunks, threshold=-5.0): # TWEAKED: Allows non-Western phrasing
    print("\n--- 🛡️ Stage 3: Cross-Encoder AI Judge ---")
    if not chunks: return []
    pairs = [[user_query, chunk] for chunk in chunks]
    scores = encoder_model.predict(pairs)
    
    survivors = []
    for i, score in enumerate(scores):
        if score > threshold:
            print(f"✅ Logic Passed ({score:.2f}) -> {chunks[i][:40]}...")
            survivors.append(chunks[i])
        else:
            print(f"❌ Logic Failed ({score:.2f}) -> {chunks[i][:40]}...")
    return survivors

# ==========================================
# STAGE 4: MISTRAL (Binary Bouncer)
# ==========================================
def stage4_binary_bouncer(user_query, chunks):
    print("\n--- 🛡️ Stage 4: Mistral Binary Bouncer ---")
    if not chunks: return []
    survivors = []
    for chunk in chunks:
        # Prompt explicitly mentions BOTH medicine types
        prompt = f"""[INST] <<SYS>>
You are the A.W.A.R.E. Medical Validator. You recognize BOTH Western Clinical Medicine 
and Classical Ayurvedic Wisdom as valid medical information.
<</SYS>>

User Query: {user_query}
Context: {chunk}

Does this provide a safe, relevant answer or treatment (Allopathic OR Ayurvedic)? 
Answer ONLY 'YES' or 'NO'. [/INST]"""
        
        try:
            r = requests.post('http://localhost:11434/api/generate', 
                              json={'model': 'mistral', 'prompt': prompt, 'stream': False})
            answer = r.json()['response'].strip().upper()
            if "YES" in answer:
                print(f"✅ Mistral Approved -> {chunk[:40]}...")
                survivors.append(chunk)
            else:
                print(f"❌ Mistral Rejected -> {chunk[:40]}...")
        except:
            print("⚠️ Ollama Offline - Skipping Mistral Check")
            return chunks
    return survivors

# ==========================================
# THE FULL GAUNTLET
# ==========================================
if __name__ == "__main__":
    # Change query to help BM25 see "remedies"
    test_query = "What is the best way to treat a high fever and chills using medicine or natural remedies?"
    
    raw_chunks = [
        "A high fever accompanied by chills should be treated with rest, hydration, and paracetamol.", 
        "To build a strong foundation for your house, use concrete.", 
        "Chills occur when muscles rapidly expand and contract to generate heat.", 
        "Ayurveda suggests ginger tea and fasting (Langhana) for initial stages of Jwara (fever).", 
        "The patient felt warm after walking in the sun."
    ]
    
    print(f"\n🚀 STARTING HYBRID GAUNTLET FOR: '{test_query}'")
    
    s1 = stage1_cosine_verify(test_query, raw_chunks)
    s2 = stage2_lexical_bm25(test_query, s1)
    s3 = stage3_cross_encoder(test_query, s2)
    final_survivors = stage4_binary_bouncer(test_query, s3)

    print("\n" + "="*50)
    print("🏆 FINAL HYBRID SURVIVOR REPORT")
    print("="*50)
    if not final_survivors:
        print("🚨 NO CHUNKS SURVIVED THE GAUNTLET.")
    else:
        for idx, text in enumerate(final_survivors):
            print(f"\nGOLDEN CHUNK {idx+1}:")
            print(f"--- '{text}' ---")
    print("="*50)