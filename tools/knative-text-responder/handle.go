package function

import (
	"context"
	"fmt"

	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/google/uuid"
)

type KnativeRequest struct {
	query string `json:"query"`
}

// Handle an event.
func Handle(ctx context.Context, e event.Event) (*event.Event, error) {
	fmt.Println("Received event")
	fmt.Println(e) // echo to local output

	req := &KnativeRequest{}

	err := e.DataAs(req)
	if err != nil {
		fmt.Printf("encountered an error parsing the data: %s\n", err.Error())
		return nil, err
	}
	fmt.Printf("successfully parsed request: %+v\n", req)

	res := event.New()
	res.SetType("knative.dev.info.response")
	res.SetSource("/knative-test-responder")
	res.SetExtension("responseid", e.ID())
	res.SetID(uuid.NewString())
	err = res.SetData(event.TextPlain, "Knative is a platform-agnostic solution for running serverless deployments. It is made up of 4 key components: Serving, Eventing, Functions, and Client")
	if err != nil {
		fmt.Printf("encountered an error setting the data: %s\n", err.Error())
		return nil, err
	}

	return &res, nil // echo to caller
}

/*
Other supported function signatures:

	Handle()
	Handle() error
	Handle(context.Context)
	Handle(context.Context) error
	Handle(event.Event)
	Handle(event.Event) error
	Handle(context.Context, event.Event)
	Handle(context.Context, event.Event) error
	Handle(event.Event) *event.Event
	Handle(event.Event) (*event.Event, error)
	Handle(context.Context, event.Event) *event.Event
	Handle(context.Context, event.Event) (*event.Event, error)

*/
