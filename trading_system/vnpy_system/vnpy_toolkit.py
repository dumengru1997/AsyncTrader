from typing import List

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.tools import BaseTool

from trading_system.vnpy_system.vnpy_tools import (
    VnpyBaseTool,
    VnpyCommandsTool,
    DataDownloadTool,
    StrategyBacktestTool,
    StrategyOptimizationTool,
    StrategyCreationTool
)

from trading_system.vnpy_system.vnpy_commands import VnpyCommands


class VnpyToolkit(BaseToolkit):
    """Toolkit for vnpy System."""
    vc: VnpyCommands
    config_file: str
    return_direct: bool = False
    strategy_name: str = "AtrRsiStrategy"

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        VnpyBaseTool.vc = self.vc
        VnpyBaseTool.config_file = self.config_file
        VnpyBaseTool.return_direct = self.return_direct
        VnpyBaseTool.strategy_name = self.strategy_name

        return [
            VnpyCommandsTool(),
            DataDownloadTool(),
            StrategyBacktestTool(),
            StrategyOptimizationTool(),
            StrategyCreationTool()
        ]
