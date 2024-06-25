package function

import (
	"context"
	"fmt"

	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/google/uuid"
)

type WordLengthRequest struct {
	Words []string `json:"words"`
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

	req := &WordLengthRequest{}
	resp := event.New()
	resp.SetID(uuid.NewString())
	resp.SetSource("/word-length")
	resp.SetExtension("responseid", e.ID())

	err := e.DataAs(req)
	if err != nil {
		fmt.Printf("failed to decode data: %s", err.Error())
		resp.SetType("word.length.error.response")
		resp.SetData(event.TextPlain, fmt.Sprintf("Unable to decode the request received: %s", err.Error()))
		return &resp, err
	}
	lengths := make(map[string]int)

	for _, w := range req.Words {
		lengths[w] = len(w)
	}

	resp.SetType("word.length.result.response")
	err = resp.SetData(event.TextJSON, lengths)
	if err != nil {
		fmt.Printf("failed to encode result: %s", err.Error())
		resp.SetType("word.length.error.response")
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
