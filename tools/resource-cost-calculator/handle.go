package function

import (
	"context"
	"fmt"
	"strings"

	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/google/uuid"
)

var usageCosts map[string]map[string]float64 = map[string]map[string]float64{
	"cpu":    {"cores": 12.5},
	"memory": {"mib": 0.01, "gib": 10.24},
}

type ResourceCostRequest struct {
	ResourceKind string  `json:"resourceKind"`
	Usage        float64 `json:"usage"`
	Unit         string  `json:"unit"`
}

func (r *ResourceCostRequest) Cost() (float64, error) {
	resourceCosts, ok := usageCosts[strings.ToLower(r.ResourceKind)]
	if !ok {
		return 0, fmt.Errorf("invalid resource kind")
	}

	resourceCost, ok := resourceCosts[strings.ToLower(r.Unit)]
	if !ok {
		return 0, fmt.Errorf("invalid resource unit")
	}

	return resourceCost * r.Usage, nil
}

// Handle an event.
func Handle(ctx context.Context, e event.Event) (*event.Event, error) {
	/*
	 * YOUR CODE HERE
	 *
	 * Try running `go test`.  Add more test as you code in `handle_test.go`.
	 */

	fmt.Println("Received event")
	fmt.Println(e) // echo to local output

	req := &ResourceCostRequest{}
	resp := event.New()
	resp.SetID(uuid.New().String())
	resp.SetSource("/resource-cost")
	resp.SetExtension("responseid", e.ID())

	err := e.DataAs(req)
	if err != nil {
		fmt.Printf("failed to decode data: %s", err.Error())
		resp.SetType("resource.cost.error.response")
		resp.SetData(event.TextPlain, fmt.Sprintf("Unable to decode the request received: %s", err.Error()))
		return &resp, err
	}

	cost, err := req.Cost()
	if err != nil {
		fmt.Printf("failed to calculate cost: %s", err.Error())
		resp.SetType("resource.cost.error.response")
		resp.SetData(event.TextPlain, fmt.Sprintf("Unable to calculate the cost: %s", err.Error()))
		return &resp, err
	}

	resp.SetType("word.length.result.response")
	err = resp.SetData(event.TextJSON, map[string]float64{"cost": cost})
	if err != nil {
		fmt.Printf("failed to encode result: %s", err.Error())
		resp.SetType("resource.cost.error.response")
		resp.SetData(event.TextPlain, fmt.Sprintf("Unable to process the request: %s", err.Error()))
		return &resp, err
	}

	return &resp, nil // echo to caller
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
