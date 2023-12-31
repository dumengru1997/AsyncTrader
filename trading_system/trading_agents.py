from typing import Tuple, Union, Sequence, Any, List

from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType, ZeroShotAgent, AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.tools.base import BaseTool
from langchain.callbacks.manager import Callbacks

from trading_system.base import llm_chatgpt
from trading_system.trading_prompts import EXTRACT_STRATEGY, EXTRACT_AKSHARE


class ExtractAgent(ZeroShotAgent):
    """ """
    @property
    def input_keys(self):
        return ["input"]

    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """ Make subtle adjustments to the ZeroShotAgent and select different input methods for different tasks. """
        full_inputs = self.get_full_inputs(intermediate_steps, **kwargs)
        full_output = self.llm_chain.predict(callbacks=callbacks, **full_inputs)
        out_put_list = full_output.split("\n")
        for out in out_put_list:
            if out.startswith("Action:"):
                tool_name = out.split(":")[-1].strip()
                if tool_name == "strategy_creation":
                    prompt = PromptTemplate(template=EXTRACT_STRATEGY, input_variables=["raw_input"])
                elif tool_name.startswith("akshare_"):
                    prompt = PromptTemplate(template=EXTRACT_AKSHARE, input_variables=["raw_input"])
                else:
                    continue

                prompt = prompt.format(raw_input=full_inputs["input"])
                action_input = llm_chatgpt.predict(prompt)
                out_put = full_output.split("Action Input:")[0]
                full_output = f"{out_put}Action Input: {action_input}"
        return self.output_parser.parse(full_output)

    async def aplan(
            self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        raise NotImplementedError("TraderAgent does not support async")


def create_extract_agent(tools: Sequence[BaseTool]):
    """ Create an Agent by using TraderAgent """
    agent = ExtractAgent.from_llm_and_tools(llm=llm_chatgpt, tools=tools)
    return AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True
    )


def create_langchain_agent(tools: Sequence[BaseTool]):
    """ Create an Agent by using ZeroShotAgent """
    return initialize_agent(
        tools=tools,
        llm=llm_chatgpt,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
