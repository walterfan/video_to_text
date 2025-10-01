#!/bin/bash

# Create upload directory if it doesn't exist
mkdir -p app/static/uploads

# Set default port
PORT=$1
if [ x${PORT} == x"" ]; then
    PORT=8000
fi

# Set Flask environment variables
export FLASK_APP=app
export FLASK_ENV=development

# Start the Flask app using Poetry
poetry run flask run --debug -p $PORT