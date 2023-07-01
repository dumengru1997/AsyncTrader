import re

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from langchain.document_loaders import WebBaseLoader
from langchain.tools import Tool

from trading_system.base import llm_chatgpt


def web_strategy(query: str) -> str:
    """ Extract the strategy's trading logic from the web page through the url. """
    pattern = re.compile(r"https?://[^\s/$.?#].[^\s]*")
    urls = re.search(pattern, query)
    if urls:
        url = urls.group(0)
    else:
        return "Problem: There is no url in the content"

    loader = WebBaseLoader([url])
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    documents = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm_chatgpt, vectorstore.as_retriever(), memory=memory)

    query = "Summarize the trading strategy logic mentioned in the article, " \
            "if the article has no trading strategy related content, then reply 'Problem: no relevant information': "
    result = qa({"question": query})
    return result["answer"]


web_strategy_tool = Tool.from_function(
        func=web_strategy,
        name="extract_strategy",
        description="Extract the strategy's trading logic from the web page through the url."
    )


if __name__ == '__main__':
    ...
