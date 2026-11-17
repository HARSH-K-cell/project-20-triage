import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class TicketDeduplicator:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.index = faiss.IndexFlatIP(self.dimension)
        self.ticket_ids = []
        self.ticket_texts = []

    def check_and_add(self, ticket_id: int, text: str):
        embedding = self.model.encode([text]).astype('float32')
        faiss.normalize_L2(embedding)

        if self.index.ntotal > 0:
            distances, indices = self.index.search(embedding, k=1)
            highest_similarity = float(distances[0][0])
            matched_idx = int(indices[0][0])

            if highest_similarity >= self.threshold:
                matched_ticket_id = self.ticket_ids[matched_idx]
                matched_text = self.ticket_texts[matched_idx]
                return {
                    "is_duplicate": True,
                    "similarity": round(highest_similarity * 100, 2),
                    "matched_ticket_id": matched_ticket_id,
                    "matched_text": matched_text
                }

        self.index.add(embedding)
        self.ticket_ids.append(ticket_id)
        self.ticket_texts.append(text)

        return {
            "is_duplicate": False,
            "similarity": 0.0,
            "matched_ticket_id": None,
            "matched_text": None
        }

deduplicator = TicketDeduplicator(threshold=0.85)
