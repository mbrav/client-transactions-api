#!/bin/sh

OS_NAME=$(awk -F= '$1=="NAME" { print $2 ;}' /etc/os-release)
OS_VERSION=$(awk -F= '$1=="VERSION" { print $2 ;}' /etc/os-release)
OS_KERNEL=$(uname -mrs)

echo "Stating client transactions api \e[0m"
echo "OS $OS_NAME - $OS_VERSION \e[0m"
echo "Kernel $OS_KERNEL \e[0m"
echo "Port $API_PORT \e[0m"
echo "Host $API_HOST \e[0m"
echo "API Path: $API_PATH \e[0m"

$WORKDIR/.venv/bin/python -m uvicorn --host 0.0.0.0 --port "${API_PORT:-8000}" client_transactions_api.main:app