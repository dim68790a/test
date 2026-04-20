
curl http://127.0.0.1:5003/invocations \
  -H "Content-Type: application/json" \
  --data '{
    "inputs": [[3.5, 25.0, 5.5, 1.0, 500.0, 2.5, 34.5, -118.5]]
  }'
