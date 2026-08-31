import ollama
import chromadb
import numpy as np
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from tabulate import tabulate
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

print("🚨🚨🚨 A.W.A.R.E. SANDBOX v4.0: THE MATH BOUNCER ONLINE 🚨🚨🚨")

# --- INITIALIZE SECURITY ENGINES (Load once to save VRAM) ---
print("🚀 Loading Math Security Models into VRAM...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
encoder_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# =====================================================================
# 🛡️ THE SECURITY GAUNTLET (The Cliff Edge Algorithm)
# =====================================================================
def run_the_gauntlet(query, raw_chunks):
    print("\n[ 🧮 GAUNTLET: EXECUTING PURE MATH VERIFICATION... ]")
    if not raw_chunks: return [], "No context found."
    
    matrix = []

    # 1. Calculate the 3 Core Metrics
    q_emb = embed_model.encode([query])
    c_embs = embed_model.encode(raw_chunks)
    cosine_scores = cosine_similarity(q_emb, c_embs)[0]
    
    tokenized_query = query.lower().split()
    bm25 = BM25Okapi([c.lower().split() for c in raw_chunks])
    bm25_scores = bm25.get_scores(tokenized_query)
    
    cross_scores = encoder_model.predict([[query, c] for c in raw_chunks])

    # 2. Calculate Power Scores
    power_scores = []
    for i in range(len(raw_chunks)):
        s3_shifted = max(0.1, cross_scores[i] + 15) 
        s2_shifted = bm25_scores[i] + 1
        power = cosine_scores[i] * s2_shifted * s3_shifted
        power_scores.append(power)

    # 3. Detect the Cliff
    ranked_indices = sorted(range(len(power_scores)), key=lambda k: power_scores[k], reverse=True)
    cliff_index = len(ranked_indices) 
    max_drop_percentage = 0.0
    
    for rank in range(len(ranked_indices) - 1):
        current_idx = ranked_indices[rank]
        next_idx = ranked_indices[rank + 1]
        current_power = power_scores[current_idx]
        next_power = power_scores[next_idx]
        
        if current_power == 0: continue
            
        drop_percentage = (current_power - next_power) / current_power
        if drop_percentage > 0.20 and drop_percentage > max_drop_percentage:
            max_drop_percentage = drop_percentage
            cliff_index = rank + 1

    # 4. Execute the Cut & Build the Matrix (Original Order)
    golden_chunks = []
    
    # Secretly feed the Doctor the best chunks first
    for idx in ranked_indices[:cliff_index]:
        golden_chunks.append(raw_chunks[idx])

    # Build the visual Matrix in the ORIGINAL 1-10 order
    for i in range(len(raw_chunks)):
        power = power_scores[i]
        
        # Find where this chunk placed in the race
        actual_rank = ranked_indices.index(i) + 1
        
        # Check if its rank made it past the cliff
        if ranked_indices.index(i) < cliff_index:
            standing = f"🏆 Rank {actual_rank}"
            action = "✅ PASS"
        else:
            standing = f"💀 Rank {actual_rank}"
            action = "❌ DROP"
            
        matrix.append([
            f"Chunk {i + 1}",
            standing,
            f"{power:.1f}",
            f"{cosine_scores[i]:.2f}",
            f"{bm25_scores[i]:.2f}",
            f"{cross_scores[i]:.2f}",
            action
        ])

    # Print Audit Matrix
    print("\n" + "="*85)
    print("🏥 A.W.A.R.E. SECURITY AUDIT MATRIX")
    print("="*85)
    headers = ["Source", "Standing", "Power", "S1:Cosine", "S2:BM25", "S3:Cross", "Action"]
    print(tabulate(matrix, headers=headers, tablefmt="grid"))
    print("="*85)
    verified_context = "\n\n".join(golden_chunks) if golden_chunks else "No verified medical context found."
    return golden_chunks, verified_context

# =====================================================================
# 1. TRIAGE ROUTER (The Gatekeeper)
# =====================================================================
def triage_router(patient_query):
    print("\n[ 🏥 FRONT DESK TRIAGE... ]")
    clean_query = patient_query.lower().strip()
    
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good evening', 'thanks', 'ok']
    if clean_query in greetings or any(clean_query.startswith(g + " ") for g in greetings):
        return "GREETING"
        
    math_triggers = ['+', '*', '/', '=', 'math', 'calculate', 'divisor', 'multiply', 'equation']
    if any(trigger in clean_query for trigger in math_triggers):
        return "REJECT"

    system_instruction = "Extract core symptom in 1-3 words. No math. If nonsense, output: REJECT."
    
    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction},
        {'role': 'user', 'content': f'Extract from: "{patient_query}"'}
    ], options={'temperature': 0.0, 'repeat_penalty': 1.2})
    
    result = response['message']['content'].strip().upper()
    return "REJECT" if "REJECT" in result else result

