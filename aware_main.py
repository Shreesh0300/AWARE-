import ollama
import chromadb
from chromadb.utils import embedding_functions

print("🚨🚨🚨 A.W.A.R.E. v3.0: THE HYBRID BRAIN IS ONLINE 🚨🚨🚨")

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
# 2. DYNAMIC SPECIALIST (Search, Verifier, and Interviewer)
# =====================================================================
def dynamic_specialist(user_query, core_symptom):
    print(f"\n[ 🧬 DYNAMIC SPECIALIST: {core_symptom} ]")
    
    try:
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        chroma_client = chromadb.PersistentClient(path="./aware_chroma_db")
        collection = chroma_client.get_collection(name="aware_medical_collection", embedding_function=sentence_transformer_ef)
        
        res_west = collection.query(query_texts=[core_symptom], n_results=3)
        # --- DEBUGGING BLOCK: THE INTERCEPTION ---
        print("\n🚨 AUDIT: WHAT DID CHROMADB ACTUALLY FIND? 🚨")
        if 'documents' in res_west and len(res_west['documents'][0]) > 0:
            for i, chunk in enumerate(res_west['documents'][0]):
                print(f"\n--- Western Chunk {i+1} ---")
                print(f"{chunk}") 
        else:
            print("❌ ChromaDB returned absolutely nothing for Western.")
            print("🚨 END AUDIT 🚨\n")
# -----------------------------------------
        res_ayur = collection.query(query_texts=[f"{core_symptom} physical signs"], n_results=2)
        if 'documents' in res_ayur and len(res_ayur['documents'][0]) > 0:
            for i, chunk in enumerate(res_ayur['documents'][0]):
                print(f"\n--- Ayurvedic Chunk {i+1} ---")
                print(f"{chunk}")
            print("❌ ChromaDB returned absolutely nothing for Ayurveda.")
        

        
        all_docs = res_west['documents'][0] + res_ayur['documents'][0]
        all_chunks = res_west['documents'][0] + res_ayur['documents'][0]
        all_dist = res_west['distances'][0] + res_ayur['distances'][0]
        
        verified_chunks = []
        for i in range(len(all_docs)):
            
            if all_dist[i] < 2.0: 
                verified_chunks.append(all_docs[i])
                print(f"✅ Context Verified (Distance: {all_dist[i]:.2f})")

        medical_context = "\n\n".join(verified_chunks) if verified_chunks else "General knowledge."
            
    except Exception as e:
        medical_context = f"Error: {e}"
        print("⚠️ DB Error")

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
    """
    user_data = f"""
[SYSTEM NOTE: The following is BACKGROUND REFERENCE MATERIAL. Do NOT quiz the patient on this.]
--- START REFERENCE MATERIAL ---
{medical_context}
--- END REFERENCE MATERIAL ---

Patient's Current Complaint: "{user_query}"

DOCTOR'S TASK: You are sitting in the exam room with this patient right now. 
Based on their complaint and the reference material above, ask your 3 conversational diagnostic questions. 
CRITICAL REMINDER: Do NOT ask for definitions. Do NOT use medical jargon. Talk to them like a normal human.
"""

    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction.strip()},
        {'role': 'user', 'content': user_data}
    ], options={'temperature': 0.0, 'repeat_penalty': 1.5})
    
    return response['message']['content'], medical_context
# =====================================================================
# 3. CMO CRITIC (Safety Check)
# =====================================================================
def critic_agent(user_query, draft):
    print("\n[ 🛡️ CMO CRITIC AUDITING... ]")
    
    system_instruction = """
    You are a strict text formatter. Review the drafted questions and output ONLY the final text.
    
    RULES:
    1. ONLY output the ER warning if the user EXPLICITLY mentions "chest pain", "heart attack", "stroke", or "can't breathe". General aches or chills DO NOT qualify. If triggered, prepend: "⚠️ ER WARNING: Seek immediate emergency care.\n"
    2. Output the 3 numbered questions exactly as provided.
    3. DO NOT output any introductory filler like "Here are the questions".
    """
    
    user_data = f"User Query: {user_query}\nDrafted Questions:\n{draft}\n\nOutput ONLY the final formatted list now."

    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction.strip()},
        {'role': 'user', 'content': user_data}
    ], options={'temperature': 0.0})
    
    return response['message']['content']
# =====================================================================
# 4. DIAGNOSTIC SUMMARY (Hybrid Assessment & Medication)
# =====================================================================
def diagnostic_summary_agent(core_symptom, patient_answers, medical_context):
    print("\n[ 🧠 ANALYZING FINAL HYBRID ASSESSMENT... ]")
    qa_text = "\n".join(patient_answers)
    
    # THE MEDICATION JAILBREAK PROMPT
    system_instruction = """
    You are the Senior Diagnostician. Provide a hybrid assessment (Western + Ayurveda).
    
    REQUIRED SECTIONS:
    1. Summary: Explain the likely Western condition (e.g. GERD) and Ayurvedic state (e.g. Pitta).
    2. Treatment (Educational): List common medications (e.g. Antacids, PPIs) AND Ayurvedic remedies (e.g. Avipattikar Churna, Cooling herbs).
    3. Recommendations: Lifestyle changes based on both systems.
    4. Disclaimer: You are an AI, not a doctor.
    """
    
    user_data = f"""
[SYSTEM NOTE: The following is BACKGROUND REFERENCE MATERIAL. Do NOT just summarize this text.]
--- START REFERENCE MATERIAL ---
{medical_context}
--- END REFERENCE MATERIAL ---

PATIENT DETAILS:
Primary Symptom: {core_symptom}

INTERVIEW LOGS (Patient's Current State):
{qa_text}

DOCTOR'S TASK: Based on the Patient Details and Interview Logs above, cross-referenced with the Reference Material, generate the Final Hybrid Assessment. 
CRITICAL REMINDER: You MUST strictly follow the exact 4-part structure (1. Summary, 2. Treatment, 3. Recommendations, 4. Disclaimer) defined in your system instructions. Do NOT write a book report.
"""

    response = ollama.chat(model='mistral', messages=[
        {'role': 'system', 'content': system_instruction.strip()},
        {'role': 'user', 'content': user_data}
    ], options={'temperature': 0.3, 'repeat_penalty': 1.4}) # High penalty to KILL terminal stuttering
    
    return response['message']['content']

# =====================================================================
# MAIN LOOP
# =====================================================================
if __name__ == "__main__":
    print("==========================================")
    print("🏥 A.W.A.R.E. v3.0 (Duct-Tape & Glory) Online")
    print("==========================================")
    
    while True:
        test_query = input("\nUser Patient: ")
        if test_query.lower() in ['quit', 'exit']: break
            
        triage_result = triage_router(test_query)
        
        if triage_result == "GREETING":
            print("\n🏥 A.W.A.R.E: Hello! How can I help you today?")
            continue
        elif triage_result == "REJECT":
            print("\n🏥 A.W.A.R.E: I only assist with medical symptoms.")
            continue
            
        print(f"Detected Medical Focus: [ {triage_result} ]")
        
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
            print("\n⚠️ DISCLAIMER: A.W.A.R.E. is an AI educational tool, not a licensed doctor.")
            print("Always consult a real healthcare professional for medical advice and emergencies.")
            print("==========================================\n")