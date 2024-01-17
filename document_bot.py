from time import sleep
from uuid import uuid1
from langchain.llms import GPT4All
from langchain.chains import ConversationalRetrievalChain
from indexer import index_documents, load_index

class DocumentBot:
    def __init__(self, model, index):
        self.llm = GPT4All(model=model)
        self.index = load_index(index)
        self.chat_history = []
        self.responses = {}

    def ask(self, text, index):
        if index:
            self.index = load_index('./indexes/' + index)
            
        self.qa = ConversationalRetrievalChain.from_llm(self.llm, self.index.as_retriever(), max_tokens_limit=400)
        result = self.qa({"question": text, "chat_history": self.chat_history})
        return result['answer']

    