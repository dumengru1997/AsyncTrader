import re
import json

from typing import Optional, Any
from pydantic import Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.prompts import PromptTemplate
from langchain.tools.base import BaseTool

from trading_system.base import llm_chatgpt
from trading_system.utilities import print_red
from trading_system.functions_chain import FunctionsChain

from trading_system.vnpy_system.vnpy_functions import VNPY_COMMANDS
from trading_system.vnpy_system.vnpy_commands import VnpyCommands
from trading_system.vnpy_system.vnpy_prompts import STRATEGY_CREATE


def set_parameters(config_file: str, rebuild_direct: bool = False) -> VnpyCommands:
    """ Set default parameters
    :param config_file: Default configuration file
    :param rebuild_direct: Whether to directly rebuild the configuration file.
    :return:
    """
    with open(config_file, "r", encoding="utf-8") as f:
        tf_txt = f.read()

    tf_txt = tf_txt.split("---")
    raw_sd = tf_txt[0]

    all_right = True
    if len(tf_txt) == 1 or rebuild_direct:
        all_right = False
    else:
        try:
            strategy_description, strategy_config = tf_txt
            strategy_config = strategy_config.split("Strategy Config:")[-1].strip()
            # If the configuration is incorrect, configure it from the beginning
            config = json.loads(strategy_config)
            vc = VnpyCommands(
                vt_symbol=config["vt_symbol"],
                interval=config["interval"],
                timerange=config["timerange"],
                dry_run=config["dry_run"],
            )
            vc.init_config()
            vc.validity_test()
        except Exception as e:
            all_right = False
            print(e)

    if not all_right:
        while True:
            vc = VnpyCommands(vt_symbol="IF2309.CFFEX", interval="1m", timerange="20230101-", dry_run=True)
            vc.init_config()
            vc.start_list_exchanges()
            vt_symbol = input("1. Futures contract with exchange name, eg: IF2309.CFFEX, rb2310.SHFE: ").strip()
            vt_symbol = vt_symbol if vt_symbol else "IF2309.CFFEX"

            print()
            vc.start_list_timeframes()
            interval = input("2. Which interval to trade(default: 1m): ").strip()
            interval = interval if interval else "1m"

            print()
            timerange = input("3. Which time range to use for historical data.\n"
                              "(eg: 20230101-, 20200201-20230501, default: 20230101-): ").strip()
            timerange = timerange if timerange else "20230101-"

            print()
            dry_run = input("4. Whether to enable simulated transaction mode(true/false, default `true`): ").strip().lower()
            dry_run = False if dry_run == "false" else True

            try:
                params_dict = {
                    "vt_symbol": vt_symbol,
                    "interval": interval,
                    "timerange": timerange,
                    "dry_run": dry_run
                }
                vc = VnpyCommands(**params_dict)
                vc.init_config()
                if not vc.validity_test():
                    input("Please carefully check whether the vt_symbol, interval, and timerange correspond. ")
                    continue

                with open(config_file, "w", encoding="utf-8") as f:
                    f.write(raw_sd)
                    f.write("\n\n---\n\n")
                    f.write("Strategy Config:\n\n")
                    f.write(json.dumps(params_dict, indent=4))
                break

            except Exception as e:
                print("The configuration content is incorrect. Please carefully check and reconfigure it.")
                input(e)
    return vc


class VnpyBaseTool(BaseTool):
    # Global controller and configuration file
    vc: VnpyCommands = Field(default=None, )
    config_file: str = Field(default="")

    # The project does not require AI automatic Q&A
    return_direct: bool = Field(default=False)
    strategy_name: str = Field(default="AtrRsiStrategy")

    name = Field(default="", exclude=True)
    description = Field(default="", exclude=True)

    def _run(self, *args: Any, **kwargs: Any,) -> Any:
        return ""

    async def _arun(self, input_str: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


class VnpyCommandsTool(VnpyBaseTool):
    """ Used to modify the default configuration of the Freqtrade project. """

    name = VNPY_COMMANDS[0]["name"]
    description = VNPY_COMMANDS[0]["description"]

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        functions_chain = FunctionsChain(
            llm=llm_chatgpt,
            llm_kwargs={"functions": VNPY_COMMANDS},
        )
        print_red("The default configuration information is being modified. Complete the configuration step by step as prompted...")
        functions_chain.predict(input=f"Please provide information about {self.name}?")

        VnpyBaseTool.fc = set_parameters(VnpyBaseTool.config_file, rebuild_direct=True)
        return "The project parameters have been configured. "


class DataDownloadTool(VnpyBaseTool):
    """  """
    name = "data_download"
    description = "Download historical transaction data for cryptocurrencies on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        VnpyBaseTool.vc.start_download_data()
        VnpyBaseTool.vc.start_list_data()
        return "Data download is complete. "


class StrategyBacktestTool(VnpyBaseTool):
    """  """
    name = "strategy_backtest"
    description = "Backtest strategy on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        df_stname = VnpyBaseTool.vc.start_list_strategies()
        if df_stname.empty:
            print_red("No strategy. You need create a new strategy")
        else:
            input_stname = "AtrRsiStrategy"
            if not VnpyBaseTool.return_direct:
                input_stname = VnpyBaseTool.strategy_name

            while not input_stname:
                input_stname = input("Enter the name of strategy: ").strip()
                if input_stname not in df_stname["StrategyName"].tolist():
                    input_stname = ""
            VnpyBaseTool.vc.start_backtesting(input_stname)
            VnpyBaseTool.vc.start_backtesting_show()
        return "The strategy backtest is complete. "


class StrategyOptimizationTool(VnpyBaseTool):
    """  """
    name = "strategy_optimization"
    description = "Parameter optimization of trading strategy on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        df_stname = VnpyBaseTool.vc.start_list_strategies()
        if df_stname.empty:
            print_red("No strategy. You need create a new strategy")
        else:
            input_stname = "AtrRsiStrategy"
            print_red("暂时只支持: AtrRsiStrategy")
            if not VnpyBaseTool.return_direct:
                input_stname = VnpyBaseTool.strategy_name

            while not input_stname:
                input_stname = input("Enter the name of strategy: ").strip()
                if input_stname not in df_stname["StrategyName"].tolist():
                    input_stname = ""
            VnpyBaseTool.vc.start_hyperopt()
        return "Strategy parameter optimization is complete. "


class StrategyCreationTool(VnpyBaseTool):
    """ Create strategy code according to the input prompt on the basis of Freqtrade system. """

    name = "strategy_creation"
    description = "Create quantitative trading strategies through strategy descriptions. "

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        print_red(input_str)

        print_red("ChatGPT暂无法用vnpy写出完整的交易策略")
        strategy_prompt = PromptTemplate.from_template(STRATEGY_CREATE)
        strategy_prompt = strategy_prompt.format(describe=input_str)
        strategy_content = llm_chatgpt.predict(strategy_prompt)

        pattern = r"```python(.+?)```"
        matches = re.findall(pattern, strategy_content, re.DOTALL)

        if matches:
            extracted_code = matches[0].strip()
            config = VnpyBaseTool.vc.get_config()
            with open(f'{config["strategy_path"]}/auto_strategy.py', "w", encoding="utf-8") as f:
                f.write(f'"""{input_str}"""\n')
                f.write(extracted_code)
        else:
            print("No Python code found.")

        return "The strategy is created and saved. "
