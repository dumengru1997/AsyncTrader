from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool

from trading_system.freqtrade_system.freqtrade_tools import (
    FreqtradeBaseTool,
    FreqtradeCommandsTool,
    DataDownloadTool,
    StrategyBacktestTool,
    StrategyOptimizationTool,
    TradeSimulationTool,
    LiveTradeExecutionTool,
    StrategyCreationTool
)

from trading_system.freqtrade_system.freqtrade_commands import FreqtradeCommands


class FreqtradeToolkit(BaseToolkit):
    """Toolkit for Freqtrade System."""
    fc: FreqtradeCommands
    config_file: str
    return_direct: bool = False
    strategy_name: str = "AutoStrategy"

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        FreqtradeBaseTool.fc = self.fc
        FreqtradeBaseTool.config_file = self.config_file
        FreqtradeBaseTool.return_direct = self.return_direct
        FreqtradeBaseTool.strategy_name = self.strategy_name

        return [
            FreqtradeCommandsTool(),
            DataDownloadTool(),
            StrategyBacktestTool(),
            StrategyOptimizationTool(),
            # TradeSimulationTool(),
            # LiveTradeExecutionTool(),
            StrategyCreationTool()
        ]
