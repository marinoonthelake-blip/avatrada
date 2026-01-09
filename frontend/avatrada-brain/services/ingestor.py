import os
from pypdf import PdfReader

class KnowledgeIngestor:
    def __init__(self):
        self.root = "/home/avacado/avatrada/avatrada-brain/knowledge"
        
    def convert_pdfs(self):
        print(f"🔍 Scanning {self.root} for PDF Doctrines...")
        converted = 0
        
        for root, dirs, files in os.walk(self.root):
            for f in files:
                if f.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, f)
                    md_path = os.path.splitext(pdf_path)[0] + ".md"
                    
                    # Skip if already converted
                    if os.path.exists(md_path):
                        continue
                        
                    try:
                        print(f"📄 Processing: {f}...")
                        reader = PdfReader(pdf_path)
                        text = f"# SOURCE PDF: {f}\n\n"
                        for page in reader.pages:
                            text += page.extract_text() + "\n\n"
                            
                        with open(md_path, "w", encoding="utf-8") as md_file:
                            md_file.write(text)
                            
                        print(f"✅ Created: {os.path.basename(md_path)}")
                        converted += 1
                    except Exception as e:
                        print(f"❌ Failed to convert {f}: {e}")
                        
        if converted == 0:
            print("✨ All PDFs are already ingested.")
        else:
            print(f"🚀 Successfully ingested {converted} new documents.")

if __name__ == "__main__":
    KnowledgeIngestor().convert_pdfs()
