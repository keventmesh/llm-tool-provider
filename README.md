# Teach your LLM to dynamically call your services with EventTypes

This repo is a proof of concept for how to use EventTypes to have an LLM dynamically learn to call the services which are subscribed to those eventtypes.
In order for this to work, your EventTypes MUST use the `schemaData` field with a specific format of JSON string data. To see some examples, check the 
eventtypes defined in `chat-app/config/eventtypes`. This is necessary so that the LLM can learn what data and what types of data it should use when calling 
the service.

## Trying it out

To try this out, start by getting an OPENAI API key and a TAVILY API key (Tavily is a search engine optimized for AI, and is used as an example of a "hard coded" tool the LLM can call).
Putting these keys into the secret in `chat-app/config`, you will be able to deploy the app from there into a cluster that alread has Knative Eventing and Knative Serving installed,
and it will be able to call out to Tavily and ask you (the human) when it gets stuck. These are the two "hard coded" tools. To go beyond the hard coded tools and use dynamically created ones,
you will need to also deploy the `request-proxy` deployment and service in the `request-proxy` folder with `ko apply -f request-proxy/config`. This proxy is needed because the LLM expects a simple
response to its http request with the answer, and since we use a broker to talk to all our tools we need to actually subscribe to the events to figure out which is a response. Responses are found
by comparing the CE extension attribute `responseid` with the ID of the original event sent by the LLM.

Now, all you need to test it out are some functions and eventtypes! There are two functions provided in this repo which you can deploy with `func deploy`, as well as corresponding eventtypes in the
`chat-app/config/eventtypes` folder. Important: the LLM can only call your function if you have an eventtype for it!
