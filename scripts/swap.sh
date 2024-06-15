#!/bin/bash

# Define the swap file size in megabytes (2GB in this case)
SWAP_SIZE=2048

# Create a swap file with the specified size
sudo fallocate -l ${SWAP_SIZE}M /swapfile

# Set appropriate permissions on the swap file
sudo chmod 600 /swapfile

# Mark the file as a swap space
sudo mkswap /swapfile

# Enable the swap file
sudo swapon /swapfile

# Make the swap file permanent by adding it to the /etc/fstab file
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Check if the swap space has been added successfully
echo "Swap space of 2GB has been added:"
free -h

# Verify that the swap is active
swapon --show
