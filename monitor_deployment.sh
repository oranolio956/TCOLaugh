#!/bin/bash
# Monitor Render deployment status

API_KEY="rnd_rmhLllGMj9OYUVzWjCdiTEF4pglh"
SERVICE_ID="srv-d4h30a3uibrs73dbtiig"
API_URL="https://panopticon-api-847835.onrender.com"

echo "🚀 Monitoring deployment progress..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

while true; do
    # Get deployment status
    STATUS=$(curl -s -H "Authorization: Bearer $API_KEY" \
        "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=1" | \
        python3 -c "import json,sys; d=json.load(sys.stdin)[0]['deploy']; print(d['status'])" 2>/dev/null)
    
    echo -n "$(date '+%H:%M:%S') - Deployment Status: $STATUS"
    
    if [ "$STATUS" == "live" ]; then
        echo " ✅"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 Deployment complete! Testing connection..."
        
        # Test the API
        RESPONSE=$(curl -s -X GET "$API_URL/stats" \
            -H "X-API-Key: pano_bb0712a94164f6df7e4a4741348955bf_2024" \
            -H "Origin: https://tco-laugh.vercel.app" -w "\nHTTP_STATUS:%{http_code}")
        
        HTTP_STATUS=$(echo "$RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
        BODY=$(echo "$RESPONSE" | grep -v HTTP_STATUS)
        
        if [ "$HTTP_STATUS" == "200" ]; then
            echo "✅ API responding correctly!"
            echo "📊 Response: $BODY"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🌐 You can now access the dashboard at:"
            echo "   https://tco-laugh.vercel.app"
            echo ""
            echo "🔑 Use these credentials:"
            echo "   API URL: $API_URL"
            echo "   API Key: pano_bb0712a94164f6df7e4a4741348955bf_2024"
        else
            echo "⚠️  API returned status: $HTTP_STATUS"
            echo "Response: $BODY"
        fi
        break
    elif [ "$STATUS" == "failed" ]; then
        echo " ❌"
        echo "Deployment failed! Check Render dashboard for details."
        break
    else
        echo ""
    fi
    
    sleep 5
done