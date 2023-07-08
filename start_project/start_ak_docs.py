import os
from trading_system.retrieval_qa import retrieval


if __name__ == '__main__':
    # 1. 输入文档路径
    ak_docs_path = os.path.abspath("../akshare/docs/data/futures")
    # 2. 进行文档问答
    retrieval(ak_docs_path)
