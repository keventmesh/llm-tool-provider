package function

import (
	"context"
	"fmt"

	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/google/uuid"
)

type ResourceConsumptionMetric struct {
	Value float64 `json:"value"`
	Unit  string  `json:"unit"`
}

type AverageResourceConsumption struct {
	CPU    ResourceConsumptionMetric `json:"cpu"`
	Memory ResourceConsumptionMetric `json:"memory"`
	Month  string                    `json:"month"`
}

// Handle an event.
func Handle(ctx context.Context, e event.Event) (*event.Event, error) {
	fmt.Printf("Received a new event\n%s", e.String())
	mockData := []AverageResourceConsumption{
		{CPU: ResourceConsumptionMetric{Value: 2, Unit: "Cores"}, Memory: ResourceConsumptionMetric{Value: 8200, Unit: "MiB"}, Month: "March"},
		{CPU: ResourceConsumptionMetric{Value: 2.5, Unit: "Cores"}, Memory: ResourceConsumptionMetric{Value: 8117, Unit: "MiB"}, Month: "April"},
		{CPU: ResourceConsumptionMetric{Value: 3.5, Unit: "Cores"}, Memory: ResourceConsumptionMetric{Value: 9217, Unit: "MiB"}, Month: "May"},
		{CPU: ResourceConsumptionMetric{Value: 4.5, Unit: "Cores"}, Memory: ResourceConsumptionMetric{Value: 10117, Unit: "MiB"}, Month: "June"},
	}

	response := event.New()
	response.SetID(uuid.New().String())
	response.SetType("average.resource.consumption.response")
	response.SetSource("/average-resource-consumption")
	response.SetExtension("responseid", e.ID())
	err := response.SetData(event.TextJSON, mockData)
	if err != nil {
		fmt.Printf("failed to set data on event: %s", err.Error())
		return nil, err
	}
	return &response, nil // echo to caller
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
