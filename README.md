# AsyncTrader 
[Chinese](docs/zh/README_zh.md)

Running quantitative trading systems automatically with ChatGPT sounds pretty cool, doesn't it?

## Project Introduction
Building a complete quantitative trading system using AGI (Artificial General Intelligence) is still quite challenging. However, fortunately, there seems to be a feasible approach in teaching llm to use existing mature quantitative trading systems, and we are working on it.

With the control flow of langchain, we use ChatGPT to automatically write and backtest quantitative trading strategies, as well as provide documentation question-and-answer functionality. At present, a fairly comprehensive workflow has been implemented in the Freqtrade quantitative system. Additionally, it supports partial functionality of China's AkShare and Vnpy.

## Supplementary Information
**Model limitations**
1. The database used by ChatGPT is up to date as of September 12, 2021, which means that the Freqtrade strategies generated by ChatGPT are usually old versions (v2).
2. GPT-4 is smarter, capable of completing tasks well with very simple prompts, but it is too expensive. GPT-3.5 is cheaper, but it requires more time and effort in writing prompts. Pricing information: https://openai.com/pricing
3. On June 13, 2023, OpenAI improved the GPT model by adding a function calling feature. All models in this project must use the ...-0613 model.
4. The gpt-3.5-turbo-0613 and gpt-4-0613 models support a maximum of 4096 tokens, which means that if we use these models, the total length of our prompts and the strategy code generated by the model cannot exceed about 3000 words. If there is too much content, you can try using the gpt-3.5-turbo-16k-0613 and gpt-4-32k-0613 models. Reference: https://platform.openai.com/docs/models/gpt-3-5
5. ChatGPT is obviously more proficient in English language-related knowledge. Currently, the strategies we generate based on the Freqtrade system using gpt3.5 can run directly, while the strategies based on the vnpy system always have various minor errors (only the more expensive gpt4 model and more professional prompts can solve this problem).

**Function execution and documentation Q&A**
1. Function execution and documentation Q&A are different contents and require the execution of different programs. eg: start_ft_app.py, start_ft_docs.py
2. Document Q&A relies on the MD documents written by project developers, so the project must be cloned to the local machine.
3. When using AkShare for document Q&A, you must use the gpt-3.5-turbo-16k-0613 or gpt-4-32k-0613 model.

**Introduction to Different Systems**
- Freqtrade: A free open source cryptocurrency trading robot project that contains all the contents of a complete quantitative trading system.
- Vnpy: A free open source quantitative trading project in China, dedicated to providing a quantitative solution from trading API docking to automatic strategy trading.
- AkShare: Almost all financial trading data in mainland China needs to be purchased. AkShare is a simple alternative. AkShare uses an open source financial data interface library to collect data, without involving any personal privacy data and non-public data.

## Basic Environment Installation
1. Install miniconda/anaconda: https://docs.conda.io/en/latest/miniconda.html
2. It is recommended to create a Python virtual environment (optional)
```markdown
conda create -n env_trader python=3.10
```
3. Download the `AsyncTrader` project code locally 
```markdown
cd AsyncTrader/
pip install -r requirements.txt
```
4. Modify the `trading_system/base.py` file, add `OPENAI_API_KEY`, and select `gpt3.5/4`

## Select Project for Installation

### [Freqtrade](docs/freqtrade_system.md)

1. Clone the project locally: git clone https://github.com/freqtrade/freqtrade.git
2. Enter the project directory: cd \path\freqtrade 
3. Specify the content for installation
```markdown
pip install --find-links build_helpers\ TA-Lib -U
pip install -r requirements.txt
pip install -e .
pip install -r requirements-hyperopt.txt
```

Installation reference: https://www.freqtrade.io/en/stable/windows_installation/

### [AkShare](docs/akshare_system.md)

1. Clone the project locally: git clone https://github.com/akfamily/akshare.git
2. Specify the content for installation
```markdown
pip install akshare
```

Installation reference: https://akshare.akfamily.xyz/installation.html

### [Vnpy](docs/vnpy_system.md)

1. Clone the project locally: git clone https://github.com/vnpy/vnpy.git
2. Specify the content for installation
```markdown
pip install vnpy
pip install akshare
pip install vnpy_datamanager
pip install vnpy_rqdata
pip install vnpy_ctastrategy
pip install vnpy_sqlite
```
