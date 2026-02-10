#!/bin/bash
# Deploy Todo App to Cloud Kubernetes (OKE/GKE/AKS)

set -e

echo "🚀 Starting cloud deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl is not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}helm is not installed${NC}"; exit 1; }

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}DATABASE_URL environment variable is not set${NC}"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}OPENAI_API_KEY environment variable is not set${NC}"
    exit 1
fi

if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo -e "${RED}BETTER_AUTH_SECRET environment variable is not set${NC}"
    exit 1
fi

# Verify kubectl context
echo -e "${YELLOW}Current kubectl context:${NC}"
kubectl config current-context

read -p "Is this the correct cluster? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 1
fi

# Install Dapr on Kubernetes
echo -e "${YELLOW}Installing Dapr...${NC}"
if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update
    helm upgrade --install dapr dapr/dapr \
        --version=1.14 \
        --namespace dapr-system \
        --create-namespace \
        --wait
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

# Deploy Kafka cluster (production configuration)
echo -e "${YELLOW}Deploying Kafka cluster...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.7.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: persistent-claim
      size: 100Gi
      class: standard
    resources:
      requests:
        memory: 1Gi
        cpu: 1000m
      limits:
        memory: 2Gi
        cpu: 2000m
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      class: standard
    resources:
      requests:
        memory: 512Mi
        cpu: 500m
      limits:
        memory: 1Gi
        cpu: 1000m
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

echo "Waiting for Kafka to be ready (this may take 5-10 minutes)..."
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka || true

# Deploy Kafka topics
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Install cert-manager for TLS
echo -e "${YELLOW}Installing cert-manager...${NC}"
if ! kubectl get namespace cert-manager >/dev/null 2>&1; then
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
else
    echo -e "${GREEN}cert-manager is already installed${NC}"
fi

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Deploy Dapr components
echo -e "${YELLOW}Deploying Dapr components...${NC}"
kubectl apply -f k8s/base/dapr-components/ -n todo-app

# Deploy application with Helm
echo -e "${YELLOW}Deploying application with Helm...${NC}"
IMAGE_TAG=${IMAGE_TAG:-latest}

helm upgrade --install todo-app ./helm \
    -f ./helm/values-production.yaml \
    --set chatApi.image.tag="${IMAGE_TAG}" \
    --set recurringTaskService.image.tag="${IMAGE_TAG}" \
    --set notificationService.image.tag="${IMAGE_TAG}" \
    --set frontend.image.tag="${IMAGE_TAG}" \
    --set secrets.databaseUrl="${DATABASE_URL}" \
    --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
    --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}" \
    --set secrets.emailApiKey="${EMAIL_API_KEY:-}" \
    --namespace todo-app \
    --wait \
    --timeout 15m

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=chat-api -n todo-app --timeout=600s
kubectl wait --for=condition=ready pod -l app=recurring-task-service -n todo-app --timeout=600s
kubectl wait --for=condition=ready pod -l app=notification-service -n todo-app --timeout=600s
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=600s

# Get ingress URL
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Application URLs:"
INGRESS_HOST=$(kubectl get ingress frontend-ingress -n todo-app -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "Not configured")
echo "  Frontend: https://${INGRESS_HOST}"
echo ""
echo "View pods:"
echo "  kubectl get pods -n todo-app"
echo ""
echo "View HPA status:"
echo "  kubectl get hpa -n todo-app"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/chat-api -n todo-app -c chat-api"
