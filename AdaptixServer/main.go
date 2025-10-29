package main

import (
	"AdaptixServer/core/server"
	"AdaptixServer/core/utils/logs"
	"AdaptixServer/core/utils/token"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
)

const VERSION = "0.9"

func main() {
	fmt.Printf("\n[===== Oranolio Framework v%v =====]\n\n", VERSION)

	var (
		err          error
		host         = flag.String("i", getEnv("HOST", "0.0.0.0"), "Teamserver listen interface")
		port         = flag.Int("p", getEnvInt("PORT", 0), "Teamserver handler port")
		endpoint     = flag.String("e", getEnv("ENDPOINT", ""), "Teamserver URI endpoint")
		password     = flag.String("pw", getEnv("PASSWORD", ""), "Teamserver password")
		certPath     = flag.String("sc", getEnv("CERT_PATH", ""), "Path to the SSL certificate")
		keyPath      = flag.String("sk", getEnv("KEY_PATH", ""), "Path to the SSL key")
		extenderPath = flag.String("ex", getEnv("EXTENDER_PATH", ""), "Path to the extender file")
		debug        = flag.Bool("debug", getEnvBool("DEBUG", false), "Enable debug mode")
		profilePath  = flag.String("profile", getEnv("PROFILE_PATH", ""), "Path to JSON profile file")
	)

	flag.Usage = func() {
		fmt.Printf("Usage: AdaptixServer [options]\n")
		fmt.Printf("Options:\n")
		flag.PrintDefaults()
		fmt.Printf("\nEither provide options individually or use a JSON config file with -config flag.\n\n")
		fmt.Printf("Example:\n")
		fmt.Printf("   AdaptixServer -i 0.0.0.0 -p port -pw password -e endpoint -sc SslCert -sk SslKey [-ex ext1,ext2,...] [-debug]\n")
		fmt.Printf("   AdaptixServer -profile profile.json [-debug]\n")
	}
	flag.Parse()

	logs.NewPrintLogger(*debug)
	logs.RepoLogsInstance, err = logs.NewRepoLogs()
	if err != nil {
		logs.Error("", err.Error())
		os.Exit(0)
	}

	ts := server.NewTeamserver()

	if *profilePath != "" {
		err := ts.SetProfile(*profilePath)
		if err != nil {
			logs.Error("", err.Error())
			os.Exit(1)
		}
	} else if *port > 1 && *port < 65535 && *endpoint != "" && *password != "" {
		extenders := strings.Split(*extenderPath, ",")
		ts.SetSettings(*host, *port, *endpoint, *password, *certPath, *keyPath, extenders)
	} else {
		flag.Usage()
		os.Exit(0)
	}

	err = ts.Profile.IsValid()
	if err != nil {
		logs.Error("", err.Error())
		os.Exit(0)
	}

	token.InitJWT(ts.Profile.Server.ATokenLive, ts.Profile.Server.RTokenLive)

	ts.Extender.LoadPlugins(ts.Profile.Server.Extenders)

	ts.Start()
}

// Helper functions for environment variables
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}
