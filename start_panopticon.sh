#!/bin/bash
# Kill any existing processes
kill $(lsof -t -i:8000) 2>/dev/null

# Export paths
export PATH=$PATH:/home/ubuntu/.local/bin
export PYTHONPATH=$PYTHONPATH:.

# Start API in background
echo "Starting Panopticon API..."
uvicorn panopticon.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
API_PID=$!

# Wait for API to start
sleep 3

# Check if API is running
if kill -0 $API_PID; then
    echo "API is running (PID: $API_PID)"
    echo "Access at: http://localhost:8000"
    echo "Docs at: http://localhost:8000/docs"
else
    echo "API failed to start. Check api.log"
    exit 1
fi

# Start Crawler in background
echo "Starting Continuous Ingestion Crawler..."
python3 panopticon/ingestion/crawlers/mock_crawler.py --continuous --delay 3.0 > crawler.log 2>&1 &
CRAWLER_PID=$!

echo "Crawler running (PID: $CRAWLER_PID). Logging to crawler.log"
echo "System fully operational."
