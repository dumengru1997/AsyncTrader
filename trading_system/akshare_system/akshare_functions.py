

AKSHARE_FUTURES = [
    {
        "name": "get_futures_daily",
        "description": "交易所日交易数据.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期, e.g `20200306`."
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期, e.g `20200306`.",
                },
                "market": {
                    "type": "string",
                    "enum": ["CFFEX", "CZCE", "SHFE", "DCE", "INE", "GFEX"],
                    "description": "选择交易所, 'CFFEX': 中金所,'CZCE': 郑商所, 'SHFE': 上期所, 'DCE': 大商所, 'INE': 上海国际能源交易中心, 'GFEX': 广州期货交易所. ",
                },
            },
            "required": ["market"],
        }
    },
    {
        "name": "futures_dce_position_rank",
        "description": "大连商品交易所-每日持仓排名-具体合约.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "指定交易日, e.g `20200306`."
                },
            },
            "required": ["date"],
        }
    },
    {
        "name": "futures_spot_price",
        "description": "指定交易日大宗商品现货价格及相应基差.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "开始日期, e.g `20200306`."
                },
                "vars_list": {
                    "type": "string",
                    "description": "合约品种如 RB、AL 等列表.",
                },
            },
            "required": ["date", "vars_list"],
        }
    },
    {
        "name": "futures_spot_price_previous",
        "description": "具体交易日大宗商品现货价格及相应基差.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "开始日期, e.g `20200306`."
                },
            },
            "required": ["date"],
        }
    },
    {
        "name": "futures_spot_price_daily",
        "description": "指定时间段内大宗商品现货价格及相应基差.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "开始日期, e.g `20200306`."
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期, e.g `20200306`.",
                },
                "vars_list": {
                    "type": "string",
                    "description": "合约品种如 RB、AL 等列表.",
                },
            },
            "required": ["vars_list"],
        }
    },
    {
        "name": "futures_czce_warehouse_receipt",
        "description": "郑州商品交易所-交易数据-仓单日报.",
        "parameters": {
            "type": "object",
            "properties": {
                "trade_date": {
                    "type": "string",
                    "description": "交易日, e.g `20200306`."
                },
            },
            "required": ["trade_date"],
        }
    },
    {
        "name": "futures_shfe_warehouse_receipt",
        "description": "上海期货交易所指定交割仓库期货仓单日报.",
        "parameters": {
            "type": "object",
            "properties": {
                "trade_date": {
                    "type": "string",
                    "description": "交易日, e.g `20200306`."
                },
            },
            "required": ["trade_date"],
        }
    },
    {
        "name": "futures_dce_warehouse_receipt",
        "description": "大连商品交易所-行情数据-统计数据-日统计-仓单日报.",
        "parameters": {
            "type": "object",
            "properties": {
                "trade_date": {
                    "type": "string",
                    "description": "交易日, e.g `20200306`."
                },
            },
            "required": ["trade_date"],
        }
    },
    {
        "name": "futures_rule",
        "description": "国泰君安期货-交易日历数据表.",
        "parameters": {
            "type": "object",
            "properties": {
                "trade_date": {
                    "type": "string",
                    "description": "交易日, e.g `20200306`."
                },
            },
            "required": ["trade_date"],
        }
    },
    {
        "name": "futures_zh_spot",
        "description": "期货的实时行情数据.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "合约名称."
                },
            },
            "required": ["symbol"],
        }
    },
    {
        "name": "futures_zh_realtime",
        "description": "期货品种当前时刻所有可交易的合约实时数据.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "合约名称."
                },
            },
            "required": ["symbol"],
        }
    },
    {
        "name": "futures_zh_minute_sina",
        "description": "中国各品种期货分钟频率数据.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "合约名称."
                },
                "period": {
                    "type": "string",
                    "enum": ["1", "5", "15", "30", "60"],
                    "description": "时间频率. 1: 1分钟, 5: 5分钟, 15: 15分钟, 30: 30分钟, 60: 60分钟.",
                },
            },
            "required": ["symbol"],
        }
    },
    {
        "name": "futures_main_sina",
        "description": "新浪财经-期货-主力连续日数据.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "合约名称."
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期, e.g `20200306`."
                },
                "end_date": {
                    "type": "string",
                    "description": "结束日期, e.g `20200306`.",
                },
            },
            "required": ["symbol", "start_date", "end_date"],
        }
    },
    {
        "name": "futures_contract_detail",
        "description": "查询期货合约详情.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "合约名称."
                },
            },
            "required": ["symbol"],
        }
    },
    {
        "name": "futures_comm_info",
        "description": "九期网-期货手续费.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "enum": ["所有", "上海期货交易所", "大连商品交易所", "郑州商品交易所", "上海国际能源交易中心", "中国金融期货交易所", "广州期货交易所"],
                    "description": "交易所名称."
                },
            },
            "required": ["symbol"],
        }
    },
]
