#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Navigate to the project root directory
cd $(dirname "$0")/..

# Navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Install required frontend packages
npm install @radix-ui/react-toast @radix-ui/react-select class-variance-authority lucide-react

# Build the frontend project
npm run build

# Start the frontend development server
npm run dev &

# Navigate back to the project root directory
cd ..

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python main.py