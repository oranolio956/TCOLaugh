#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Use Render's PORT env var (10000 for this service)
PORT=${PORT:-10000}

echo "Starting AdaptixServer with PORT=$PORT"

# Update profile.json with the correct port
echo "Updating profile.json port to $PORT"
sed -i "s/\"port\": [0-9][0-9]*/\"port\": $PORT/g" /app/profile.json

# Verify the port was updated
echo "Profile port after update:"
grep "port" /app/profile.json

# For Render deployment, disable SSL since load balancer handles it
# This allows health checks to work via HTTP
sed -i 's/"ssl_enabled": true/"ssl_enabled": false/g' /app/profile.json

# Start the server using the profile
echo "Starting server..."
exec /app/adaptixserver -profile /app/profile.json