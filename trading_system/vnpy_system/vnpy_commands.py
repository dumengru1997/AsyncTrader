import re
import os
import json
import sqlite3
import numpy as np

from typing import Dict, Union
import importlib.util
import importlib.machinery
import inspect


import pandas as pd
import akshare as ak

from peewee import SqliteDatabase as PeeweeSqliteDatabase
from datetime import datetime
from typing import List
from trading_system.utilities import camel_to_underscore

from vnpy.trader.optimize import OptimizationSetting
from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy.trader.constant import Interval, Exchange
from vnpy.trader.object import BarData
from vnpy.trader.utility import ZoneInfo, get_file_path
from vnpy.trader.database import get_database
from vnpy_ctastrategy.template import CtaTemplate
from vnpy_ctastrategy import template


FUTURES_EXCHANGE = {
    "中国金融期货交易所": Exchange.CFFEX,
    "上海期货交易所": Exchange.SHFE,
    "上海国际能源交易中心": Exchange.INE,
    "郑州商品交易所": Exchange.CZCE,
    "大连商品交易所": Exchange.DCE,
    "广州期货交易所": Exchange.GFEX,
}

FUTURES_INTERVAL = {
    "m": Interval.MINUTE,
    "h": Interval.HOUR,
    "d": Interval.DAILY,
    "tick": Interval.TICK
}


