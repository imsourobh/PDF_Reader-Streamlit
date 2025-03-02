from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA

class QABot:
    def __init__(self, vector_db, model_name="qwen2.5:7b", temperature=0.6):
        self.llm = ChatOllama(model=model_name, temperature=temperature)
        self.retriever = vector_db.as_retriever()
        self.bot = RetrievalQA.from_chain_type(llm=self.llm, retriever=self.retriever)

    def ask(self, question):
        """Ask a question to the bot"""
        return self.bot.invoke(question)