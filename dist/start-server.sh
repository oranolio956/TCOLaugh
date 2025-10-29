#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Default to Render's PORT env var (usually 10000)
PORT=${PORT:-10000}

# Start the server with command-line flags
# This ensures compatibility with Render's dynamic port assignment
# Remove any profile.json files to force command-line usage
rm -f /app/profile.json

exec /app/adaptixserver \
    -i 0.0.0.0 \
    -p "$PORT" \
    -e /tcolaugh \
    -pw TCOLaugh2025!Secure \
    -sc /app/server.rsa.crt \
    -sk /app/server.rsa.key