from typing import  Sequence, TypedDict, Annotated
import operator
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import  BaseMessage, HumanMessage 
from langchain_core.messages import FunctionMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.globals import set_debug

from langgraph.prebuilt import ToolExecutor, ToolInvocation 
from langgraph.graph import StateGraph, END

import chainlit as cl

from human_input import HumanInput

from cloudevent_tool import create_cloudevents_tools

load_dotenv()

set_debug(True)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(temperature=0.1, streaming=True, max_retries=5, timeout=60.)
    
    tools = [HumanInput(), TavilySearchResults(max_results=1)]
    tools.extend(create_cloudevents_tools())

    tool_executor = ToolExecutor(tools)

    functions = [format_tool_to_openai_function(t) for t in tools]
    
    model = model.bind_functions(functions)

    def should_continue(state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        if "function_call" not in last_message.additional_kwargs:
            return "end"
        else:
            return "continue"

    async def call_model(state: AgentState):
        print("calling model...")
        messages = state["messages"]        
        print(messages)
        response = await model.ainvoke(messages)
        return {"messages": [response]}

    async def call_tool(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        print(last_message)

        action = ToolInvocation(
            tool=last_message.additional_kwargs["function_call"]["name"],
            tool_input=json.loads(last_message.additional_kwargs["function_call"]["arguments"]),
        )

        tasks_list = cl.user_session.get("tasks_list")
        if tasks_list is None:
            tasks_list = cl.TaskList()

        task = cl.Task(title=action.tool, status=cl.TaskStatus.RUNNING)
        await tasks_list.add_task(task)
        await tasks_list.send()

        response = await tool_executor.ainvoke(action)
        print(f"response: {response}")

        function_message = FunctionMessage(content=str(response), name=action.tool)

        task.status = cl.TaskStatus.DONE
        await tasks_list.send()

        cl.user_session.set("tasks_list", tasks_list)

        return {"messages": [function_message]}

    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model)
    graph.add_node("action", call_tool)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )

    graph.add_edge("action", "agent")

    runner = graph.compile()

    cl.user_session.set("runner", runner)



@cl.on_message
async def main(message: cl.Message):
    runner = cl.user_session.get("runner") # Type: CompiledGraph
    if runner is None:
        print("no runner!")
        return

    
    inputs = {
        "messages": [HumanMessage(content=message.content)],
    }
    cl.user_session.set("tasks_list", None)


    #res = await runner.ainvoke(inputs)

    msg = cl.Message(content="")

    async for event in runner.astream_events(inputs, version="v1"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                await msg.stream_token(content)
    
    await msg.send()
    #await cl.Message(content=res["messages"][-1].content).send()
