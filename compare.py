import requests
from tabulate import tabulate
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

# --- INITIALIZE MODELS ---
print("🚀 Loading Security Models into VRAM...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
encoder_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def run_comparison(query, chunks):
    matrix = []

    # 1. Prepare Stage 2 (BM25)
    tokenized_query = query.lower().split()
    bm25 = BM25Okapi([c.lower().split() for c in chunks])
    bm25_scores = bm25.get_scores(tokenized_query)

    # 2. Prepare Stage 1 (Cosine)
    q_emb = embed_model.encode([query])
    c_embs = embed_model.encode(chunks)
    cosine_scores = cosine_similarity(q_emb, c_embs)[0]

    # 3. Prepare Stage 3 (Cross-Encoder)
    cross_scores = encoder_model.predict([[query, c] for c in chunks])


    # 4. Stage 4:The Binary Bouncer (Mistral)

    print("🛡️ Querying Mistral for Final Decisions...")
    
    for i in range(len(chunks)):
        chunk = chunks[i]

        if cosine_scores[i] < 0.20 or (bm25_scores[i] == 0 and cross_scores[i] < -7.0):
            decision = "0 "
        
        else:
            
            decision = "0"
            prompt = f"""[INST] <<SYS>>
            You are the A.W.A.R.E. Hybrid Expert. Verify if this chunk is relevant for: {query}.
            Recognize both Allopathic and Ayurvedic data as valid.
            
            <</SYS>>
            Context: {chunk}
            Does this context provide actionable treatment advice or specific medical information for the query? If it is just a vague observation or unrelated story, answer NO. Answer ONLY 'YES' or 'NO'[/INST]"""
            
            try:
                r = requests.post('http://localhost:11434/api/generate', 
                                json={'model': 'mistral', 'prompt': prompt, 'stream': False},
                                timeout=10)
                if "YES" in r.json()['response'].upper():
                    decision = " 1"
            except:
                decision = "⚠️ ERROR"

        # Add row to matrix
        matrix.append([
            f"Chunk {i+1}",
            f"{cosine_scores[i]:.2f}",
            f"{bm25_scores[i]:.2f}",
            f"{cross_scores[i]:.2f}",
            decision
        ])

    return matrix

if __name__ == "__main__":
    user_query = "Best treatment for high fever and chills using medicine or natural remedies?"
    
    test_chunks = [
        "A high fever with chills is treated with paracetamol and rest.", 
        "Ayurveda suggests ginger tea and fasting (Langhana) for fever (Jwara).", 
        "Chills are a biological reaction to raising body temperature.", 
        "To build a strong foundation for your house, use high-grade concrete.", 
        "The patient felt warm after walking in the sun." 
    ]

    print(f"\n🔎 BENCHMARKING QUERY: '{user_query}'")
    results = run_comparison(user_query, test_chunks)

    print("\n" + "="*85)
    print("🏥 A.W.A.R.E. SECURITY AUDIT MATRIX")
    print("="*85)
    headers = ["Source", "S1: Cosine", "S2: BM25", "S3: Cross", "S4: Binary Bouncer."]
    print(tabulate(results, headers=headers, tablefmt="grid"))
    print("="*85)