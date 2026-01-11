class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str):
        if not text or not isinstance(text, str):
            return []

        chunks = []
        text_length = len(text)
        start = 0

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            # ✅ GUARANTEED FORWARD PROGRESS
            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = end

            start = next_start

        return chunks
