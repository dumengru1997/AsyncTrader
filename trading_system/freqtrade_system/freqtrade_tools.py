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

from trading_system.freqtrade_system.freqtrade_functions import FREQTRADE_COMMANDS
from trading_system.freqtrade_system.freqtrade_prompt import STRATEGY_CREATE
from trading_system.freqtrade_system.freqtrade_commands import FreqtradeCommands


def set_parameters(config_file: str, rebuild_direct: bool = False) -> FreqtradeCommands:
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
            fc = FreqtradeCommands(
                user_data_dir=config["user_data_dir"],
                exchange=config["exchange"],
                trading_mode=config["trading_mode"],
                pairs=config["pairs"],
                timeframe=config["timeframe"],
                timerange=config["timerange"],
                dry_run=config["dry_run"],
                add_timeframes=config["add_timeframes"]
            )
            fc.init_config()
            fc.validity_test()
        except Exception as e:
            all_right = False
            print(e)

    if not all_right:
        user_data_dir = input("1. Project working directory(default: user_data): ").strip()
        user_data_dir = user_data_dir if user_data_dir else "user_data"

        while True:
            fc = FreqtradeCommands(user_data_dir=user_data_dir, exchange="binance", pairs="BTC/USDT:USDT, ETH/USDT:USDT",
                                   trading_mode="futures", timeframe="5m", timerange="20230601-", dry_run=True,
                                   add_timeframes="15m, 30m", show_logs=False)
            fc.init_config()

            fc.start_list_exchanges()
            exchange = input("2. Which cryptocurrency exchange to trade on(default: binance): ").strip().lower()
            exchange = "binance" if exchange == "" else exchange

            print()
            trading_mode = input("3. Choosing a trading mode allows(futures/spot, default: futures): ").strip().lower()
            trading_mode = "spot" if trading_mode == "spot" else "futures"

            fc.start_list_markets()
            pairs = input("4. Which symbols to trade, different symbols are separated by `,` and can be expressed using regex.\n"
                          "eg: `BTC/USDT:USDT, ETH/USDT, .*/USDT:USDT`(default: BTC/USDT:USDT): ").strip()
            pairs = pairs if pairs else "BTC/USDT:USDT"

            print()
            fc.start_list_timeframes()
            timeframe = input("5. Which timeframe to trade(default: 5m): ").strip()
            timeframe = timeframe if timeframe else "5m"

            print()
            timerange = input("6. Which time range to use for historical data.\n"
                              "(eg: 20230101-, 20200201-20230501, default: 20230101-): ").strip()
            timerange = timerange if timerange else "20230101-"

            print()
            dry_run = input("7. Whether to enable simulated transaction mode(true/false, default `true`): ").strip().lower()
            dry_run = False if dry_run == "false" else True

            print()
            fc.start_list_timeframes()
            add_timeframes = input("8. Whether additional timeframes need to be added, different timeframes are separated by `,`.\n"
                                   "This is a mandatory parameter for multi-cycle trading strategies."
                                   "(eg: `15m, 30m`): ")
            try:
                params_dict = {
                    "user_data_dir": user_data_dir,
                    "exchange": exchange,
                    "trading_mode": trading_mode,
                    "pairs": pairs,
                    "timeframe": timeframe,
                    "timerange": timerange,
                    "dry_run": dry_run,
                    "add_timeframes": add_timeframes
                }
                fc = FreqtradeCommands(**params_dict, show_logs=True)
                fc.init_config()
                if not fc.validity_test():
                    input("Please carefully check whether the exchange, symbol, trading_mode, timeframe, and timerange correspond. ")
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
    return fc


