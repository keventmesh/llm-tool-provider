#!/usr/bin/env bash

function wait_for_deployments() {
	kubectl wait deployment --all --timeout=-1s --for=condition=Available -n "$1"
}

if [[ -z $CHAT_NAMESPACE ]]; then
	export CHAT_NAMESPACE=default
fi

if [[ $OPENSHIFT ]]; then
	func_args=("-b=s2i" "--build")
else
	func_args=()
fi

if [[ $FULL_INSTALL ]]; then
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.14.1/serving-crds.yaml
	kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.14.1/serving-core.yaml
	kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.14.0/kourier.yaml
	kubectl patch configmap/config-network \
	  --namespace knative-serving \
	  --type merge \
	  --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'

	wait_for_deployments "knative-serving"

	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.14.2/eventing-crds.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.14.2/eventing-core.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.14.2/in-memory-channel.yaml
	kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.14.2/mt-channel-broker.yaml

	wait_for_deployments "knative-eventing"
fi

(cd tools/resource-cost-calculator && func deploy -n $CHAT_NAMESPACE "${func_args[@]}")
(cd tools/average-resource-consumption && func deploy -n $CHAT_NAMESPACE "${func_args[@]}")

(cd core/request-proxy && ko apply -f ./config -- -n $CHAT_NAMESPACE)
kubectl apply -f ./core/chat-app/config -n $CHAT_NAMESPACE

if [[ $OPENSHIFT ]]; then
	kubectl apply -f ./core/chat-app/config/openshift
fi

wait_for_deployments $CHAT_NAMESPACE
