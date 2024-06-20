import logging
from typing import Type
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

import chainlit as cl

class HumanInputQuery(BaseModel):
    """Input for the Human Input tool"""

    query: str = Field(description="The query to ask the human")

class HumanInput(BaseTool):
    """HumanInput is a tool that provides the capability to ask the user for input"""

    name: str = "human"
    description: str = (
        "You can ask a human user for guidance or information when you think you "
        "are stuck or you are not sure what to do next. "
        "The input should be a question for the human user."
    )
    args_schema: Type[BaseModel] = HumanInputQuery

    def _run(
        self,
        query: str,
        run_manager=None,
    ) -> str:
        """Use the Human input tool synchronously"""
        try:
            reply = cl.run_sync(cl.AskUserMessage(content=query, timeout=120, raise_on_timeout=True).send())
            if reply is None:
                return "Error: there was no reply. Maybe try asking again"
            return reply["output"].strip()
        except Exception as e:
            logging.error(f"Failed to get human input: {str(e)}")
            return "Error: Failed to get human input, try asking again letting the user know of the 2 minute timeout"

    async def _arun(
        self, 
        query: str="",
        run_manager=None,
        **kwargs
    ) -> str:
        if query == "":
            query = kwargs["__arg1"] if not None else ""
        try:
            reply = await cl.AskUserMessage(content=query).send()
            if reply is None:
                return "Error: there was no reply. Maybe try asking again"
            return reply["output"]
        except Exception as e:
            logging.error(f"Failed to get human input asynchronously: {str(e)}")
            return "Error: Failed to get human input"