class FreqtradeBaseTool(BaseTool):
    # Global controller and configuration file
    fc: FreqtradeCommands = Field(default=None, )
    config_file: str = Field(default="")

    # The project does not require AI automatic Q&A
    return_direct: bool = Field(default=False)
    strategy_name: str = Field(default="AutoStrategy")

    name = Field(default="", exclude=True)
    description = Field(default="", exclude=True)

    def _run(self, *args: Any, **kwargs: Any,) -> Any:
        return ""

    async def _arun(self, input_str: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


class FreqtradeCommandsTool(FreqtradeBaseTool):
    """ Used to modify the default configuration of the Freqtrade project. """

    name = FREQTRADE_COMMANDS[0]["name"]
    description = FREQTRADE_COMMANDS[0]["description"]

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        functions_chain = FunctionsChain(
            llm=llm_chatgpt,
            llm_kwargs={"functions": FREQTRADE_COMMANDS},
        )
        print_red("The default configuration information is being modified. Complete the configuration step by step as prompted...")
        functions_chain.predict(input=f"Please provide information about {self.name}?")

        FreqtradeBaseTool.fc = set_parameters(FreqtradeBaseTool.config_file, rebuild_direct=True)
        return "The project parameters have been configured. "


class DataDownloadTool(FreqtradeBaseTool):
    """  """
    name = "data_download"
    description = "Download historical transaction data for cryptocurrencies on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        FreqtradeBaseTool.fc.start_download_data()
        FreqtradeBaseTool.fc.start_list_data()
        return "Data download is complete. "


class StrategyBacktestTool(FreqtradeBaseTool):
    """  """
    name = "strategy_backtest"
    description = "Backtest strategy on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        df_stname = FreqtradeBaseTool.fc.start_list_strategies(return_df=True)
        if df_stname.empty:
            print_red("No strategy. You need create a new strategy")
        else:
            input_stname = ""
            if not FreqtradeBaseTool.return_direct:
                input_stname = FreqtradeBaseTool.strategy_name

            while not input_stname:
                input_stname = input("Enter the name of strategy: ").strip()
                if input_stname not in df_stname["StrategyName"].tolist():
                    input_stname = ""
            FreqtradeBaseTool.fc.start_strategy_update(input_stname)
            FreqtradeBaseTool.fc.start_backtesting(input_stname)
            # FreqtradeBaseTool.fc.start_backtesting_show()
        return "The strategy backtest is complete. "


class StrategyOptimizationTool(FreqtradeBaseTool):
    """  """
    name = "strategy_optimization"
    description = "Parameter optimization of trading strategy on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        df_stname = FreqtradeBaseTool.fc.start_list_strategies(return_df=True)
        if df_stname.empty:
            print_red("No strategy. You need create a new strategy")
        else:
            input_stname = ""
            if not FreqtradeBaseTool.return_direct:
                input_stname = FreqtradeBaseTool.strategy_name

            while not input_stname:
                input_stname = input("Enter the name of strategy: ").strip()
                if input_stname not in df_stname["StrategyName"].tolist():
                    input_stname = ""
            FreqtradeBaseTool.fc.start_hyperopt(input_stname, 20)
            FreqtradeBaseTool.fc.start_hyperopt_list()
            # index = input("View the detailed backtest result of the specified index: ").strip()
            # FreqtradeBaseTool.fc.start_hyperopt_show(int(index))

        return "Strategy parameter optimization is complete. "


class TradeSimulationTool(FreqtradeBaseTool):
    """ After starting the trading program, the program will block, and this function is not provided """
    name = "trade_simulation"
    description = "Start simulated trading on the basis of Freqtrade system."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # df_stname = FreqtradeBaseTool.fc.start_list_strategies()
        # if df_stname.empty:
        #     print_red("No strategy. You need create a new strategy")
        # else:
        #     input_stname = ""
        #     if not FreqtradeBaseTool.return_direct:
        #         input_stname = FreqtradeBaseTool.strategy_name
        #     while input_stname:
        #         input_stname = input("Enter the name of strategy: ").strip()
        #         if input_stname not in df_stname["strategy_name"].tolist():
        #             input_stname = ""
        #     FreqtradeBaseTool.fc.start_trading(input_stname)

        return ""


class LiveTradeExecutionTool(FreqtradeBaseTool):
    """ After starting the trading program, the program will block, and this function is not provided """
    name = "trade_simulation"
    description = "Start real trading on the basis of Freqtrade system. "

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # first, check account
        # df_stname = FreqtradeBaseTool.fc.start_list_strategies()
        # if df_stname.empty:
        #     print("No strategy. You need create a new strategy")
        # else:
        #     input_stname = ""
        #     if not FreqtradeBaseTool.return_direct:
        #         input_stname = FreqtradeBaseTool.strategy_name
        #     while input_stname:
        #         input_stname = input("Enter the name of strategy: ").strip()
        #         if input_stname not in df_stname["strategy_name"].tolist():
        #             input_stname = ""
        #     FreqtradeBaseTool.fc.start_trading(input_stname)

        return ""


class StrategyCreationTool(FreqtradeBaseTool):
    """ Create strategy code according to the input prompt on the basis of Freqtrade system. """

    name = "strategy_creation"
    description = "Create quantitative trading strategies through strategy descriptions. "

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        print_red(input_str)

        strategy_prompt = PromptTemplate.from_template(STRATEGY_CREATE)
        can_short = "True" if FreqtradeBaseTool.fc.trading_mode == "futures" else "False"
        strategy_prompt = strategy_prompt.format(describe=input_str, can_short=can_short)
        strategy_content = llm_chatgpt.predict(strategy_prompt)

        pattern = r"```python(.+?)```"
        matches = re.findall(pattern, strategy_content, re.DOTALL)

        if matches:
            extracted_code = matches[0].strip()
            with open(f"{FreqtradeBaseTool.fc.user_data_dir}/strategies/auto_strategy.py", "w", encoding="utf-8") as f:
                f.write(f'"""{input_str}"""\n')
                f.write(extracted_code)
        else:
            print("No Python code found.")

        return "The strategy is created and saved. "
