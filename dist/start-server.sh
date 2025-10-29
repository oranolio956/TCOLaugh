#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Use Render's PORT env var (10000 for this service)
PORT=${PORT:-10000}

# Update profile.json with the correct port
sed -i "s/\"port\": [0-9][0-9]*/\"port\": $PORT/g" /app/profile.json

# For Render deployment, keep SSL enabled for HTTPS
# SSL certificates are provided in the container

# Start the server using the profile
exec /app/adaptixserver -profile /app/profile.json