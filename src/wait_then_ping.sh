#!/bin/bash

echo "Sleeping..."
sleep 100

echo "Pinging..."
ping ${MASTER_ADDR}