class VnpyCommands:
    def __init__(
            self,
            vt_symbol: str,
            interval: str,
            timerange: str,
            dry_run: bool = True,
    ):
        """
        @param vt_symbol: eg: "IF2309.CFFEX, rb2310.SHFE"
        @param interval: eg: "5m"
        @param timerange: eg: "20230101-"
        @param dry_run: eg: True
        """
        self.vt_symbol = vt_symbol
        self.interval = interval
        self.timerange = timerange
        self.dry_run = dry_run

        # init sqlite database
        self.sqlite_db = get_database()
        self.backtest_engine = None

        # 从akshare获取期货基础信息
        self.df_futures_comm_info = ak.futures_comm_info(symbol="所有")
        today_str = datetime.today().date()
        df_trade_date = ak.tool_trade_date_hist_sina()
        last_date = df_trade_date[df_trade_date["trade_date"] < today_str]["trade_date"].tolist()[-1].strftime("%Y%m%d")
        self.df_futures_rule = ak.futures_rule(date=last_date)

        self.df_futures_comm_info["合约"] = self.df_futures_comm_info["合约代码"].str.replace('[^a-zA-Z]', '', regex=True)

    def init_config(self):
        self.start_new_config()

    def start_new_config(self) -> None:
        """ """
        config = {}
        config["vt_symbol"] = self.vt_symbol
        config["timerange"] = self.timerange
        config["interval"] = self.interval

        # path params
        config["strategy_path"] = f"{os.path.dirname(template.__file__)}/strategies"
        config["datadir"] = str(get_file_path("."))

        with open(f'{str(get_file_path("."))}/config.json', "w") as f:
            json.dump(config, f, indent=4)

        # connect database
        path: str = str(get_file_path("database.db"))
        db: PeeweeSqliteDatabase = PeeweeSqliteDatabase(path)
        self.sqlite_db.db = db

    def get_config(self) -> dict:
        """  """
        with open(f'{str(get_file_path("."))}/config.json', "r") as f:
            config = json.load(f)

        return config.copy()

    def import_data_from_csv(self, df_data: pd.DataFrame, symbol: str, exchange: Exchange, interval: Interval, tz_name: str, datetime_head: str, open_head: str, high_head: str, low_head: str, close_head: str, volume_head: str, turnover_head: str, open_interest_head: str, datetime_format: str) -> tuple:
        """ """
        bars: List[BarData] = []
        start: datetime = None
        count: int = 0
        tz = ZoneInfo(tz_name)

        for _, item in df_data.iterrows():
            if datetime_format:
                dt: datetime = datetime.strptime(item[datetime_head], datetime_format)
            else:
                dt: datetime = datetime.fromisoformat(item[datetime_head])
            dt = dt.replace(tzinfo=tz)

            turnover = item.get(turnover_head, 0)
            open_interest = item.get(open_interest_head, 0)
            bar: BarData = BarData(
                symbol=symbol,
                exchange=exchange,
                datetime=dt,
                interval=interval,
                volume=float(item[volume_head]),
                open_price=float(item[open_head]),
                high_price=float(item[high_head]),
                low_price=float(item[low_head]),
                close_price=float(item[close_head]),
                turnover=float(turnover),
                open_interest=float(open_interest),
                gateway_name="DB",
            )
            bars.append(bar)
            # do some statistics
            count += 1
            if not start:
                start = bar.datetime

        end: datetime = bar.datetime
        # insert into database
        self.sqlite_db.save_bar_data(bars)
        return start, end, count

    def start_download_data(self) -> None:
        """ """
        config = self.get_config()
        df_futures_comm = self.df_futures_comm_info
        df_futures_comm["交易所"] = df_futures_comm["交易所名称"].map(FUTURES_EXCHANGE)

        timerange = config["timerange"]
        start_time, end_time = timerange.split("-")
        assert len(start_time) == 8, "config['timerange'] Incorrect format"
        assert len(end_time) in [8, 0], "config['timerange'] Incorrect format"
        print("AkShare不支持指定时间周期数据下载, 默认下载1024根K线数据...")

        symbol = config["vt_symbol"].split(".")[0]
        contract = re.sub('[^a-zA-Z]', '', symbol)
        exchange = df_futures_comm[df_futures_comm["合约"] == contract].reset_index().loc[0, "交易所"]

        period = config["interval"]
        period_suffix = period[-1].lower()
        print(symbol, ", ", period)
        data = ak.futures_zh_minute_sina(symbol, period)
        info = self.import_data_from_csv(
            df_data=data,
            symbol=symbol,
            exchange=exchange,
            interval=FUTURES_INTERVAL[period_suffix],
            tz_name="Asia/Shanghai",
            datetime_head="datetime",
            open_head="open",
            high_head="high",
            low_head="low",
            close_head="close",
            volume_head="volume",
            turnover_head="",
            open_interest_head="",
            datetime_format="",
        )
        print("data import succeeded: ", info)

    def start_list_data(self):
        """ List available backtest data """
        # 连接到 SQLite 数据库
        conn = sqlite3.connect(str(get_file_path("database.db")))  # 替换为你的数据库名
        c = conn.cursor()
        # 查询所有的表名
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        # 对于每个表，查询并打印其数据
        for table_name in tables:
            table_name = table_name[0]
            if not table_name.endswith("overview"):
                continue
            c.execute(f"SELECT * from {table_name}")
            # Fetches all rows from the result of the query
            rows = c.fetchall()
            for row in rows:
                print(f"Table name: {table_name}")
                print(row)
        # 关闭数据库连接
        conn.close()

    def start_backtesting(self, strategy_name: str, fees: float=0.0) -> Union[Dict, None]:
        """  """
        # 动态导入策略
        config = self.get_config()
        strategy_file = camel_to_underscore(strategy_name)

        # 先检查默认策略路径是否存在策略
        directory = f"{os.path.dirname(template.__file__)}/strategies"
        strategy = ""
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                module_name = filename[:-3]  # 去掉 ".py"
                if module_name == strategy_file:
                    # 动态导入模块
                    full_name = f"vnpy_ctastrategy.strategies.{module_name}"
                    module = importlib.import_module(full_name)
                    strategy = getattr(module, strategy_name)
                    break
        # 再检查自定义路径策略
        if strategy == "":
            print("策略文件不存在...")
            return

        timerange = config["timerange"]
        start_time, end_time = timerange.split("-")
        start = datetime.strptime(start_time, "%Y%m%d")
        end = datetime.strptime(end_time, "%Y%m%d") if end_time else datetime.today()

        symbol = config["vt_symbol"].split(".")[0]
        contract = re.sub('[^a-zA-Z]', '', symbol)
        self.df_futures_comm_info["手续费标准-开仓-万分之"].fillna(0.00001, inplace=True)

        ext_fees = self.df_futures_comm_info[self.df_futures_comm_info["合约"] == contract].reset_index().loc[0, "手续费标准-开仓-万分之"]
        contract_upper = contract.upper()
        pricetick = self.df_futures_rule[self.df_futures_rule["代码"] == contract_upper].reset_index().loc[0, "最小变动价位"]
        size = self.df_futures_rule[self.df_futures_rule["代码"] == contract_upper].reset_index().loc[0, "合约乘数"]

        engine = BacktestingEngine()
        engine.set_parameters(
            vt_symbol=config["vt_symbol"],
            interval=config["interval"],
            start=start,
            end=end,
            rate=(fees if fees else ext_fees) * 2,
            slippage=pricetick,
            size=size,
            pricetick=pricetick,
            capital=1_000_000,
        )
        engine.add_strategy(strategy, {})
        engine.load_data()
        engine.run_backtesting()
        engine.calculate_result()

        self.backtest_engine = engine
        result = engine.calculate_statistics()
        result["start_date"] = result["start_date"].strftime("%Y-%m-%d")
        result["end_date"] = result["end_date"].strftime("%Y-%m-%d")
        for key in result:
            if type(result[key]) == np.float64:
                result[key] = round(float(result[key]), 6)
            elif type(result[key]) == np.int32:
                result[key] = int(result[key])
            elif type(result[key]) == np.int64:
                result[key] = int(result[key])
        with open(f'{config["datadir"]}/last_backtest.json', "w") as f:
            json.dump(result, f, indent=4)
        return result

    def start_backtesting_show(self) -> None:
        """
        Show previous backtest result
        """
        config = self.get_config()

        json_file = f'{config["datadir"]}/last_backtest.json'
        if not os.path.exists(json_file):
            print("回测文件不存在: ", json_file)
            return

        with open(json_file, "r") as f:
            result = json.load(f)
            for key in result:
                print(key, ": ", result[key])

    def start_hyperopt(self) -> None:
        """ """
        config = self.get_config()

        setting = OptimizationSetting()
        setting.set_target("sharpe_ratio")
        setting.add_parameter("atr_length", 25, 27, 1)
        setting.add_parameter("atr_ma_length", 10, 30, 10)

        self.start_backtesting("AtrRsiStrategy")
        result = self.backtest_engine.run_ga_optimization(setting)
        df = pd.DataFrame(result)
        df.to_csv(f'{config["datadir"]}/last_hyperopt.csv', index=False)

    def start_hyperopt_show(self, index: int = -1) -> None:
        """ Show details of a hyperopt epoch previously evaluated """
        config = self.get_config()
        hyperopt_file = f'{config["datadir"]}/last_hyperopt.csv'
        df = pd.read_csv(hyperopt_file)
        print(df)

    def find_classes_in_directory(self, directory, base_class_name) -> Dict:
        subclasses = {}
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                module_name = filename[:-3]  # 去掉 ".py"
                module_path = os.path.join(directory, filename)
                loader = importlib.machinery.SourceFileLoader(module_name, module_path)
                module = loader.load_module()

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, base_class_name):
                        subclasses[name] = filename
        return subclasses

    def start_list_strategies(self) -> pd.DataFrame:
        """
        Print files with Strategy custom classes available in the directory
        """
        config = self.get_config()
        strategies = self.find_classes_in_directory(config["strategy_path"], CtaTemplate)
        strategies = {k: strategies[k] for k in strategies if k != "CtaTemplate"}

        items = []
        for key in strategies:
            item = {}
            item["strategy_name"] = key
            item["strategy_file"] = strategies[key]
            items.append(item)
        df_strategy = pd.DataFrame(items)
        print(df_strategy)
        return df_strategy

    def start_list_exchanges(self) -> pd.DataFrame:
        """ Print available exchanges """
        exchanges = list(set(self.df_futures_comm_info["交易所名称"].to_list()))
        items = []
        for ex in exchanges:
            item = {}
            item["name"] = ex
            item["code"] = FUTURES_EXCHANGE[ex]
            items.append(item)
        df = pd.DataFrame(items)
        print(df)
        return df

    def start_list_timeframes(self) -> None:
        """
        Print timeframes available on Exchange
        """
        for i in Interval:
            print(i.value)

    def start_trading(self, strategy: str):
        """
        Main entry point for trading mode
        """
        ...

    def validity_test(self) -> bool:
        """ Download data and verify parameters """
        self.start_download_data()
        return True


if __name__ == '__main__':
    vc = VnpyCommands(
        vt_symbol="IF2309.CFFEX",
        interval="1m",
        timerange="20230101-",
        dry_run=True,
    )
    vc.init_config()
    vc.validity_test()
    vc.start_list_data()
    vc.start_backtesting(strategy_name="AutoStrategy")
    vc.start_backtesting_show()
    # vc.start_hyperopt()
    # vc.start_hyperopt_show()
    # vc.start_list_strategies()
    # vc.start_list_exchanges()
    # vc.start_list_timeframes()


"""
pip install akshare
pip install vnpy_datamanager
pip install vnpy_rqdata
pip install vnpy_ctastrategy
pip install vnpy_sqlite
"""