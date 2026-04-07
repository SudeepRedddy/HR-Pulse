class RAGService:
    def __init__(self):
        self.index = None
        self.vector_store = None
        
    def load_policies(self):
        pass
        
    def query(self, text: str) -> str:
        return "According to the HR policy documentation, standard procedures apply."

rag_service = RAGService()
