import re
from typing import List

class Chunker:
    """
    Responsible for splitting text into manageable chunks for embedding.
    Uses a recursive character split approach (simplified) or paragraph-based split.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits text into chunks. 
        Strategy:
        1. Split by double newlines (paragraphs).
        2. If a paragraph is too long, split by sentence endings.
        3. If still too long, hard truncate (rare for policy docs).
        """
        text = re.sub(r'\n{3,}', '\n\n', text)
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                if len(para) > self.chunk_size:
                    sub_chunks = self._split_large_paragraph(para)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = para
                    
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def _split_large_paragraph(self, text: str) -> List[str]:
        """Simple sentence splitter for large blocks."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
