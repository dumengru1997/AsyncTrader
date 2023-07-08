from typing import Any, Dict, List, Optional, Union
from pydantic import Extra, Field, root_validator

from langchain.chains.llm import LLMChain
from langchain.memory.buffer import ConversationBufferMemory
from langchain import PromptTemplate, BasePromptTemplate

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.schema import (
    BaseMemory,
    Generation,
    LLMResult,
)

from trading_system.trading_prompts import FUNCTIONS_Chain_PROMPT


FUNCTIONS_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=FUNCTIONS_Chain_PROMPT
)


class FunctionsChain(LLMChain):
    memory: BaseMemory = Field(default_factory=ConversationBufferMemory)
    """Default memory store."""
    prompt: BasePromptTemplate = FUNCTIONS_PROMPT
    """Default conversation prompt to use."""
    verbose = True

    input_key: str = "input"  #: :meta private:
    output_key: str = "response"  #: :meta private:
    chat_response: LLMResult = None

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Use this since so some prompt vars come from history."""
        return [self.input_key]

    @root_validator()
    def validate_prompt_input_variables(cls, values: Dict) -> Dict:
        """Validate that prompt input variables are consistent."""
        memory_keys = values["memory"].memory_variables
        input_key = values["input_key"]
        if input_key in memory_keys:
            raise ValueError(
                f"The input key {input_key} was also found in the memory keys "
                f"({memory_keys}) - please provide keys that don't overlap."
            )
        prompt_variables = values["prompt"].input_variables
        expected_keys = memory_keys + [input_key]
        if set(expected_keys) != set(prompt_variables):
            raise ValueError(
                "Got unexpected prompt input variables. The prompt expects "
                f"{prompt_variables}, but got {memory_keys} as inputs from "
                f"memory, and {input_key} as the normal input key."
            )
        return values

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        self.chat_response = self.generate([inputs], run_manager=run_manager)
        return self.create_outputs(self.chat_response)[0]


def functions_chain_to_functions_call(functions_chain: FunctionsChain) -> Union[None, Dict[str, str]]:
    """ input `FunctionsChain`, output `function_call`"""
    gen: Generation = functions_chain.chat_response.generations[0][0]
    if hasattr(gen, "message") and hasattr(gen.message, "additional_kwargs") and gen.message.additional_kwargs.get("function_call"):
        function_call = gen.message.additional_kwargs.get("function_call")
        if function_call:
            return function_call
