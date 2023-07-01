

FREQTRADE_COMMANDS = [
    {
        "name": "freqtrade_commands",
        "description": "Modify project parameters and configurations on the basic of Freqtrade.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_data_dir": {
                    "type": "string",
                    "description": "Project working directory."
                },
                "exchange": {
                    "type": "string",
                    "description": "Which cryptocurrency exchange to trade on.",
                },
                "trading_mode": {
                    "type": "string",
                    "enum": ["spot", "futures"],
                    "description": "Choosing a trading mode allows, You can short in `futures` mode.",
                },
                "pairs": {
                    "type": "string",
                    "description": "Which currency pairs to trade, different currency pairs are separated by `,` and can be expressed using regex."
                                   "(eg: `BTC/USDT:USDT, ETH/USDT, .*/USDT`, `BTC/USDT, ETH/USDT`, `BTC/USDT`)",
                },
                "timeframe": {
                    "type": "string",
                    "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "8h"],
                    "description": "Which timeframe to trade. (eg: `5m`, `1m`)",
                },
                "timerange": {
                    "type": "string",
                    "description": "Which time range to use for historical data. (eg: 20230101-, 20200201-20230501)",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Whether to enable simulated transaction mode.",
                },
                "add_timeframes": {
                    "type": "string",
                    "description": "Whether additional timeframes need to be added, different timeframes are separated by `,`. (eg: `15m, 30m`)"
                                   "This is a mandatory parameter for multi-cycle trading strategies. ",
                },
            },
            "required": ["user_data_dir", "exchange", "trading_mode", "pairs", "timeframe", "timerange", "dry_run", "add_timeframes"],
        },
    }
]
