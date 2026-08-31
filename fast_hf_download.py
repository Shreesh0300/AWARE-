from datasets import load_dataset
import sys

print("🚀 Initiating Hugging Face Streaming Bypass...")

# streaming=True completely skips the Arrow database building phase!
dataset = load_dataset("MedRAG/pubmed", split="train", streaming=True)

output_file = "HF_MEDICAL_DATA.txt"
print(f"📦 Streaming PubMed chunks directly to {output_file}...")

# Write the dataset directly to text for your pipeline
with open(output_file, 'w', encoding='utf-8') as f:
    for i, item in enumerate(dataset):
        # MedRAG is already cleaned for AI use
        title = item.get('title', 'Medical Text')
        content = item.get('content', '')
        
        f.write(f"\n\n--- {title} ---\n\n")
        f.write(f"{content}")
        
        # Fast progress tracker (We removed the total count since streaming is dynamic)
        if i % 1000 == 0:
            sys.stdout.write(f"\r✍️ Written {i} chunks directly to text...")
            sys.stdout.flush()

print(f"\n✅ Boom! Medical chunks unpacked. Zero Arrow bottlenecks.")   