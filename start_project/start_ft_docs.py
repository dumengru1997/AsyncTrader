import os
import freqtrade
from trading_system.retrieval_qa import retrieval


if __name__ == '__main__':
    freqtrade_docs_path = os.path.join(os.path.dirname(os.path.dirname(freqtrade.__file__)), "docs")
    retrieval(freqtrade_docs_path)
