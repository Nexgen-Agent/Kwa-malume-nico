#!/bin/sh
# Wait for database to be ready (if using PostgreSQL)
# then start the server

exec hypercorn app.main:app --host 0.0.0.0 --port 4000