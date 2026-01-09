import os
from pypdf import PdfReader

DOC_DIR = "/home/avacado/avatrada/avatrada-brain/knowledge/doctrines"

print(f"📂 Scanning {DOC_DIR} for PDFs...")

for filename in os.listdir(DOC_DIR):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(DOC_DIR, filename)
        md_filename = filename.replace(".pdf", ".md").replace(" ", "_").lower()
        md_path = os.path.join(DOC_DIR, md_filename)
        
        print(f"🔄 Converting: {filename} -> {md_filename}...")
        
        try:
            reader = PdfReader(pdf_path)
            text_content = f"# SOURCE: {filename}\n\n"
            
            for page in reader.pages:
                text_content += page.extract_text() + "\n\n"
            
            with open(md_path, "w") as f:
                f.write(text_content)
            
            # Optional: Delete the PDF after conversion to keep folder clean
            os.remove(pdf_path)
            print("✅ Conversion Complete. PDF removed.")
            
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")

print("✨ All operations finished.")
