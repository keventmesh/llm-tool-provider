import json
from typing import Any, Dict, List 
from os import environ as env
import requests
import aiohttp

from cloudevents.http import CloudEvent
from cloudevents.conversion import to_binary

from langchain_core.pydantic_v1 import Field, create_model 
from langchain_core.tools import BaseTool

from kubernetes import config, dynamic
from kubernetes import client as k8s_client
from kubernetes.dynamic.exceptions import ResourceNotFoundError
from kubernetes.client import api_client

try:
    if env["IN_KUBERNETES"] is not None:
        client = dynamic.DynamicClient(
            api_client.ApiClient(configuration=config.load_incluster_config())
        )
except KeyError:
    print("not in k8s, not loading client config")
    

def make_request_maker(eventtype, request_structure):
    attributes = {
        "type": eventtype["spec"]["type"],
        "datacontenttype": "application/json",
        "source": "/chat-app",
    }
    def make_request(request):
        data = {}
        for k, v in request.items():
            if k in request_structure:
                data[k] = v
        print(data)
        event = CloudEvent(attributes, data)
        return to_binary(event)

    return make_request

def make_run(construct_request):
    def run(self, **kwargs) -> str:
        headers, body = construct_request(kwargs)

        res = requests.post(env["K_SINK"], data=body, headers=headers)
        if res.ok:
            return res.text
        else:
            return "Failed to ask your question about Knative"

    return run

def make_arun(construct_request):
    async def arun(self, **kwargs) -> str:
        headers, body = construct_request(kwargs)
        print(headers)

        async with aiohttp.ClientSession() as session:
            res = await session.post(env["K_SINK"], data=body, headers=headers)
            if res.ok:
                text = await res.text()
                print(text)
                return text
            else:
                return "Failed to ask your question about Knative"

    return arun

types = {"string": str, "int": int, "float": float, "list:string": List[str], "list:int": List[int], "list:float": List[float]}

def make_input_class(eventtype, request_structure: Dict[str, Dict[str, Any]]):
    d = {}
    for parameter, info in request_structure.items():
        t = types.get(info.get("type", ""), str)
        desc = types.get(info.get("description", ""), f"The {parameter} value") # Type: str
        d[parameter] = (t, Field(description=desc))

    name = eventtype["spec"]["type"].replace(".", "_",) + "_input"
    return create_model(name, **d)

def make_tool(eventtype, request_structure: Dict[str, Dict[str, Any]]) -> BaseTool:
    request_factory = make_request_maker(eventtype, request_structure)

    name = eventtype["spec"]["type"].replace(".", "_")

    tool_class = type(name, (BaseTool,), {
        "name": name,
        "description": eventtype["spec"]["description"],
        "_run": make_run(request_factory),
        "_arun": make_arun(request_factory),
    })

    input_class = make_input_class(eventtype, request_structure)

    return tool_class(args_schema=input_class)



def get_eventtypes() -> List:
    custom_object_api = k8s_client.CustomObjectsApi()
    try:
        eventtypes = custom_object_api.list_namespaced_custom_object("eventing.knative.dev", "v1beta2", "default", "eventtypes")
        return eventtypes["items"]
    except ResourceNotFoundError as e:
        print(f"failed to get eventtypes: {e}")
        return []

def process_eventtype_to_request_structure(eventtype):
    request_structure = {}
    schema_data = eventtype.get("spec", {}).get("schemaData", None)
    if schema_data is not None:
        request_structure = json.loads(schema_data)
    return request_structure
        

def create_cloudevents_tools() -> List:
    result = []
    try:
        in_k8s = env["IN_KUBERNETES"] is not None
    except KeyError:
        in_k8s = False

    if in_k8s:
        print("getting eventtypes")
        for et in get_eventtypes():
            request_structure = process_eventtype_to_request_structure(et)
            tool = make_tool(et, request_structure)
            if tool is not None:
                result.append(tool)


    #knative_text_eventtype = {"type": "dev.knative.info.request", "description": "This answers any and all questions you have about Knative"}
    #request_structure = {"query": {"type": "string", "description": "The question you would like to ask about Knative"}}
    #tool = make_tool(knative_text_eventtype, request_structure)
    return result

