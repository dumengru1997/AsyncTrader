import logging
from pathlib import Path
from typing import List, Dict, Union
from datetime import datetime, timedelta
from collections import defaultdict
import json

import pandas as pd


class FreqtradeCommands:
    def __init__(
            self,
            user_data_dir: str,
            exchange: str,
            pairs: str,
            trading_mode: str,
            timeframe: str,
            timerange: str,

            dry_run: bool = True,
            add_timeframes: str = "",
            show_logs: bool = True,
    ):
        """
        @param user_data_dir: "user_data"
        @param exchange: eg: "binance"
        @param pairs: eg: "BTC/USDT:USDT, ETH/USDT:USDT"
        @param trading_mode: eg: "futures"
        @param timeframe: eg: "5m"
        @param timerange: eg: "20230101-"
        @param dry_run: eg: True
        @param add_timeframes: "15m, 30m"
        @param show_logs: output logs
        """
        self.user_data_dir = user_data_dir if user_data_dir else "user_data"
        self.exchange = exchange
        self.pairs = [i.strip() for i in pairs.split(",")]
        self.trading_mode = trading_mode
        self.timeframe = timeframe
        self.timerange = timerange
        self.dry_run = dry_run
        self.add_timeframes = [i.strip() for i in add_timeframes.split(",")] if add_timeframes else []

        if show_logs:
            from freqtrade.main import setup_logging_pre
            setup_logging_pre()

    def init_config(self):
        self.start_create_userdir()
        self.start_new_config()

    def start_create_userdir(self, reset=False) -> None:
        """
        Create "user_data" directory to contain user data strategies, hyperopt, ...)
        :param reset: Whether to overwrite existing files
        """
        from freqtrade.commands.deploy_commands import create_userdata_dir, copy_sample_files

        userdir = create_userdata_dir(self.user_data_dir, create_dir=True)
        copy_sample_files(userdir, overwrite=reset)

    def start_new_config(self) -> None:
        """
        Create a new strategy from a template
        Asking the user questions to fill out the template accordingly.
        """
        from freqtrade.commands.build_config_commands import Path, chown_user_directory, secrets, deploy_new_config

        config_path = Path(self.user_data_dir, "config.json")
        chown_user_directory(config_path.parent)
        selections = {
            'dry_run': self.dry_run,
            'stake_currency': 'USDT',
            'stake_amount': '"unlimited"',
            'max_open_trades': '3',
            'timeframe_in_config': 'Override in configuration.',
            'timeframe': self.timeframe,
            'fiat_display_currency': 'USD',
            'exchange_name': self.exchange,
            'trading_mode': self.trading_mode,
            'telegram': False,
            'telegram_token': 'telegram_token',
            'telegram_chat_id': 'telegram_chat_id',
            'api_server': False,
            'api_server_listen_addr': '127.0.0.1',
            'api_server_username': 'freqtrader',
            'api_server_password': 'freqtrader',
            'margin_mode': 'isolated',
            'api_server_jwt_key': secrets.token_hex(),
            'api_server_ws_token': secrets.token_urlsafe(25)
        }
        deploy_new_config(config_path, selections)

        with open(f"{self.user_data_dir}/config.json", "r") as f:
            config = json.load(f)
            # additional params
            config["exchange"]["pair_whitelist"] = self.pairs
            config["pairs"] = self.pairs
            config["timerange"] = self.timerange
            config["timeframes"] = self.add_timeframes.copy()
            if config["timeframe"] not in config["timeframes"]:
                config["timeframes"].append(config["timeframe"])

            # default params
            config["dataformat_ohlcv"] = "json"
            config["dataformat_trades"] = "json"
            config["pairlists"] = [{"method": "StaticPairList"}]
            config["db_url"] = f"sqlite:///{self.user_data_dir}/tradesv3.dryrun.sqlite" if self.dry_run else f"sqlite:///{self.user_data_dir}/tradesv3.sqlite"

            # path params
            config["user_data_dir"] = self.user_data_dir
            config["strategy_path"] = f"{self.user_data_dir}/strategies"
            config["datadir"] = f"{self.user_data_dir}/data/{self.exchange}"
            config["exportfilename"] = f"{self.user_data_dir}/backtest_results"

        with open(f"{self.user_data_dir}/config.json", "w") as f:
            json.dump(config, f, indent=4)

    def get_config(self):
        """  """
        from freqtrade.configuration.configuration import Configuration
        from freqtrade.enums.runmode import RunMode

        config_files = {"config": [f"{self.user_data_dir}/config.json",]}
        configuration = Configuration(config_files, RunMode.UTIL_EXCHANGE)
        config = configuration.get_config()

        # path params
        config["user_data_dir"] = Path(config["user_data_dir"])
        config["strategy_path"] = Path(config["strategy_path"])
        config["datadir"] = Path(config["datadir"])
        config["exportfilename"] = Path(config["exportfilename"])

        return config.copy()

    def start_new_strategy(self, strategy_name: str, subtemplate: str = "full") -> None:
        """
        @param strategy_name:
        @param subtemplate:
        """

        def underscore_to_camel(s):
            """  """
            components = s.split('_')
            return ''.join(x.title() for x in components)

        from freqtrade.commands.deploy_commands import Path, render_template_with_fallback, render_template, logger
        config = self.get_config()
        strategy_path = Path(config["strategy_path"], f"{strategy_name}.py")

        fallback = 'full'
        indicators = render_template_with_fallback(
            templatefile=f"strategy_subtemplates/indicators_{subtemplate}.j2",
            templatefallbackfile=f"strategy_subtemplates/indicators_{fallback}.j2",
        )
        buy_trend = render_template_with_fallback(
            templatefile=f"strategy_subtemplates/buy_trend_{subtemplate}.j2",
            templatefallbackfile=f"strategy_subtemplates/buy_trend_{fallback}.j2",
        )
        sell_trend = render_template_with_fallback(
            templatefile=f"strategy_subtemplates/sell_trend_{subtemplate}.j2",
            templatefallbackfile=f"strategy_subtemplates/sell_trend_{fallback}.j2",
        )
        plot_config = render_template_with_fallback(
            templatefile=f"strategy_subtemplates/plot_config_{subtemplate}.j2",
            templatefallbackfile=f"strategy_subtemplates/plot_config_{fallback}.j2",
        )
        additional_methods = render_template_with_fallback(
            templatefile=f"strategy_subtemplates/strategy_methods_{subtemplate}.j2",
            templatefallbackfile="strategy_subtemplates/strategy_methods_empty.j2",
        )

        strategy_text = render_template(
            templatefile='base_strategy.py.j2',
            arguments={"strategy": underscore_to_camel(strategy_name),
                       "indicators": indicators,
                       "buy_trend": buy_trend,
                       "sell_trend": sell_trend,
                       "plot_config": plot_config,
                       "additional_methods": additional_methods,
                       })
        logger.info(f"Writing strategy to `{strategy_path}`.")
        strategy_path.write_text(strategy_text)

    def start_download_data(self) -> None:
        """ """
        from freqtrade.data.history.history_utils import (
            TimeRange,
            logger,
            dynamic_expand_pairlist,
            refresh_backtest_trades_data,
            convert_trades_to_ohlcv,
            migrate_binance_futures_data,
            refresh_backtest_ohlcv_data
        )

        config = self.get_config()

        config["erase"] = False
        config["new_pairs_days"] = None

        timerange = TimeRange()
        if 'days' in config:
            time_since = (datetime.now() - timedelta(days=config['days'])).strftime("%Y%m%d")
            timerange = TimeRange.parse_timerange(f'{time_since}-')

        if 'timerange' in config:
            timerange = timerange.parse_timerange(config['timerange'])

        # Remove stake-currency to skip checks which are not relevant for datadownload
        config['stake_currency'] = ''
        pairs_not_available: List[str] = []

        # Init exchange
        from freqtrade.resolvers.exchange_resolver import ExchangeResolver
        exchange = ExchangeResolver.load_exchange(config, validate=False)
        available_pairs = [
            p for p in exchange.get_markets(
                tradable_only=True, active_only=not config.get('include_inactive')
                ).keys()
        ]

        expanded_pairs = dynamic_expand_pairlist(config, available_pairs)

        # Manual validations of relevant settings
        if not config['exchange'].get('skip_pair_validation', False):
            exchange.validate_pairs(expanded_pairs)
        logger.info(f"About to download pairs: {expanded_pairs}, "
                    f"intervals: {config['timeframes']} to {config['datadir']}")

        for timeframe in config['timeframes']:
            exchange.validate_timeframes(timeframe)

        # Start downloading
        try:
            if config.get('download_trades'):
                if config.get('trading_mode') == 'futures':
                    logger.warning("Trade download not supported for futures.")
                    return
                pairs_not_available = refresh_backtest_trades_data(
                    exchange, pairs=expanded_pairs, datadir=config['datadir'],
                    timerange=timerange, new_pairs_days=config['new_pairs_days'],
                    erase=bool(config.get('erase')), data_format=config['dataformat_trades'])

                # Convert downloaded trade data to different timeframes
                convert_trades_to_ohlcv(
                    pairs=expanded_pairs, timeframes=config['timeframes'],
                    datadir=config['datadir'], timerange=timerange, erase=bool(config.get('erase')),
                    data_format_ohlcv=config['dataformat_ohlcv'],
                    data_format_trades=config['dataformat_trades'],
                )
            else:
                if not exchange.get_option('ohlcv_has_history', True):
                    logger.warning(
                        f"Historic klines not available for {exchange.name}. "
                        "Please use `--dl-trades` instead for this exchange "
                        "(will unfortunately take a long time)."
                        )
                    return
                migrate_binance_futures_data(config)

                pairs_not_available = refresh_backtest_ohlcv_data(
                    exchange, pairs=expanded_pairs, timeframes=config['timeframes'],
                    datadir=config['datadir'], timerange=timerange,
                    new_pairs_days=config['new_pairs_days'],
                    erase=bool(config.get('erase')), data_format=config['dataformat_ohlcv'],
                    trading_mode=config.get('trading_mode', 'spot'),
                    prepend=config.get('prepend_data', False)
                )
        finally:
            if pairs_not_available:
                logger.info(f"Pairs [{','.join(pairs_not_available)}] not available "
                            f"on exchange {exchange.name}.")

    def start_list_data(self, show_timerange: bool = True, return_df: bool = False):
        """
        List available backtest data
        """
        from freqtrade.enums import TradingMode
        from freqtrade.commands.data_commands import timeframe_to_minutes, DATETIME_PRINT_FORMAT

        from tabulate import tabulate

        from freqtrade.data.history.idatahandler import get_datahandler

        config = self.get_config()
        config["show_timerange"] = show_timerange

        dhc = get_datahandler(config['datadir'], config['dataformat_ohlcv'])

        paircombs = dhc.ohlcv_get_available_data(
            config['datadir'],
            config.get('trading_mode', TradingMode.SPOT)
        )

        if config["pairs"]:
            paircombs = [comb for comb in paircombs if comb[0] in config["pairs"]]

        print(f"Found {len(paircombs)} pair / timeframe combinations.")
        result = ""
        if not config.get('show_timerange'):
            groupedpair = defaultdict(list)
            for pair, timeframe, candle_type in sorted(
                    paircombs,
                    key=lambda x: (x[0], timeframe_to_minutes(x[1]), x[2])
            ):
                groupedpair[(pair, candle_type)].append(timeframe)

            if groupedpair:
                result = tabulate([
                    (pair, ', '.join(timeframes), candle_type)
                    for (pair, candle_type), timeframes in groupedpair.items()
                ],
                    headers=("Pair", "Timeframe", "Type"),
                    tablefmt='psql', stralign='right')
                print(result)
        else:
            paircombs1 = [(
                pair, timeframe, candle_type,
                *dhc.ohlcv_data_min_max(pair, timeframe, candle_type)
            ) for pair, timeframe, candle_type in paircombs]

            result = tabulate([
                (pair, timeframe, candle_type,
                 start.strftime(DATETIME_PRINT_FORMAT),
                 end.strftime(DATETIME_PRINT_FORMAT))
                for pair, timeframe, candle_type, start, end in sorted(
                    paircombs1,
                    key=lambda x: (x[0], timeframe_to_minutes(x[1]), x[2]))
            ],
                headers=("Pair", "Timeframe", "Type", 'From', 'To'),
                tablefmt='psql', stralign='right')

            print(result)

        items = []
        result_list = result.split("\n")
        if len(result_list) > 4:
            for row in result.split("\n")[3:-1]:
                item = {}
                item["Pair"], item["Timeframe"], item["Type"], item["From"], item["To"] = \
                    [i.strip() for i in row.split("|")[1:-1]]
                items.append(item)

        if return_df:
            df = pd.DataFrame(items)
            return df

    def start_backtesting(self, strategy_name: str) -> None:
        """
        @param strategy_name:
        """
        # Import here to avoid loading backtesting module when it's not used
        from freqtrade.optimize.backtesting import Backtesting
        from freqtrade.enums.runmode import RunMode
        from freqtrade.commands.optimize_commands import logger

        # Initialize configuration
        config = self.get_config()
        config["runmode"] = RunMode.BACKTEST
        config["strategy"] = strategy_name

        logger.info('Starting freqtrade in Backtesting mode')

        # Initialize backtesting object
        backtesting = Backtesting(config)
        backtesting.start()

    def start_backtesting_show(self) -> None:
        """
        Show previous backtest result
        """
        config = self.get_config()
        config["backtest_show_pair_list"] = True

        from freqtrade.data.btanalysis import load_backtest_stats
        from freqtrade.optimize.optimize_reports import show_backtest_results, show_sorted_pairlist

        results = load_backtest_stats(config['exportfilename'])

        show_backtest_results(config, results)
        show_sorted_pairlist(config, results)

    def start_analysis_entries_exits(self) -> None:
        """ delete """

    def start_hyperopt(self, strategy_name: str, epochs: int) -> None:
        """
        Start hyperopt script
        """
        from freqtrade.commands.optimize_commands import logger, logging
        # Import here to avoid loading hyperopt module when it's not used
        from filelock import FileLock, Timeout
        from freqtrade.optimize.hyperopt import Hyperopt
        from freqtrade.enums.runmode import RunMode

        # Initialize configuration
        config = self.get_config()
        config["runmode"] = RunMode.HYPEROPT
        config["strategy"] = strategy_name

        config["epochs"] = epochs
        config["hyperopt_loss"] = "SharpeHyperOptLoss"
        config["spaces"] = "default"
        config["hyperopt_min_trades"] = 1

        logger.info('Starting freqtrade in Hyperopt mode')

        lock = FileLock(Hyperopt.get_lock_filename(config))

        try:
            with lock.acquire(timeout=1):

                # Remove noisy log messages
                logging.getLogger('hyperopt.tpe').setLevel(logging.WARNING)
                logging.getLogger('filelock').setLevel(logging.WARNING)

                # Initialize backtesting object
                hyperopt = Hyperopt(config)
                hyperopt.start()

        except Timeout:
            logger.info("Another running instance of freqtrade Hyperopt detected.")
            logger.info("Simultaneous execution of multiple Hyperopt commands is not supported. "
                        "Hyperopt module is resource hungry. Please run your Hyperopt sequentially "
                        "or on separate machines.")
            logger.info("Quitting now.")
            # TODO: return False here in order to help freqtrade to exit
            # with non-zero exit code...
            # Same in Edge and Backtesting start() functions.

    def start_hyperopt_list(self) -> None:
        """
        List hyperopt epochs previously evaluated
        """
        from freqtrade.optimize.hyperopt_tools import HyperoptTools
        from freqtrade.commands.hyperopt_commands import get_latest_hyperopt_file, colorama_init, itemgetter


        config = self.get_config()

        print_colorized = config.get('print_colorized', False)
        print_json = config.get('print_json', False)
        export_csv = config.get('export_csv')
        no_details = config.get('hyperopt_list_no_details', False)
        no_header = False

        results_file = get_latest_hyperopt_file(
            config['user_data_dir'] / 'hyperopt_results',
            config.get('hyperoptexportfilename'))

        # Previous evaluations
        epochs, total_epochs = HyperoptTools.load_filtered_results(results_file, config)

        if print_colorized:
            colorama_init(autoreset=True)

        if not export_csv:
            try:
                print(HyperoptTools.get_result_table(config, epochs, total_epochs,
                                                     not config.get('hyperopt_list_best', False),
                                                     print_colorized, 0))
            except KeyboardInterrupt:
                print('User interrupted..')

        if epochs and not no_details:
            sorted_epochs = sorted(epochs, key=itemgetter('loss'))
            results = sorted_epochs[0]
            HyperoptTools.show_epoch_details(results, total_epochs, print_json, no_header)

        if epochs and export_csv:
            HyperoptTools.export_csv_file(
                config, epochs, export_csv
            )

    def start_hyperopt_show(self, index: int = -1) -> None:
        """ Show details of a hyperopt epoch previously evaluated """
        from freqtrade.optimize.hyperopt_tools import HyperoptTools
        from freqtrade.commands.hyperopt_commands import logger, get_latest_hyperopt_file, show_backtest_result

        config = self.get_config()
        config["hyperopt_show_index"] = index

        print_json = config.get('print_json', False)
        no_header = config.get('hyperopt_show_no_header', False)
        results_file = get_latest_hyperopt_file(
            config['user_data_dir'] / 'hyperopt_results',
            config.get('hyperoptexportfilename'))

        n = config.get('hyperopt_show_index', -1)

        # Previous evaluations
        epochs, total_epochs = HyperoptTools.load_filtered_results(results_file, config)

        filtered_epochs = len(epochs)

        if n > filtered_epochs:
            logger.warning(
                f"The index of the epoch to show should be less than {filtered_epochs + 1}.")
            return
        if n < -filtered_epochs:
            logger.warning(
                f"The index of the epoch to show should be greater than {-filtered_epochs - 1}.")
            return

        # Translate epoch index from human-readable format to pythonic
        if n > 0:
            n -= 1

        if epochs:
            val = epochs[n]
            metrics = val['results_metrics']
            if 'strategy_name' in metrics:
                strategy_name = metrics['strategy_name']
                show_backtest_result(strategy_name, metrics,
                                     metrics['stake_currency'], config.get('backtest_breakdown', []))

                HyperoptTools.try_export_params(config, strategy_name, val)

            HyperoptTools.show_epoch_details(val, total_epochs, print_json, no_header,
                                             header_str="Epoch details")

    def start_list_exchanges(self) -> None:
        """
        Print available exchanges
        """
        from freqtrade.commands.list_commands import list_available_exchanges, ValidExchangesType, tabulate

        config = {
            "list_exchanges_all": False,
            "print_one_column": False,
        }
        exchanges = list_available_exchanges(config['list_exchanges_all'])

        if config['print_one_column']:
            print('\n'.join([e['name'] for e in exchanges]))
        else:
            headers = {
                'name': 'Exchange name',
                'supported': 'Supported',
                'trade_modes': 'Markets',
                'comment': 'Reason',
            }
            headers.update({'valid': 'Valid'} if config['list_exchanges_all'] else {})

            def build_entry(exchange: ValidExchangesType, valid: bool):
                valid_entry = {'valid': exchange['valid']} if valid else {}
                result: Dict[str, Union[str, bool]] = {
                    'name': exchange['name'],
                    **valid_entry,
                    'supported': 'Official' if exchange['supported'] else '',
                    'trade_modes': ', '.join(
                        (f"{a['margin_mode']} " if a['margin_mode'] else '') + a['trading_mode']
                        for a in exchange['trade_modes']
                    ),
                    'comment': exchange['comment'],
                }

                return result

            if config['list_exchanges_all']:
                print("All exchanges supported by the ccxt library:")
                exchanges = [build_entry(e, True) for e in exchanges]
            else:
                print("Exchanges available for Freqtrade:")
                exchanges = [build_entry(e, False) for e in exchanges if e['valid'] is not False]

            print(tabulate(exchanges, headers=headers, ))

    def start_list_markets(self, pairs_only: bool = False) -> None:
        """
        Print pairs/markets on the exchange
        :param pairs_only: if True print only pairs, otherwise print all instruments (markets)
        """
        from freqtrade.commands.list_commands import (
            RunMode,
            ExchangeResolver,
            plural,
            market_is_active,
            logger,
            tabulate,
            sys,
            csv,
            rapidjson

        )

        config = self.get_config()
        config["runmode"] = RunMode.UTIL_EXCHANGE
        config["list_pairs_all"] = False
        config["base_currencies"] = []
        config["quote_currencies"] = []

        config["print_one_column"] = False
        config["list_pairs_print_json"] = False
        config["print_csv"] = False
        config["print_list"] = False
        futures_only = config["trading_mode"] == "futures"
        spot_only = config["trading_mode"] == "spot"

        # Init exchange
        exchange = ExchangeResolver.load_exchange(config, validate=False)

        # By default only active pairs/markets are to be shown
        active_only = not config["list_pairs_all"]

        base_currencies = config["base_currencies"]
        quote_currencies = config["quote_currencies"] = []

        try:
            pairs = exchange.get_markets(base_currencies=base_currencies,
                                         quote_currencies=quote_currencies,
                                         tradable_only=pairs_only,
                                         futures_only=futures_only,
                                         spot_only=spot_only,
                                         active_only=active_only)
            # Sort the pairs/markets by symbol
            pairs = dict(sorted(pairs.items()))
        except Exception as e:
            logging.warning(f"Cannot get markets. Reason: {e}")
            return
        else:
            summary_str = ((f"Exchange {exchange.name} has {len(pairs)} ") +
                           ("active " if active_only else "") +
                           (plural(len(pairs), "pair" if pairs_only else "market")) +
                           (f" with {', '.join(base_currencies)} as base "
                            f"{plural(len(base_currencies), 'currency', 'currencies')}"
                            if base_currencies else "") +
                           (" and" if base_currencies and quote_currencies else "") +
                           (f" with {', '.join(quote_currencies)} as quote "
                            f"{plural(len(quote_currencies), 'currency', 'currencies')}"
                            if quote_currencies else ""))

            headers = ["Id", "Symbol", "Base", "Quote", "Active",
                       "Spot", "Margin", "Future", "Leverage"]

            tabular_data = [{
                'Id': v['id'],
                'Symbol': v['symbol'],
                'Base': v['base'],
                'Quote': v['quote'],
                'Active': market_is_active(v),
                'Spot': 'Spot' if exchange.market_is_spot(v) else '',
                'Margin': 'Margin' if exchange.market_is_margin(v) else '',
                'Future': 'Future' if exchange.market_is_future(v) else '',
                'Leverage': exchange.get_max_leverage(v['symbol'], 20)
            } for _, v in pairs.items()]

            if (config["print_one_column"] or config["list_pairs_print_json"] or config["print_csv"]):
                # Print summary string in the log in case of machine-readable
                # regular formats.
                logger.info(f"{summary_str}.")
            else:
                # Print empty string separating leading logs and output in case of
                # human-readable formats.
                print()

            if pairs:
                if config["print_list"]:
                    # print data as a list, with human-readable summary
                    print(f"{summary_str}: {', '.join(pairs.keys())}.")
                elif config["print_one_column"]:
                    print('\n'.join(pairs.keys()))
                elif config["list_pairs_print_json"]:
                    print(rapidjson.dumps(list(pairs.keys()), default=str))
                elif config["print_csv"]:
                    writer = csv.DictWriter(sys.stdout, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(tabular_data)
                else:
                    # print data as a table, with the human-readable summary
                    print(f"{summary_str}:")
                    print(tabulate(tabular_data, headers='keys', tablefmt='psql', stralign='right'))
            elif not (config["print_one_column"] or config["list_pairs_print_json"] or config["print_csv"]):
                print(f"{summary_str}.")

    def start_list_strategies(self, return_df: bool = False):
        """
        Print files with Strategy custom classes available in the directory
        """
        from freqtrade.commands.list_commands import StrategyResolver, _print_objs_tabular
        config = self.get_config()

        config["print_one_column"] = False
        config["strategy_path"] = None
        strategy_objs = StrategyResolver.search_all_objects(
            config, not config['print_one_column'], config.get('recursive_strategy_search', False))
        # Sort alphabetically
        strategy_objs = sorted(strategy_objs, key=lambda x: x['name'])
        for obj in strategy_objs:
            if obj['class']:
                obj['hyperoptable'] = obj['class'].detect_all_parameters()
            else:
                obj['hyperoptable'] = {'count': 0}

        if config['print_one_column']:
            print('\n'.join([s['name'] for s in strategy_objs]))
        else:
            _print_objs_tabular(strategy_objs, config.get('print_colorized', False))

        if return_df:
            df = pd.DataFrame(
                {
                    "StrategyName": [s['name'] for s in strategy_objs]
                }
            )
            return df

    def start_list_timeframes(self) -> None:
        """
        Print timeframes available on Exchange
        """
        from freqtrade.commands.list_commands import ExchangeResolver
        config = self.get_config()
        # Do not use timeframe set in the config
        config['timeframe'] = None
        config["print_one_column"] = False
        # Init exchange
        exchange = ExchangeResolver.load_exchange(config, validate=False)

        if config['print_one_column']:
            print('\n'.join(exchange.timeframes))
        else:
            print(f"Timeframes available for the exchange `{exchange.name}`: "
                  f"{', '.join(exchange.timeframes)}")

    def start_show_trades(self) -> None:
        """
        Show trades
        """
        from freqtrade.commands.list_commands import RunMode, logger, parse_db_uri_for_logging
        import json, os.path

        from freqtrade.persistence import Trade, init_db
        config = self.get_config()
        config["runmode"] = RunMode.UTIL_NO_EXCHANGE

        if 'db_url' not in config:
            logger.warning("--db-url is required for this command.")
            return

        logger.info(f'Using DB: "{parse_db_uri_for_logging(config["db_url"])}"')
        if not os.path.exists(config["db_url"]):
            logger.warning("--db-url doesn't exist.")
            return

        init_db(config['db_url'])
        tfilter = []

        if config.get('trade_ids'):
            tfilter.append(Trade.id.in_(config['trade_ids']))

        trades = Trade.get_trades(tfilter).all()
        logger.info(f"Printing {len(trades)} Trades: ")
        if config.get('print_json', False):
            print(json.dumps([trade.to_json() for trade in trades], indent=4))
        else:
            for trade in trades:
                print(trade)

    def start_plot_dataframe(
            self, strategy: str,
            trade_source: str = "file",
            indicators1: str = "",
            indicators2: str = "") -> None:
        """
        Entrypoint for dataframe plotting
        """
        # Import here to avoid errors if plot-dependencies are not installed.
        from freqtrade.plot.plotting import load_and_plot_trades
        from freqtrade.commands.plot_commands import RunMode

        config = self.get_config()
        config["runmode"] = RunMode.PLOT
        config["strategy"] = strategy
        config["trade_source"] = trade_source
        config["indicators1"] = [i.strip() for i in indicators1.split(",")]
        config["indicators2"] = [i.strip() for i in indicators2.split(",")]

        load_and_plot_trades(config)

    def start_plot_profit(self, strategy: str) -> None:
        """
        Entrypoint for plot_profit
        """
        # Import here to avoid errors if plot-dependencies are not installed.
        from freqtrade.plot.plotting import plot_profit
        from freqtrade.commands.plot_commands import RunMode

        config = self.get_config()
        config["runmode"] = RunMode.PLOT
        config["strategy"] = strategy

        plot_profit(config)

    def start_strategy_update(self, strategies: str) -> None:
        """
        Start the strategy updating script
        """
        from freqtrade.commands.strategy_utils_commands import sys, RunMode, StrategyResolver, start_conversion

        if sys.version_info == (3, 8):  # pragma: no cover
            sys.exit("Freqtrade strategy updater requires Python version >= 3.9")

        config = self.get_config()
        config["runmode"] = RunMode.UTIL_NO_EXCHANGE
        config["strategy_path"] = None
        config["strategy_list"] = [i.strip() for i in strategies.split(",")]

        strategy_objs = StrategyResolver.search_all_objects(
            config, enum_failed=False, recursive=config.get('recursive_strategy_search', False))

        filtered_strategy_objs = []
        if config['strategy_list']:
            filtered_strategy_objs = [
                strategy_obj for strategy_obj in strategy_objs
                if strategy_obj['name'] in config['strategy_list']
            ]

        else:
            # Use all available entries.
            filtered_strategy_objs = strategy_objs

        processed_locations = set()
        for strategy_obj in filtered_strategy_objs:
            if strategy_obj['location'] not in processed_locations:
                processed_locations.add(strategy_obj['location'])
                start_conversion(strategy_obj, config)

    def start_list_freqAI_models(self) -> None:
        """
        Print files with FreqAI models custom classes available in the directory
        """
        from freqtrade.commands.list_commands import _print_objs_tabular
        config = self.get_config()
        from freqtrade.resolvers.freqaimodel_resolver import FreqaiModelResolver

        config["print_one_column"] = False
        model_objs = FreqaiModelResolver.search_all_objects(config, not config['print_one_column'])
        # Sort alphabetically
        model_objs = sorted(model_objs, key=lambda x: x['name'])
        if config['print_one_column']:
            print('\n'.join([s['name'] for s in model_objs]))
        else:
            _print_objs_tabular(model_objs, config.get('print_colorized', False))

    def start_webserver(self) -> None:
        """
        Main entry point for webserver mode
        """
        from freqtrade.commands.webserver_commands import RunMode
        config = self.get_config()

        from freqtrade.configuration import Configuration
        from freqtrade.rpc.api_server import ApiServer

        # Initialize configuration
        config["runmode"] = RunMode.WEBSERVER
        ApiServer(config, standalone=True)

    def start_trading(self, strategy: str):
        """
        Main entry point for trading mode
        """
        from freqtrade.commands.trade_commands import signal, logger
        from freqtrade.enums import RunMode

        config = self.get_config()
        config["strategy"] = strategy
        config["runmode"] = RunMode.DRY_RUN if config["dry_run"] else RunMode.LIVE

        # Import here to avoid loading worker module when it's not used
        from freqtrade.worker import Worker

        def term_handler(signum, frame):
            # Raise KeyboardInterrupt - so we can handle it in the same way as Ctrl-C
            raise KeyboardInterrupt()

        # Create and run worker
        worker = None
        try:
            signal.signal(signal.SIGTERM, term_handler)
            worker = Worker({}, config)
            worker.run()
        except Exception as e:
            logger.error(str(e))
            logger.exception("Fatal exception!")
        except (KeyboardInterrupt):
            logger.info('SIGINT received, aborting ...')
        finally:
            if worker:
                logger.info("worker found ... calling exit")
                worker.exit()
        return 0

    def validity_test(self) -> bool:
        """ Download data and verify parameters """
        self.start_download_data()
        config = self.get_config()
        df_data = self.start_list_data(return_df=True)
        print("Downloading data and verifying parameters...")
        for pair in config["pairs"]:
            df_temp = df_data.query(f"Pair == '{pair}' and Timeframe == '{config['timeframe']}' and Type == '{config['trading_mode']}'")
            if df_temp.empty:
                print(f"{pair} download failed, please check the parameters.")
                return False

        return True


if __name__ == '__main__':
    fc = FreqtradeCommands(
        user_data_dir="bbb",
        exchange="binance",
        pairs="BTC/USDT:USDT, ETH/USDT:USDT",
        trading_mode="futures",
        timeframe="5m",
        timerange="20230601-",
        dry_run=True,
        add_timeframes="15m, 30m"
    )
    fc.init_config()
    fc.validity_test()

    # fc.start_download_data()

    # fc.start_new_strategy("my_strategy")
    # fc.start_strategy_update("MyStrategy")
    # fc.start_backtesting("MyStrategy")
    # fc.start_hyperopt("MyStrategy", 10)
    # fc.start_trading("SampleStrategy")

    # result = fc.start_list_data(return_df=True)
    # print(result)

    # print(type(result))
    # fc.start_list_exchanges()
    # fc.start_list_markets()
    fc.start_list_strategies()
    # fc.start_list_timeframes()

    # fc.start_backtesting_show()
    # fc.start_hyperopt_list()
    # fc.start_hyperopt_show(4)
    # fc.start_show_trades()

    # Advanced Topics
    # fc.start_list_freqAI_models()
    # fc.start_plot_dataframe("MyStrategy")
    # fc.start_plot_profit("MyStrategy")
    # fc.start_webserver()

"""
pip install -r requirements-hyperopt.txt

pip install -r requirements-plot
pip install -r requirements-freqai.txt
pip install -r requirements-freqai-rl
"""


