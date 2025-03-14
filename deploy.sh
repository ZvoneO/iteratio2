#!/bin/bash

# Script to help with deploying to Render

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git and try again."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Not in a git repository. Please initialize a git repository first."
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "There are uncommitted changes. Please commit your changes first."
    read -p "Do you want to commit all changes with a message? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_message
        git add .
        git commit -m "$commit_message"
    else
        exit 1
    fi
fi

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Render CLI is not installed."
    read -p "Do you want to deploy without the Render CLI? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please install the Render CLI and try again."
        echo "Visit https://render.com/docs/cli for installation instructions."
        exit 1
    fi
fi

# Push to the remote repository
echo "Pushing to remote repository..."
git push

# If Render CLI is installed, deploy using the CLI
if command -v render &> /dev/null; then
    echo "Deploying to Render using CLI..."
    render deploy
else
    echo "Deployment pushed to git. Render will automatically deploy if you have connected your repository."
    echo "Visit https://dashboard.render.com to check the status of your deployment."
fi

echo "Deployment process completed!" 