import os
from typing import List
from langchain.tools.base import BaseTool

from trading_system.vnpy_system.vnpy_toolkit import VnpyToolkit
from trading_system.vnpy_system.vnpy_tools import set_parameters
from trading_system.trading_agents import create_extract_agent, create_langchain_agent


def start_auto(config_file: str = "trader_vnpy.txt", add_tools: List[BaseTool] = None):
    config_file = os.path.abspath(config_file)

    # 2. Initialize the environment according to the configuration file
    vc = set_parameters(config_file)
    # 3. read strategy
    with open(config_file, "r", encoding="utf-8") as f:
        strategy_describe = f.read().split("---")[0].strip()

    toolkit = VnpyToolkit(vc=vc, config_file=config_file)
    tools = toolkit.get_tools()
    if add_tools:
        tools.extend(add_tools)
    fc_agent = create_extract_agent(tools)
    # fc_agent = create_langchain_agent(tools)
    fc_agent.run(strategy_describe)


def start_stepwise(config_file: str = "trader_vnpy.txt", add_tools: List[BaseTool] = None):
    config_file = os.path.abspath(config_file)

    # 2. Initialize the environment according to the configuration file
    vc = set_parameters(config_file)
    # 3. read strategy
    with open(config_file, "r", encoding="utf-8") as f:
        strategy_describe = f.read().split("---")[0].strip()

    toolkit = VnpyToolkit(vc=vc, config_file=config_file)
    toolkit.return_direct = True
    tools = toolkit.get_tools()
    if add_tools:
        tools.extend(add_tools)
    fc_agent = create_langchain_agent(tools)
    while True:
        command = input("command: ")
        fc_agent.run(command)
