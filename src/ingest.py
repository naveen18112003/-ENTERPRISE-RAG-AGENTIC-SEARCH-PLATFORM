import os
import glob
from typing import List

from src.chunker import Chunker
from src.rag_engine import RagEngine

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
    elif ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
    
    return text

def ingest_data(data_dir: str = "data"):
    print("Initializing Ingestion...")
    chunker = Chunker(chunk_size=600, chunk_overlap=100)
    rag = RagEngine()
    
    # Check if DB already populated (simple check)
    if rag.count() > 0:
        print(f"Database already contains {rag.count()} entries. Note: appending specific new files not supported in this mini-version, clearing DB recommended if re-ingesting.")
        # We proceed to ingest anyway for this demo, usually you'd check file hashes.
    
    # Support multiple extensions
    extensions = ["*.txt", "*.pdf"]
    file_paths = []
    for ext in extensions:
        file_paths.extend(glob.glob(os.path.join(data_dir, ext)))
    
    all_chunks = []
    all_metadatas = []
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        print(f"Processing {filename}...")
        
        text = extract_text(file_path)
        if not text:
            print(f"Skipping {filename} (no text extracted).")
            continue
            
        chunks = chunker.split_text(text)
        
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": filename})
            
    if all_chunks:
        print(f"Ingesting {len(all_chunks)} chunks...")
        rag.add_documents(all_chunks, all_metadatas)
        print("Ingestion Complete.")
    else:
        print("No data found to ingest.")

if __name__ == "__main__":
    ingest_data()
