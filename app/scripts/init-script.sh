#!/bin/bash

# Ustawienie maksymalnego czasu oczekiwania (np. 300 sekund)
MAX_WAIT=300
WAIT_INTERVAL=5
TOTAL_WAIT=0

# Pętla sprawdzająca dostępność adresu IP
until [ -n "$(kubectl get svc fb-poster-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')" ] || [ "$TOTAL_WAIT" -ge "$MAX_WAIT" ]; do
  echo "Oczekiwanie na dostępność adresu IP... ($TOTAL_WAIT/$MAX_WAIT)"
  sleep $WAIT_INTERVAL
  TOTAL_WAIT=$((TOTAL_WAIT+WAIT_INTERVAL))
done

# Sprawdzenie, czy adres IP jest dostępny
if [ "$TOTAL_WAIT" -lt "$MAX_WAIT" ]; then
  echo "Adres IP jest dostępny."
  kubectl get svc fb-poster-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' > /tmp/adres-ip
else
  echo "Przekroczono maksymalny czas oczekiwania. Adres IP nie jest dostępny."
  exit 1
fi
