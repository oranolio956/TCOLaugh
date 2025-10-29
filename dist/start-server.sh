#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Use Render's PORT env var (defaults to 10000 for Render)
PORT=${PORT:-10000}

# Update profile.json with the correct port
sed -i "s/\"port\": 4321/\"port\": $PORT/g" /app/profile.json

# For Render deployment, disable SSL since load balancer handles it
# Set ssl_enabled to false to disable SSL validation
sed -i 's/"ssl_enabled": true/"ssl_enabled": false/g' /app/profile.json

# Also clear the cert and key paths since SSL is disabled
sed -i 's/"cert": "server.rsa.crt"/"cert": ""/g' /app/profile.json
sed -i 's/"key": "server.rsa.key"/"key": ""/g' /app/profile.json

# Start the server using the profile
exec /app/adaptixserver -profile /app/profile.json