#!/bin/bash

echo "🔍 Monitoring CORS Fix Deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing: https://tco-laugh.vercel.app → https://panopticon-api-847835.onrender.com"
echo ""

while true; do
    # Test CORS with your domain
    RESPONSE=$(curl -s -X GET "https://panopticon-api-847835.onrender.com/stats" \
        -H "Origin: https://tco-laugh.vercel.app" \
        -H "X-API-Key: pano_bb0712a94164f6df7e4a4741348955bf_2024" \
        -H "Accept: application/json" \
        -w "\nHTTP_CODE:%{http_code}\nCORS_HEADER:%{header_json}" \
        -D - 2>/dev/null)
    
    # Check if Access-Control-Allow-Origin is present
    if echo "$RESPONSE" | grep -q "access-control-allow-origin: https://tco-laugh.vercel.app"; then
        echo ""
        echo "✅✅✅ SUCCESS! CORS IS FIXED! ✅✅✅"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$(date '+%H:%M:%S') - CORS header detected!"
        echo ""
        echo "API Response:"
        curl -s -X GET "https://panopticon-api-847835.onrender.com/stats" \
            -H "Origin: https://tco-laugh.vercel.app" \
            -H "X-API-Key: pano_bb0712a94164f6df7e4a4741348955bf_2024" | python3 -m json.tool
        echo ""
        echo "🎉 Your dashboard should now work at:"
        echo "   https://tco-laugh.vercel.app"
        echo ""
        echo "Use these credentials:"
        echo "   API URL: https://panopticon-api-847835.onrender.com"
        echo "   API Key: pano_bb0712a94164f6df7e4a4741348955bf_2024"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        break
    else
        # Check deployment status
        STATUS=$(curl -s -H "Authorization: Bearer rnd_rmhLllGMj9OYUVzWjCdiTEF4pglh" \
            "https://api.render.com/v1/services/srv-d4h30a3uibrs73dbtiig/deploys?limit=1" | \
            python3 -c "import json,sys; print(json.load(sys.stdin)[0]['deploy']['status'])" 2>/dev/null || echo "unknown")
        
        echo -ne "\r$(date '+%H:%M:%S') - Deployment: $STATUS | CORS: ❌ Not fixed yet (waiting...)"
    fi
    
    sleep 3
done