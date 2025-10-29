#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Use Render's PORT env var (4321 for this service)
PORT=${PORT:-4321}

# Update profile.json with the correct port
sed -i "s/\"port\": 10000/\"port\": $PORT/g" /app/profile.json

# For Render deployment, disable SSL since load balancer handles it
# Set ssl_enabled to false to disable SSL validation
sed -i 's/"ssl_enabled": true/"ssl_enabled": false/g' /app/profile.json

# Start the server using the profile
exec /app/adaptixserver -profile /app/profile.json