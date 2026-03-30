#!/bin/bash

DURATION=10
RATE=2
ANOMALY=20

for arg in "$@"; do
  case $arg in
    --duration=*) DURATION="${arg#*=}" ;;
    --rate=*) RATE="${arg#*=}" ;;
    --anomaly-chance=*) ANOMALY="${arg#*=}" ;;
  esac
done

echo "Test başladı: $DURATION saniye boyunca, saniyede $RATE istek, %$ANOMALY anomali şansı."

END_TIME=$((SECONDS + DURATION))

while [ $SECONDS -lt $END_TIME ]; do
  for ((i=1; i<=RATE; i++)); do
    USER="user_$((RANDOM % 5 + 1))"
    AMOUNT=$((RANDOM % 100 + 10))
    LOC="City_$((RANDOM % 3 + 1))"

    if [ $((RANDOM % 100)) -lt $ANOMALY ]; then
      AMOUNT=$((AMOUNT * 10))
    fi

    ./scripts/manual-input.sh "$USER" "$AMOUNT" "$LOC" > /dev/null &
  done
  sleep 1
done

echo "Test tamamlandı."
