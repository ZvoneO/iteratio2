#!/bin/bash

# Script to help with local Docker development

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Function to display help
show_help() {
    echo "Usage: ./docker-dev.sh [OPTION]"
    echo "Options:"
    echo "  start       Build and start the Docker containers"
    echo "  stop        Stop the Docker containers"
    echo "  restart     Restart the Docker containers"
    echo "  logs        Show logs from the Docker containers"
    echo "  shell       Open a shell in the web container"
    echo "  help        Show this help message"
}

# Parse command line arguments
case "$1" in
    start)
        echo "Building and starting Docker containers..."
        docker-compose up --build -d
        echo "Docker containers started. Access the application at http://localhost:8080"
        ;;
    stop)
        echo "Stopping Docker containers..."
        docker-compose down
        echo "Docker containers stopped."
        ;;
    restart)
        echo "Restarting Docker containers..."
        docker-compose down
        docker-compose up --build -d
        echo "Docker containers restarted. Access the application at http://localhost:8080"
        ;;
    logs)
        echo "Showing logs from Docker containers..."
        docker-compose logs -f
        ;;
    shell)
        echo "Opening shell in web container..."
        docker-compose exec web bash
        ;;
    help|*)
        show_help
        ;;
esac 