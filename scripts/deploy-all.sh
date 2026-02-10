#!/bin/bash
# Complete deployment workflow for Todo application

set -e

echo "🚀 Todo Application - Complete Deployment Workflow"
echo "=================================================="
echo ""

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube not found. Please install Minikube."
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found. Please install Helm."
    exit 1
fi

echo "✅ All prerequisites installed"
echo ""

# Step 2: Start Minikube
echo "Step 2: Starting Minikube..."
if minikube status | grep -q "Running"; then
    echo "✅ Minikube already running"
else
    echo "Starting Minikube with 4 CPU and 8GB RAM..."
    minikube start --cpus=4 --memory=8192 --driver=docker

    echo "Enabling addons..."
    minikube addons enable ingress
    minikube addons enable metrics-server
fi
echo ""

# Step 3: Build images
echo "Step 3: Building Docker images..."
./scripts/build-images.sh
echo ""

# Step 4: Load images to Minikube
echo "Step 4: Loading images to Minikube..."
./scripts/load-images.sh
echo ""

# Step 5: Deploy application
echo "Step 5: Deploying application..."
./scripts/deploy.sh
echo ""

# Step 6: Display access information
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "🌐 Access the application:"
echo "   minikube service frontend-service -n todo-app"
echo ""
echo "📊 Monitor resources:"
echo "   kubectl get pods -n todo-app"
echo "   kubectl get svc -n todo-app"
echo "   kubectl logs -f <pod-name> -n todo-app"
echo ""
echo "🎛️  Open Kubernetes Dashboard:"
echo "   minikube dashboard"
echo ""
echo "🧹 Cleanup when done:"
echo "   ./scripts/cleanup.sh"
