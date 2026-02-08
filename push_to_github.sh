#!/bin/bash

# Script to push project to GitHub
# Usage: ./push_to_github.sh YOUR_USERNAME REPO_NAME

set -e

if [ $# -lt 2 ]; then
    echo "Usage: ./push_to_github.sh YOUR_USERNAME REPO_NAME"
    echo ""
    echo "Example: ./push_to_github.sh johndoe placement-readiness-analytics"
    echo ""
    echo "First, create a new repository on GitHub.com:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: REPO_NAME"
    echo "3. Description: 'University Placement Readiness Analytics Dashboard'"
    echo "4. Choose Public or Private"
    echo "5. DO NOT initialize with README, .gitignore, or license"
    echo "6. Click 'Create repository'"
    echo ""
    exit 1
fi

USERNAME=$1
REPO_NAME=$2

echo "=========================================="
echo "Pushing to GitHub"
echo "=========================================="
echo ""
echo "Repository: https://github.com/$USERNAME/$REPO_NAME"
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote get-url origin
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "https://github.com/$USERNAME/$REPO_NAME.git"
    else
        echo "Keeping existing remote. Exiting."
        exit 1
    fi
else
    echo "Adding remote repository..."
    git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"
fi

# Ensure we're on main branch
echo ""
echo "Ensuring we're on 'main' branch..."
git branch -M main

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
echo "This may take a moment..."
git push -u origin main

echo ""
echo "=========================================="
echo "✅ Successfully pushed to GitHub!"
echo "=========================================="
echo ""
echo "Repository URL: https://github.com/$USERNAME/$REPO_NAME"
echo ""
echo "Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add a description and topics"
echo "3. Consider adding a LICENSE file"
echo "4. Update README.md if needed"
echo ""

