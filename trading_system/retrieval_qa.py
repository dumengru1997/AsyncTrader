from trading_system.base import llm_chatgpt

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import DirectoryLoader


def retrieval(docs_path: str):
    loader = DirectoryLoader(docs_path, glob="**/*.md")
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=100)
    documents = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)

    from langchain.memory import ConversationBufferMemory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm_chatgpt, vectorstore.as_retriever(), memory=memory)

    while True:
        query = input("question(Press `q` to exit): ")
        if query.lower() == "q":
            print("Exit. ")
            break

        result = qa({"question": query})
        print(result["answer"])
