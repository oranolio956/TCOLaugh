package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type AdaptixProfile struct {
	Server struct {
		SSLEnabled bool   `json:"ssl_enabled"`
		Cert       string `json:"cert"`
		Key        string `json:"key"`
	} `json:"Teamserver"`
}

func main() {
	fileContent, err := os.ReadFile("/tmp/test_app/profile.json")
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}
	
	var profile AdaptixProfile
	err = json.Unmarshal(fileContent, &profile)
	if err != nil {
		fmt.Printf("Error parsing JSON: %v\n", err)
		return
	}
	
	fmt.Printf("SSLEnabled: %v\n", profile.Server.SSLEnabled)
	fmt.Printf("Cert: \"%s\"\n", profile.Server.Cert)
	fmt.Printf("Key: \"%s\"\n", profile.Server.Key)
}
