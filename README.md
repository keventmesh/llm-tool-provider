# Teach your LLM to dynamically call your services with EventTypes

This repo is a proof of concept for how to use EventTypes to have an LLM dynamically learn to call the services which are subscribed to those eventtypes.
Going forwards, we are looking to generalize this approach beyond just eventtypes, so that an LLM agent can dynamically discover and call all types of
tools (both internal and external to your cluster).

## :warning: This repo is a Prototype/Proof of Concept. It **should not** be used in any kind of production environment.

## Trying it out

The prototype is (hopefully) easy to set up and use - you should be able to get it running by following the steps below:

1. Get an OpenAI api key. For instructions on this, follow the steps [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)
1. Add your api key to the secret that will be deployed:
   1. Run `cp core/chat-app/config/100-chat-app-credentials.secret.default.yaml core/chat-app/config/100-chat-app-credentials.secret.yaml`
   1. Edit `core/chat-app/config/100-chat-app-credentials.secret.yaml` to include your api key
1. Ensure that Knative Functions is installed on your machine. For installation instructions, see [here](https://knative.dev/docs/functions/install-func/)
1. With your credentials set up so that `kubectl` has access to a running cluster, run `./hack/install.sh`. If you do not already have Knative Serving and Eventing
   installed in your cluster, you can instead run `FULL_INSTALL=true ./hack/install.sh`

You will now have a cluster with everything installed and working! If anything did not work in this process, please open a GitHub issue. 

The easiest way to access the LLM app running in your cluster is to port forward the service: `kubectl port-forward svc/chat-app-service 8080:8080`.
After running this command in your terminal, you will be able to access the app at `localhost:8080`.

However, when you ask the LLM questions you will likely notice that it is not yet calling any tools to answer your questions! This is because we have not
yet created any [EventTypes](https://knative.dev/docs/eventing/event-registry/#about-eventtype-objects). To give the LLM access to the tools we have deployed
from the `tools` directory with the `./hack/install.sh` script, we will need to apply the eventtype yaml files found in `./core/chat-app/config/eventtypes`.

If you want to create your own tools for the LLM to call, the easiest way to do that would be to:
1. Create your own function with `func create -l <language of your choice> -t cloudevents <function name>`
1. Subscribe to an eventtype with `func subscribe --filter type=<your event type here>`
1. Create a corresponding eventtype for your function with the `.spec.type` field matching the type parameter from above. It is
   important when you create the eventtype that you set the `.spec.schemaData` field like it is set in the examples provided in 
   this repo so that the LLM knows how to format the `data` field of the cloudevent it will send to your function. Unfortunately,
   this prototype does not support a full OpenAPI spec there, rather a much simpler format that was easier to parse. This will be
   fixed in future work.

Hopefully this works for you! If you have any problems please open a GitHub issue.
