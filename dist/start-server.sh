#!/bin/sh
# Startup script for AdaptixServer on Render
# Reads PORT from environment and starts server with proper configuration

# Default to Render's PORT env var (usually 10000)
PORT=${PORT:-10000}

# Start the server with command-line flags
# This ensures compatibility with Render's dynamic port assignment
# No profile.json file is copied to container, forcing command-line usage

exec /app/adaptixserver \
    -i 0.0.0.0 \
    -p "$PORT" \
    -e /tcolaugh \
    -pw TCOLaugh2025!Secure \
    -sc /app/server.rsa.crt \
    -sk /app/server.rsa.key