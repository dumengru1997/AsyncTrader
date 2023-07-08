from typing import Optional, Any, Dict

import pandas as pd
from pydantic import Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool

from trading_system.base import llm_chatgpt
from trading_system.utilities import print_red
from trading_system.functions_chain import FunctionsChain, functions_chain_to_functions_call

from trading_system.akshare_system.akshare_functions import AKSHARE_FUTURES
from trading_system.akshare_system.akshare_commands import function_call


class AkShareBaseTool(BaseTool):
    # Global controller and configuration file
    data_storage: Dict[str, pd.DataFrame] = Field(default={})

    # The project does not require AI automatic Q&A
    return_direct: bool = Field(default=True)

    name = Field(default="", exclude=True)
    description = Field(default="", exclude=True)

    def _run(self, *args: Any, **kwargs: Any,) -> Any:
        return ""

    async def _arun(self, input_str: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


class AkShareFuturesTool(AkShareBaseTool):
    """  """
    name = "akshare_futures"
    description = "Access to financial data related to futures through the AkShare project."

    def _run(self, input_str: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        functions_chain = FunctionsChain(
            llm=llm_chatgpt,
            llm_kwargs={"functions": AKSHARE_FUTURES},
        )
        functions_chain.predict(input=input_str)
        response = functions_chain_to_functions_call(functions_chain)
        if response:
            result = function_call(response)
            AkShareBaseTool.data_storage["data"] = result
        return "Data acquisition complete. "