# =====================================================================
# 2. DYNAMIC SPECIALIST (The Interviewer)
# =====================================================================
# =====================================================================
# 2. DYNAMIC SPECIALIST (The Interviewer)
# =====================================================================
def dynamic_specialist(user_query, core_symptom):
    print(f"\n[ 🧬 DYNAMIC SPECIALIST: {core_symptom} ]")
    
    try:
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        chroma_client = chromadb.PersistentClient(path="./aware_chroma_db") 
        collection = chroma_client.get_collection(name="aware_medical_collection", embedding_function=sentence_transformer_ef)
        
        # Pull 5 West + 5 Ayur
        
        res_ayur = collection.query(query_texts=[f"{core_symptom} physical signs ayurveda"], n_results=10)
        raw_retrieved_chunks = res_ayur['documents'][0]

        # --- THE PROPER X-RAY PREVIEW ---
        print("\n[ 📥 X-RAY PREVIEW ]:")
        for i, c in enumerate(raw_retrieved_chunks):
            print(f"  [{i+1}] {c[:250].replace('/n', ' ')}...")
        print("-" * 75)

        # --- THE MATH GAUNTLET INTERCEPTION ---
        verified_chunks, medical_context = run_the_gauntlet(user_query, raw_retrieved_chunks)
            
    except Exception as e:
        medical_context = f"Error: {e}"
        print(f"⚠️ DB Error: {e}")

    # --- THE MUZZLE (Notice this is outside the try/except block) ---
    system_instruction = f"""
    You are a professional, empathetic triage doctor for Project A.W.A.R.E. 
    You are currently interviewing a patient to determine if they are suffering from: {core_symptom}.

    STRICT CONTEXT RULES:
    1. RELEVANCY GUARD: Use the provided medical context ONLY if it directly discusses {core_symptom}. 
    2. DISCARD IRRELEVANT DATA: If the retrieved context mentions other conditions, ignore them completely.
    3. NO JARGON: Do not use complex medical terms. Use natural, 5th-grade level English.

    INTERVIEW RULES (CRITICAL):
    1. Ask EXACTLY 3 questions. Number them 1, 2, and 3.
    2. Speak directly to the user (use "you" and "your").
    3. NEVER ask the patient to define medical terms, explain causes, or list treatments. (e.g., BAD: "What is otitis media?")
    4. ONLY ask about what the patient physically feels right now based on the context. (e.g., GOOD: "Are you feeling a deep ache inside your ear, or perhaps a fever?")
    5. Formulate your own conversational questions. DO NOT copy phrases or hints from the source text.
    6. DO NOT give advice, suggest a diagnosis, or provide multiple-choice options yet.

    EXAMPLE FORMAT:
    "I'm sorry you're feeling unwell. To help me get a better picture, could you answer these three questions?
    1. [Ask about the timing or duration of their discomfort]
    2. [Ask if they are experiencing a specific physical symptom found in the {core_symptom} context]
    3. [Ask if they have noticed any specific triggers or related issues found in the {core_symptom} context]"

    ### EXAMPLES OF GOOD QUESTIONS:
    - "Is the popping sound accompanied by a grinding sensation?"
    - "Does the swelling get worse at a specific time of day?"
    - "Does the area feel warm or look red to the eye?"


    """
    
    user_data = f"--- REFERENCE MATERIAL ---\n{medical_context}\n\nPatient's Complaint: {user_query}"

    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction.strip()},
        {'role': 'user', 'content': user_data}
    ], options={
        'temperature': 0.0,
        'num_predict': 100, # Stops the model from rambling too long
        'top_k': 1,         # Forces it to pick ONLY the top most likely word
        'top_p': 0.0        # Further reduces randomness
    })
    return response['message']['content'], medical_context

