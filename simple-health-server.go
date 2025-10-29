package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "4321"
	}

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"online","version":"v0.9","message":"TCOLaugh C2 Server Ready"}`)
	})

	http.HandleFunc("/tcolaugh", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprintf(w, `{"status":"online","version":"v0.9","endpoint":"/tcolaugh","message":"TCOLaugh C2 Server Ready"}`)
	})

	fmt.Printf("Starting simple health server on port %s\n", port)
	http.ListenAndServe(":"+port, nil)
}