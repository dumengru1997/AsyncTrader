from trading_system.trading_agents import create_extract_agent
from trading_system.akshare_system.akshare_tools import AkShareBaseTool, AkShareFuturesTool


def start_auto(input_str: str):
    tools = [
        AkShareFuturesTool()
    ]
    AkShareBaseTool.data_storage = {}
    fc_agent = create_extract_agent(tools)
    fc_agent.run(input_str)
    return AkShareBaseTool.data_storage["data"]
