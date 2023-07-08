

VNPY_COMMANDS = [
    {
        "name": "vnpy_commands",
        "description": "Modify project parameters and configurations on the basic of vnpy.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_data_dir": {
                    "type": "string",
                    "description": "Project working directory."
                },
                "vt_symbol": {
                    "type": "string",
                    "description": "Futures contract with exchange name, eg: IF2309.CFFEX, rb2310.SHFE.",
                },
                "interval": {
                    "type": "string",
                    "enum": ["1m", "1h", "1d"],
                    "description": "Which interval to trade. (eg: `1m`)",
                },
                "timerange": {
                    "type": "string",
                    "description": "Which time range to use for historical data. (eg: 20230101-, 20200201-20230501)",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Whether to enable simulated transaction mode.",
                }
            },
            "required": ["user_data_dir", "vt_symbol", "interval", "timerange", "dry_run"],
        },
    }
]
