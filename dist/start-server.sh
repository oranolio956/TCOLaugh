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
echo "Disabling SSL for Render deployment..."

# Create a new profile without SSL configuration
cat > /app/profile_render.json << 'EOF'
{
  "Teamserver": {
    "interface": "0.0.0.0",
    "port": 10000,
    "endpoint": "/tcolaugh",
    "password": "pass",
    "only_password": true,
    "operators": {
      "operator1": "pass1",
      "operator2": "pass2"
    },
    "ssl_enabled": false,
    "cert": "",
    "key": "",
    "extenders": [
      "extenders/listener_beacon_http/config.json",
      "extenders/listener_beacon_smb/config.json",
      "extenders/listener_beacon_tcp/config.json",
      "extenders/agent_beacon/config.json",
      "extenders/listener_gopher_tcp/config.json",
      "extenders/agent_gopher/config.json"
    ],
    "access_token_live_hours": 12,
    "refresh_token_live_hours": 168
  },
  "ServerResponse": {
    "status": 404,
    "headers": {
      "Content-Type": "text/html; charset=UTF-8",
      "Server": "AdaptixC2",
      "Adaptix Version": "v0.9"
    },
    "page": "404page.html"
  },
  "EventCallback": {
    "Telegram": {
      "token": "",
      "chats_id": []
    },
    "Webhooks": [
      {
      }
    ],
    "new_agent_message": "New agent: %type% (%id%)\\n\\n%user% @ %computer% (%internalip%)\\nelevated: %elevated%\\nfrom: %externalip%\\ndomain: %domain%",
    "new_cred_message": "New secret [%type%]:\\n\\n%username% : %password% (%domain%)\\n\\nStorage: %storage%\\nHost: %host%",
    "new_download_message": "File saved: %path% [%size%] from %computer% (%user%)"
  }
}
EOF

# Update the port in the new profile
sed -i "s/\"port\": 10000/\"port\": $PORT/g" /app/profile_render.json

# Start the server using the new profile
echo "Starting server with HTTP configuration..."
exec /app/adaptixserver -profile /app/profile_render.json