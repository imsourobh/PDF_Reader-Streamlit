from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

class VectorDBManager:
    def __init__(self, model_name="qwen2.5:7b"):
        self.embedding_model = OllamaEmbeddings(model=model_name)
        self.default_save_path = "a_different_story"

    def create_vector_db(self, chunks, save_path=None):
        """Create and save a new vector database with an optional custom path"""
        vector_db = FAISS.from_texts(chunks, self.embedding_model)
        save_path = save_path or self.default_save_path
        vector_db.save_local(save_path)
        return vector_db

    def load_vector_db(self, path):
        """Load an existing vector database"""
        return FAISS.load_local(
            path,
            embeddings=self.embedding_model,
            allow_dangerous_deserialization=True
        )