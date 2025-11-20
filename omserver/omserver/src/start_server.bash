#!/bin/bash
# Start the Flask server using PDM
# Run this script from the src directory: bash start_server.bash
# Or use: pdm run bash start_server.bash

pdm run flask --app omserver --debug run --host=0.0.0.0 --port=5000
