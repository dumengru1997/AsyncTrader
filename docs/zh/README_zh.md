# AsyncTrader
[English](../../README.md)

用ChatGPT自动运行量化交易系统, 听起来很有趣.

## 项目介绍
利用AGI(Artificial general intelligence)创建一个完整的量化交易系统仍旧是十分困难的, 然而幸运的是, 尝试让llm学会使用现有的成熟的量化交易系统似乎具有可行性, 我们正在尝试做这件事情.

借助langchain控制流程, 利用ChatGPT自动编写量化交易策略并进行回测, 同时提供文档问答的功能. 目前在Freqtrade量化系统中实现了较为完整的流程, 同时也支持中国大陆的AkShare和Vnpy部分功能.

## 补充知识

**模型限制**
1. ChatGPT使用的资料库截止到2021年9月12, 这意味着利用ChatGPT生成的Freqtrade策略一般都是旧版本的(v2)
2. gpt4更加智能, 利用很简单的提示词便可以很好的完成任务, 但是太贵了. gpt3.5更便宜, 但是需要在编写提示词上花费更多时间和精力. 价格参考: https://openai.com/pricing
3. 2023年6月13日, OpenAI对GPT模型进行改进, 增加了`function calling`功能, 本项目所有模型都必须使用`...-0613`模型.
4. `gpt-3.5-turbo-0613`和`gpt-4-0613`模型最多支持4096个token, 这意味着如果使用该模型, 我们给出的提示词和模型产生的策略代码长度总计不能超过约3000个单词. 如果实在有太多内容, 可以尝试使用`gpt-3.5-turbo-16k-0613`和`gpt-4-32k-0613`模型. 参考: https://platform.openai.com/docs/models/gpt-3-5
5. ChatGPT显然更加擅长英文语料相关的知识. 目前我们使用gpt3.5生成的基于Freqtrade系统的策略, 可直接运行, 而基于vnpy系统的策略, 却总是出现各种细节上的错误(只能使用更贵的gpt4模型和调整更专业的提示词解决).

**功能执行和文档问答**
1. 功能执行和文档问答是不同内容, 需要执行不同的程序. eg: `start_ft_app.py`, `start_ft_docs.py`
2. 文档问答需要依赖项目开发者编写的md文档, 因此必须将项目clone到本地. 
3. 在使用AkShare进行文档问答时必须使用`gpt-3.5-turbo-16k-0613`或`gpt-4-32k-0613`模型

**不同系统介绍**
- Freqtrade: 免费开源的加密货币交易机器人项目, 它包含完整量化交易系统的所有内容. 
- Vnpy: 中国大陆免费开源的量化交易项目, 致力于提供从交易API对接到策略自动交易的量化解决方案.
- AkShare: 中国大陆所有的金融交易数据几乎都需要花钱购买, AkShare是一个简单的替代方案. AkShare使用开源财经数据接口库采集数据, 不涉及任何个人隐私数据和非公开数据.

## 基本环境安装
1. 安装miniconda/anaconda: https://docs.conda.io/en/latest/miniconda.html
2. 安装langchain: https://python.langchain.com/docs/get_started/installation
3. 下载AsyncTrader项目代码到本地 
4. 修改`trading_system/base.py`文件, 添加`OPENAI_API_KEY`和选择`gpt3.5/4`

## 选择安装项目

推荐创建ython虚拟环境(可选项)
```markdown
conda create -n env_trader python=3.10
```

### [Freqtrade](freqtrade_system_zh.md)

1. clone项目到本地: git clone https://github.com/freqtrade/freqtrade.git
2. 进入项目目录: cd \path\freqtrade 
3. 指定安装内容
```markdown
pip install --find-links build_helpers\ TA-Lib -U
pip install -r requirements.txt
pip install -e .
pip install -r requirements-hyperopt.txt
```

安装参考: https://www.freqtrade.io/en/stable/windows_installation/

### [AkShare](akshare_system_zh.md)

1. clone项目到本地: git clone https://github.com/akfamily/akshare.git
2. 指定安装内容
```markdown
pip install akshare
```

安装参考: https://akshare.akfamily.xyz/installation.html

### [Vnpy](vnpy_system_zh.md)

1. clone项目到本地: git clone https://github.com/vnpy/vnpy.git
2. 指定安装内容
```markdown
pip install vnpy
pip install akshare
pip install vnpy_datamanager
pip install vnpy_rqdata
pip install vnpy_ctastrategy
pip install vnpy_sqlite
```
