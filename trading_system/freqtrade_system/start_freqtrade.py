import os
from typing import List
from langchain.tools.base import BaseTool

from trading_system.freqtrade_system.freqtrade_toolkit import FreqtradeToolkit
from trading_system.freqtrade_system.freqtrade_tools import set_parameters
from trading_system.trading_agents import create_extract_agent, create_langchain_agent


def start_auto(config_file: str = "trader_freqtrade.txt", workspace: str = "ft_workspace", add_tools: List[BaseTool] = None):
    config_file = os.path.abspath(config_file)

    # 1. Set the default working path
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    os.chdir(workspace)
    # 2. Initialize the environment according to the configuration file
    fc = set_parameters(config_file)
    # 3. read strategy
    with open(config_file, "r", encoding="utf-8") as f:
        strategy_describe = f.read().split("---")[0].strip()

    toolkit = FreqtradeToolkit(fc=fc, config_file=config_file)
    tools = toolkit.get_tools()
    if add_tools:
        tools.extend(add_tools)
    fc_agent = create_extract_agent(tools)
    # fc_agent = create_langchain_agent(tools)
    fc_agent.run(strategy_describe)


def start_stepwise(config_file: str = "trader_freqtrade.txt", workspace: str = "ft_workspace", add_tools: List[BaseTool] = None):
    config_file = os.path.abspath(config_file)

    # 1. Set the default working path
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    os.chdir(workspace)
    # 2. Initialize the environment according to the configuration file
    fc = set_parameters(config_file)
    # 3. read strategy
    with open(config_file, "r", encoding="utf-8") as f:
        strategy_describe = f.read().split("---")[0].strip()

    toolkit = FreqtradeToolkit(fc=fc, config_file=config_file)
    toolkit.return_direct = True
    tools = toolkit.get_tools()
    if add_tools:
        tools.extend(add_tools)
    fc_agent = create_langchain_agent(tools)
    while True:
        command = input("command: ")
        fc_agent.run(command)
