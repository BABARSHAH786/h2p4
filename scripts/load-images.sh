#!/bin/bash
# Load Docker images to Minikube

set -e

echo "📤 Loading Docker images to Minikube..."

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Please start it first:"
    echo "   minikube start --cpus=4 --memory=8192"
    exit 1
fi

# Load frontend image
echo "📤 Loading frontend image..."
minikube image load todo-frontend:1.0.0

# Load backend image
echo "📤 Loading backend image..."
minikube image load todo-backend:1.0.0

# Verify images in Minikube
echo ""
echo "✅ Images loaded! Verifying..."
minikube image ls | grep todo

echo ""
echo "✅ Images loaded successfully to Minikube!"
echo "Next step: Deploy to Kubernetes with ./scripts/deploy.sh"
