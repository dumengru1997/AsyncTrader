import os
os.environ["OPENAI_API_KEY"] = ""

import langchain
# langchain.debug = True

from langchain.cache import SQLiteCache
# langchain.llm_cache = SQLiteCache(database_path=".langchain_cache.db")

from langchain.chat_models import ChatOpenAI


llm_chatgpt = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
# llm_chatgpt = ChatOpenAI(temperature=0, model="gpt-4-0613")

