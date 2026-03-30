#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Kullanım: $0 <user_id> <amount> <location>"
    exit 1
fi

USER_ID=$1
AMOUNT=$2
LOCATION=$3

curl -s -X POST "http://localhost:8000/transactions" \
     -H "Content-Type: application/json" \
     -d "{\"user_id\": \"$USER_ID\", \"amount\": $AMOUNT, \"location\": \"$LOCATION\"}" | jq . || echo "İstek gönderildi."
