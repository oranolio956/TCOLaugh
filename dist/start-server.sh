#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Default to Render's PORT env var (usually 10000)
PORT=${PORT:-10000}

# Update profile.json with the correct port
sed -i "s/\"port\": 10000/\"port\": $PORT/g" /app/profile.json

# For Render deployment, disable SSL since load balancer handles it
# Remove SSL certificate configuration to force HTTP mode
sed -i 's/"cert": "server.rsa.crt"/"cert": ""/g' /app/profile.json
sed -i 's/"key": "server.rsa.key"/"key": ""/g' /app/profile.json

# Start the server using the profile
exec /app/adaptixserver -profile /app/profile.json