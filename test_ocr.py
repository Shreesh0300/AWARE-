import os
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path

# 1. YOUR TESSERACT PATH 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. YOUR POPPLER PATH 
MY_POPPLER_PATH = r'C:\IMP STUFF\STUDY\4TH SEM\CODING\PYTHON\TESSERACT\Release-25.12.0-0\poppler-25.12.0\Library\bin' 

def process_pdf_page_by_page(pdf_path, output_filename):
    print(f"\n>>> Starting extraction for: {pdf_path}")
    
    try:
        # Get total page count instantly (doesn't load the whole PDF)
        info = pdfinfo_from_path(pdf_path, poppler_path=MY_POPPLER_PATH)
        total_pages = info["Pages"]
        print(f"Total pages: {total_pages}. Starting scan...")

        with open(output_filename, "w", encoding="utf-8") as file:
            for i in range(1, total_pages + 1):
                # Print progress on the exact same line so it doesn't spam your screen
                print(f"Scanning page {i} of {total_pages}...", end="\r") 
                
                # Convert and read ONLY this specific page
                page_image = convert_from_path(pdf_path, first_page=i, last_page=i, poppler_path=MY_POPPLER_PATH)[0]
                text = pytesseract.image_to_string(page_image)
                
                file.write(f"\n----- PAGE {i} -----\n{text.strip()}\n")
                
        print(f"\n✅ Success! Saved all text to '{output_filename}'")
        
    except Exception as e:
        print(f"\n❌ Error processing {pdf_path}:\n{e}")

# --- BATCH PROCESSING LOGIC ---
print("Scanning folder for textbooks...")
pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
print(f"Found {len(pdf_files)} PDF(s) to process! Let's get to work.\n")

for pdf_file in pdf_files:
    txt_file = pdf_file.replace('.pdf', '.txt').replace('.PDF', '.txt')
    
    # Check if we already processed this textbook
    if os.path.exists(txt_file):
        print(f"⏭️ Skipping '{pdf_file}' (already extracted)")
    else:
        process_pdf_page_by_page(pdf_file, txt_file)    