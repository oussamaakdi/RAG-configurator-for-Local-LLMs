import os
import pandas as pd
import re
from chromadb.config import Settings
from chromadb import Client
from sentence_transformers import SentenceTransformer
import numpy as np

class ChromaRetriever:
    def __init__(self, embedding_model, chunks, top_k=2, collection_name="Collection"):

        self.embedding_model = embedding_model
        self.chunks = chunks
        self.top_k = top_k

        self.client = Client(Settings(allow_reset=True))
        for collection in self.client.list_collections():
            self.client.delete_collection(collection.name)
        self.collection = self.client.create_collection(collection_name)

        self._add_chunks_to_collection()

    def _add_chunks_to_collection(self):
    
        embeddings = self.embedding_model.encode(self.chunks, show_progress_bar=True)
        for idx, chunk in enumerate(self.chunks):
            self.collection.add(
                documents=[chunk],
                ids=[str(idx)],
                embeddings=[embeddings[idx].tolist()]
            )

    def query(self, query_text):
  
        query_embedding = self.embedding_model.encode(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=self.top_k
        )

        context_blocks = ''
        for document in results["documents"][0]:
            context_blocks += document + "\n"
        return context_blocks
