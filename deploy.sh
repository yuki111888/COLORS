#!/bin/bash
set -e

# Deploy static files to web directory
echo "Deploying COLORS app to /var/www/incinerator.xyz/colors..."

# Ensure directory exists
sudo mkdir -p /var/www/incinerator.xyz/colors

# Clear the destination
sudo rm -rf /var/www/incinerator.xyz/colors/*

# Copy all files except hidden files/directories and git
find . -maxdepth 1 -type f ! -name ".*" ! -name "deploy.sh" ! -name "generate_palette.py" -exec sudo cp {} /var/www/incinerator.xyz/colors/ \;

# Set proper permissions
sudo chown -R www-data:www-data /var/www/incinerator.xyz/colors

echo "Deployment complete!"

