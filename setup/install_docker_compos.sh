#!/bin/bash

# Define the Docker Compose version to install
DOCKER_COMPOSE_VERSION="2.26.1"

# Download URL for the binary
DOCKER_COMPOSE_URL="https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"

# Installation directory
INSTALL_DIR="/usr/local/bin"

# Binary path
BINARY_PATH="${INSTALL_DIR}/docker-compose"

echo "Installing Docker Compose version ${DOCKER_COMPOSE_VERSION}..."

# Step 1: Download Docker Compose binary
if curl -L "${DOCKER_COMPOSE_URL}" -o "${BINARY_PATH}"; then
    echo "Docker Compose binary downloaded successfully."
else
    echo "Failed to download Docker Compose binary. Please check your network or the version specified."
    exit 1
fi

# Step 2: Make the binary executable
if chmod +x "${BINARY_PATH}"; then
    echo "Docker Compose binary made executable."
else
    echo "Failed to set execute permissions on Docker Compose binary."
    exit 1
fi

# Step 3: Verify the installation
if "${BINARY_PATH}" --version; then
    echo "Docker Compose installed successfully."
else
    echo "Failed to verify Docker Compose installation."
    exit 1
fi

# Step 4: Provide user instructions
echo "Docker Compose is now installed and available as 'docker-compose'."
echo "You can use 'docker-compose --version' to verify the installation."
