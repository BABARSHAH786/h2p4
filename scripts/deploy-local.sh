#!/bin/bash
# Deploy Todo App to Minikube (Local Development)

set -e

echo "🚀 Starting Minikube deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v minikube >/dev/null 2>&1 || { echo -e "${RED}minikube is not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl is not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}helm is not installed${NC}"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo -e "${RED}dapr CLI is not installed${NC}"; exit 1; }

# Start Minikube if not running
if ! minikube status >/dev/null 2>&1; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo -e "${GREEN}Minikube is already running${NC}"
fi

# Enable required addons
echo -e "${YELLOW}Enabling Minikube addons...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server

# Install Dapr on Kubernetes
echo -e "${YELLOW}Installing Dapr...${NC}"
if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
    dapr init -k
    kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s
else
    echo -e "${GREEN}Dapr is already installed${NC}"
fi

# Install Strimzi Kafka Operator
echo -e "${YELLOW}Installing Kafka (Strimzi)...${NC}"
if ! kubectl get namespace kafka >/dev/null 2>&1; then
    kubectl create namespace kafka
    kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
    kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
else
    echo -e "${GREEN}Kafka namespace already exists${NC}"
fi

# Deploy Kafka cluster
echo -e "${YELLOW}Deploying Kafka cluster...${NC}"
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
echo "Waiting for Kafka to be ready (this may take 2-3 minutes)..."
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=300s -n kafka || true

# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"
eval $(minikube docker-env)

echo "Building chat-api..."
docker build -t chat-api:latest -f backend/Dockerfile backend/

echo "Building recurring-task-service..."
docker build -t recurring-task-service:latest -f backend/services/recurring_task_service/Dockerfile backend/

echo "Building notification-service..."
docker build -t notification-service:latest -f backend/services/notification_service/Dockerfile backend/

echo "Building frontend..."
docker build -t frontend:latest -f frontend/Dockerfile frontend/

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Deploy Dapr components
echo -e "${YELLOW}Deploying Dapr components...${NC}"
kubectl apply -f k8s/base/dapr-components/ -n todo-app

# Deploy application with Helm
echo -e "${YELLOW}Deploying application with Helm...${NC}"
helm upgrade --install todo-app-local ./helm \
    -f ./helm/values-local.yaml \
    --set secrets.databaseUrl="${DATABASE_URL}" \
    --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
    --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}" \
    --namespace todo-app \
    --wait \
    --timeout 10m

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=chat-api -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=recurring-task-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=300s

# Get service URL
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Access the application:"
echo "  Frontend: $(minikube service frontend -n todo-app --url)"
echo ""
echo "View pods:"
echo "  kubectl get pods -n todo-app"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/chat-api -n todo-app -c chat-api"
echo ""
echo "Port forward (alternative access):"
echo "  kubectl port-forward svc/frontend 3000:3000 -n todo-app"
