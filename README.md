# Project A.W.A.R.E. 🏥🧠 
**The Hybrid Medical AI (Western + Ayurveda) & RAG Sandbox**

Project A.W.A.R.E. (Advanced Western & Ayurvedic Reasoning Engine) is an autonomous, multi-agent AI diagnostic system that integrates a powerful Retrieval-Augmented Generation (RAG) pipeline to consult both Western medical textbooks and Ayurvedic knowledge bases.

This project is built completely locally using **Ollama** (for local LLMs), **ChromaDB** (for vector storage), and a custom **tri-metric RAG security gauntlet** to prevent AI hallucinations.

---

## 🌟 Core Features

- **Hybrid Medical Knowledge:** Cross-references queries against both Western medical documents and Ayurvedic texts.
- **Multi-Agent Architecture:** Utilizes specialized LLM agents (Triage Router, Dynamic Specialist, CMO Critic, Senior Diagnostician) to handle different stages of the medical interview.
- **Advanced RAG "Math Bouncer":** Employs a custom "Cliff Edge" algorithm combining **Cosine Similarity**, **BM25 Lexical Search**, and a **Cross-Encoder** to mathematically verify and rank retrieved document chunks before feeding them to the AI.
- **Automated Data Pipeline:** Includes an end-to-end pipeline to OCR medical textbook PDFs, clean the text, chunk it intelligently, and vectorize it.
- **Strict Safety Rails:** Built-in safeguards reject non-medical queries (like math) and inject critical ER warnings for life-threatening symptoms.

---

## 🏗️ System Architecture

The project is divided into two distinct pipelines: **Data Ingestion** and **AI Inference**.

### 1. Data Ingestion Pipeline (The Knowledge Builder)
Before the AI can answer questions, it must learn from textbooks.

1. **OCR Extraction (`test_ocr.py`)**: Uses `pytesseract` and `poppler` to scan large medical PDF textbooks page-by-page and convert them into raw text files.
2. **Merging (`combine.py`)**: Stitches all the individual OCR text files into a single master file (`ALL IN ONE.txt`).
3. **Data Cleaning (`cleaning.py`)**: Strips out page numbers, headers, textbook dividers, and weird OCR artifacts to create a pristine `CLEANED_ALL_IN_ONE.txt`.
4. **Smart Chunking (`database.py`)**: Slices the cleaned text into 500-word chunks (with a 100-word overlap to preserve sentence context) and stores them in a local SQLite database (`AWARE_knowledge_base.db`).
5. **Vectorization (`vector_db.py`)**: Reads the chunks from SQLite, converts them into high-dimensional math vectors using `sentence-transformers` (`all-MiniLM-L6-v2`), and injects them into **ChromaDB** (`aware_chroma_db`).

### 2. AI Inference Pipeline (The Doctor's Office)
When a user asks a question, the system runs a gauntlet of scripts:

1. **Front Desk Triage (`aware_main.py` / `sandbox.py`)**:
   - An LLM analyzes the patient's query.
   - Extracts the core 1-3 word symptom.
   - Rejects malicious queries (like math problems or coding questions).
2. **The Math Bouncer / RAG Retrieval (`sandbox.py`)**:
   - Queries ChromaDB for the core symptom.
   - Runs retrieved chunks through the **Security Gauntlet**.
   - Calculates a combined "Power Score" based on:
     - `S1: Cosine Similarity` (Semantic meaning)
     - `S2: BM25` (Exact keyword match)
     - `S3: Cross-Encoder` (Deep contextual relevance)
   - Detects the "Cliff Edge" (a >20% drop in relevance score) and aggressively drops low-quality chunks to prevent hallucination.
3. **Dynamic Specialist Interview**:
   - The LLM reads the mathematically verified context.
   - Formulates exactly 3 natural, jargon-free diagnostic questions based *only* on the provided context.
4. **CMO Critic**:
   - Audits the LLM's drafted questions.
   - Forces formatting compliance.
   - Injects `⚠️ ER WARNING` if dangerous keywords (stroke, heart attack, chest pain) are detected.
5. **Senior Diagnostician**:
   - Takes the patient's answers to the 3 questions and the verified context.
   - Outputs a highly structured 4-part assessment:
     1. **Summary** (Western + Ayurvedic states)
     2. **Treatment** (Meds + Herbs)
     3. **Recommendations** (Lifestyle)
     4. **Disclaimer**

---

## 📂 Key Files & Modules Overview

| File | Purpose |
|------|---------|
| `aware_main.py` | The main execution loop of the A.W.A.R.E. AI system. Handles the conversational flow, prompting, and agent chaining. |
| `sandbox.py` | The v4.0 upgrade featuring the "Math Bouncer". Contains the advanced RAG ranking algorithm (BM25 + Cross-Encoder) and visual audit matrices. |
| `test_ocr.py` | Converts PDFs to Text. Requires Tesseract-OCR and Poppler binaries installed on the host machine. |
| `combine.py` | Utility to merge multiple `.txt` outputs into one mega-file. |
| `cleaning.py` | Regex-heavy script to sanitize raw OCR text for optimal LLM ingestion. |
| `database.py` | Handles the SQLite logic and the smart sliding-window word chunking algorithm. |
| `vector_db.py` | Handles embedding generation and ChromaDB collection management. |
| `compare.py`, `cosine.py`, `bm25.py`, `ce.py` | Sandbox testing scripts used to isolate and test the individual mathematical scoring mechanisms before they were merged into `sandbox.py`. |

---

## 🛠️ Prerequisites & Dependencies

To run this project, you need a powerful local environment capable of running LLMs and embedding models.

### System Requirements:
- **Ollama**: Must be installed and running locally.
- **LLM Model**: `mistral` (Run `ollama run mistral` before starting).
- **Tesseract OCR**: Installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- **Poppler**: Required for PDF to image conversion.

### Python Packages (`requirements.txt` equivalent):
```bash
pip install ollama chromadb numpy scikit-learn sentence-transformers rank_bm25 tabulate pytesseract pdf2image
```

---

## 🚀 How to Run

1. **Build the Brain** (Only if you are adding new textbooks):
   - Place PDFs in the root directory.
   - Run `python test_ocr.py` -> `python combine.py` -> `python cleaning.py`.
   - Run `python database.py` (Creates SQLite DB).
   - Run `python vector_db.py` (Builds ChromaDB vector space).

2. **Start the Doctor**:
   - To run the standard version: `python aware_main.py`
   - To run the advanced version with the RAG Math Gauntlet and visual audit matrices: `python sandbox.py`

---
*Disclaimer: Project A.W.A.R.E. is an experimental AI educational tool. It is not a licensed medical professional and should not be used for actual medical diagnosis or treatment.*