# =====================================================================
# 3. CMO CRITIC (Safety Check)
# =====================================================================
def critic_agent(user_query, draft):
    print("\n[ 🛡️ CMO CRITIC AUDITING... ]")
    system_instruction = """
    You are a text formatter. 
    1. Output ONLY 3 numbered questions. 
    2. If the drafted text contains treatments instead of questions, REWRITE it into 3 diagnostic questions.
    3. Add ER warnings if necessary.
    """
    user_data = f"User Query: {user_query}\nDrafted Questions:\n{draft}"
    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction.strip()},
        {'role': 'user', 'content': user_data}
    ], options={'temperature': 0.0})
    return response['message']['content']

# =====================================================================
# 4. DIAGNOSTIC SUMMARY (Hybrid Assessment)
# =====================================================================
def diagnostic_summary_agent(core_symptom, patient_answers, medical_context):
    print("\n[ 🧠 ANALYZING FINAL HYBRID ASSESSMENT... ]")
    qa_text = "\n".join(patient_answers)
    
    system_instruction = """
    Senior Diagnostician. 4 sections: 1. Summary, 2. Treatment (Hybrid), 3. Recommendations, 4. Disclaimer.
    CRITICAL RULE: If the reference material states 'No verified medical context found', you MUST state that you cannot provide a diagnosis or treatment plan. DO NOT invent herbs or medicines.
    """
    user_data = f"Context: {medical_context}\nSymptom: {core_symptom}\nPatient Answers: {qa_text}"
    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction.strip()},
        {'role': 'user', 'content': user_data}
    ], options={'temperature': 0.3, 'repeat_penalty': 1.4})
    return response['message']['content']

# =====================================================================
# MAIN LOOP
# =====================================================================
if __name__ == "__main__":
    print("==========================================")
    print("🏥 A.W.A.R.E. SANDBOX v4.0 (Math Bouncer)")
    print("==========================================")
    
    while True:
        test_query = input("\nUser Patient: ")
        if test_query.lower() in ['quit', 'exit']: break
            
        triage_result = triage_router(test_query)
        
        if triage_result == "GREETING":
            print("\n🏥 A.W.A.R.E: Hello! How can I help today?")
            continue
        elif triage_result == "REJECT":
            print("\n🏥 A.W.A.R.E: I only assist with medical symptoms.")
            continue
            
        draft, used_context = dynamic_specialist(test_query, triage_result)
        final_questions = critic_agent(test_query, draft)
        
        print("\n==========================================")
        print("🏥 A.W.A.R.E. DOCTOR CONSULTATION:")
        print("==========================================")
        
        lines = final_questions.split('\n')
        patient_answers = []
        for line in lines:
            line = line.strip()
            if not line: continue
            if any(char.isdigit() for char in line[:2]):
                ans = input(f"\n🩺 {line}\nPatient Answer: ")
                patient_answers.append(f"Q: {line}\nA: {ans}")
            else:
                print(f"\n⚠️ {line}")
                
        if patient_answers:
            final_assessment = diagnostic_summary_agent(triage_result, patient_answers, used_context)
            print("\n==========================================")
            print("🏥 A.W.A.R.E. FINAL HYBRID ASSESSMENT:")
            print("==========================================")
            print(final_assessment)
            print("\n==========================================\n")