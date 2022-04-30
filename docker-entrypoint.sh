#!/usr/bin/env bash

case "$1" in
    "help")
        echo "Please use of next parameters to start: "
        echo "  > test-webserver: Starting test webserver"
        echo "  > webserver: Start webserver"
        echo "  > bash: Start bash shell"
        ;;
    "bash")
        echo "Starting bash..."
        exec bash
        ;;

    "test-webserver")
        echo "Starting test webserver..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;

    "webserver")
        echo "Starting webserver..."
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    *)
        echo "Unknown command '$1'. please use one of: [test-webserver, webserver, bash, help]"
        exit 1
        ;;
esac
