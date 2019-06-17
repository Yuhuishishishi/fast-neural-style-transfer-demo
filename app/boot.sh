#!/bin/bash
source activate web
exec gunicorn -b :$PORT --access-logfile - --error-logfile - app:app
