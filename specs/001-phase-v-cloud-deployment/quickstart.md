# Quickstart Guide - Phase V Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-02-10
**Status**: Complete

## Overview

This guide provides step-by-step instructions for deploying the Phase V Todo Chatbot with microservices, event-driven architecture, and cloud deployment.

## Prerequisites

### Required Software

**Local Development**:
- Docker Desktop (latest)
- Minikube (v1.32+)
- kubectl (v1.28+)
- Helm (v3.14+)
- Dapr CLI (v1.14+)
- Python 3.13+
- Node.js 20+
- Git

**Cloud Deployment** (choose one):
- Oracle Cloud account (OKE)
- Google Cloud account (GKE)
- Azure account (AKS)

### Installation Commands

```bash
# Install Minikube (macOS)
brew install minikube

# Install kubectl
brew install kubectl

# Install Helm
brew install helm

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify installations
minikube version
kubectl version --client
helm version
dapr version
```

---

## Part 1: Local Development Setup (Minikube)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
```

### Step 2: Install Dapr on Kubernetes

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system

# Expected output:
# dapr-operator-xxx        1/1     Running
# dapr-placement-server-xxx 1/1     Running
# dapr-sentry-xxx          1/1     Running
# dapr-sidecar-injector-xxx 1/1     Running
```

### Step 3: Install Kafka (Strimzi Operator)

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Wait for Kafka to be ready (takes 2-3 minutes)
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=300s -n kafka

# Verify Kafka is running
kubectl get kafka -n kafka
```

**k8s/kafka/kafka-cluster.yaml**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
spec:
  kafka:
    version: 3.7.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

### Step 4: Create Kafka Topics

```bash
# Create task-events topic
kubectl apply -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
EOF

# Create reminders topic
kubectl apply -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
EOF

# Verify topics
kubectl get kafkatopics -n kafka
```

### Step 5: Set Up Database

```bash
# Create .env file with Neon database URL
cat > backend/.env <<EOF
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
OPENAI_API_KEY=sk-...
BETTER_AUTH_SECRET=your-secret-key
EOF

# Run database migrations
cd backend
uv sync
uv run alembic upgrade head
cd ..
```

### Step 6: Deploy Dapr Components

```bash
# Create todo-app namespace
kubectl create namespace todo-app

# Create secrets
kubectl create secret generic app-secrets \
  --from-env-file=backend/.env \
  -n todo-app

# Deploy Dapr components
kubectl apply -f k8s/base/dapr-components/ -n todo-app

# Verify components
dapr components -k -n todo-app
```

### Step 7: Deploy Services with Helm

```bash
# Install Helm chart
helm install todo-app-local helm/ \
  -f helm/values-local.yaml \
  -n todo-app

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=chat-api -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=recurring-task-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service -n todo-app --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=300s

# Verify all pods are running
kubectl get pods -n todo-app
```

### Step 8: Access the Application

```bash
# Get frontend URL
minikube service frontend -n todo-app --url

# Open in browser
open $(minikube service frontend -n todo-app --url)
```

**Expected Output**:
```
http://127.0.0.1:xxxxx
```

Navigate to this URL in your browser to access the Todo Chatbot.

---

## Part 2: Testing the Application

### Test 1: Create a Task with Priority and Tags

**User Input**:
```
Add a task: Client presentation, high priority, tagged with work and urgent, due Friday 3 PM
```

**Expected Response**:
```
I've created a high priority task "Client presentation" tagged with work and urgent, due Friday at 3 PM. I'll remind you 1 hour before.
```

**Verify in Database**:
```bash
kubectl exec -it deployment/chat-api -n todo-app -- psql $DATABASE_URL -c "SELECT title, priority, tags, due_at FROM tasks ORDER BY created_at DESC LIMIT 1;"
```

### Test 2: List Tasks with Filters

**User Input**:
```
Show me all high priority work tasks
```

**Expected Response**:
```
Here are your high priority work tasks:
1. Client presentation (due Friday 3 PM)
```

### Test 3: Search Tasks

**User Input**:
```
Find tasks about presentation
```

**Expected Response**:
```
I found 1 task matching "presentation":
1. Client presentation (high priority, due Friday 3 PM)
```

### Test 4: Create Recurring Task

**User Input**:
```
Add weekly team standup every Monday at 10 AM
```

**Expected Response**:
```
I've created a recurring task "Team standup" that repeats weekly on Mondays at 10 AM.
```

**Complete the Task**:
```
Mark "Team standup" as complete
```

**Verify Next Occurrence**:
Wait 5 seconds, then:
```
Show me my tasks
```

**Expected**: New "Team standup" task for next Monday should appear.

### Test 5: Verify Event Publishing

**Check Kafka Events**:
```bash
# Consume task-events topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning \
  --max-messages 5
```

**Expected Output**: JSON events for task.created, task.completed, etc.

---

## Part 3: Cloud Deployment (Oracle Cloud - OKE)

### Step 1: Create OKE Cluster

```bash
# Install OCI CLI
brew install oci-cli

# Configure OCI CLI
oci setup config

# Create OKE cluster (via OCI Console or CLI)
# - 3 worker nodes
# - 2 vCPU, 4GB RAM per node
# - Kubernetes 1.28+

# Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file ~/.kube/config-oke \
  --region us-ashburn-1

# Set context
export KUBECONFIG=~/.kube/config-oke
kubectl config use-context <oke-context>

# Verify cluster
kubectl get nodes
```

### Step 2: Install Dapr on OKE

```bash
# Initialize Dapr
dapr init -k

# Verify
kubectl get pods -n dapr-system
```

### Step 3: Install Kafka on OKE

**Option A: Strimzi (Self-Hosted)**:
```bash
# Same as local setup, but with replicas=3
kubectl create namespace kafka
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f k8s/kafka/kafka-cluster-production.yaml -n kafka
```

**Option B: Redpanda Cloud (Managed)**:
```bash
# Sign up at https://redpanda.com/redpanda-cloud
# Create serverless cluster (free tier)
# Get bootstrap servers URL
# Update Dapr Pub/Sub component with Redpanda URL
```

### Step 4: Deploy Application

```bash
# Create namespace
kubectl create namespace todo-app

# Create secrets
kubectl create secret generic app-secrets \
  --from-env-file=.env.production \
  -n todo-app

# Deploy Dapr components
kubectl apply -f k8s/base/dapr-components/ -n todo-app

# Deploy with Helm
helm install todo-app helm/ \
  -f helm/values-production.yaml \
  -n todo-app

# Wait for pods
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=600s

# Verify deployment
kubectl get pods -n todo-app
kubectl get ingress -n todo-app
```

### Step 5: Configure DNS and TLS

```bash
# Get LoadBalancer IP
kubectl get ingress -n todo-app

# Configure DNS A record
# your-domain.com → <LoadBalancer-IP>

# Install cert-manager for TLS
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f k8s/base/cert-manager/cluster-issuer.yaml

# Update ingress with TLS
kubectl apply -f k8s/base/frontend/ingress-tls.yaml -n todo-app
```

### Step 6: Verify Production Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check HPA is configured
kubectl get hpa -n todo-app

# Test application
curl https://your-domain.com/health/ready

# Access application
open https://your-domain.com
```

---

## Part 4: CI/CD Setup (GitHub Actions)

### Step 1: Configure GitHub Secrets

Navigate to GitHub repository → Settings → Secrets and variables → Actions

**Add Secrets**:
- `KUBECONFIG`: Base64-encoded kubeconfig file
- `DATABASE_URL`: Neon PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `BETTER_AUTH_SECRET`: Better Auth secret key

```bash
# Encode kubeconfig
cat ~/.kube/config-oke | base64
```

### Step 2: Create GitHub Actions Workflow

File: `.github/workflows/ci-cd.yaml` (already created in plan.md)

### Step 3: Test CI/CD Pipeline

```bash
# Make a change
echo "# Test change" >> README.md

# Commit and push
git add .
git commit -m "Test CI/CD pipeline"
git push origin main

# Monitor workflow
# Go to GitHub → Actions tab
# Watch pipeline execute: lint → test → build → push → deploy
```

---

## Part 5: Monitoring and Troubleshooting

### View Logs

```bash
# Chat API logs
kubectl logs -f deployment/chat-api -n todo-app -c chat-api

# Recurring Task Service logs
kubectl logs -f deployment/recurring-task-service -n todo-app -c recurring-task-service

# Notification Service logs
kubectl logs -f deployment/notification-service -n todo-app -c notification-service

# Dapr sidecar logs
kubectl logs -f deployment/chat-api -n todo-app -c daprd
```

### Check Health

```bash
# All services
kubectl get pods -n todo-app

# Health checks
kubectl exec -it deployment/chat-api -n todo-app -- curl localhost:8000/health/ready
```

### Debug Kafka

```bash
# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Consume events
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

### Common Issues

**Issue**: Pods stuck in Pending state
```bash
# Check events
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# - Insufficient cluster resources
# - Image pull errors
# - PVC not bound
```

**Issue**: Dapr sidecar not injecting
```bash
# Verify Dapr is installed
kubectl get pods -n dapr-system

# Check deployment annotations
kubectl get deployment chat-api -n todo-app -o yaml | grep dapr.io
```

**Issue**: Kafka connection errors
```bash
# Verify Kafka is running
kubectl get kafka -n kafka

# Check Dapr Pub/Sub component
kubectl describe component pubsub -n todo-app
```

---

## Part 6: Cleanup

### Local (Minikube)

```bash
# Delete Helm release
helm uninstall todo-app-local -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Delete Kafka
kubectl delete namespace kafka

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

### Cloud (OKE)

```bash
# Delete Helm release
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Delete Kafka namespace
kubectl delete namespace kafka

# Delete OKE cluster (via OCI Console or CLI)
oci ce cluster delete --cluster-id <cluster-ocid>
```

---

## Next Steps

1. **Implement Advanced Features**: Add more sophisticated filtering, sorting, and search capabilities
2. **Add Real-Time Sync**: Implement WebSocket service for multi-device sync
3. **Enhance Notifications**: Add push notifications and SMS support
4. **Improve Observability**: Set up Prometheus and Grafana for metrics visualization
5. **Add Audit Service**: Implement comprehensive audit logging
6. **Performance Optimization**: Add caching layer with Redis

---

## Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Strimzi Documentation](https://strimzi.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Oracle Cloud OKE](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [Better Auth Documentation](https://better-auth.com/docs)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)

---

## Support

For issues or questions:
1. Check logs: `kubectl logs -f deployment/<service> -n todo-app`
2. Review events: `kubectl get events -n todo-app --sort-by='.lastTimestamp'`
3. Consult documentation links above
4. Open GitHub issue with logs and error messages

---

**Estimated Setup Time**:
- Local Development: 30-45 minutes
- Cloud Deployment: 60-90 minutes
- CI/CD Setup: 15-30 minutes

**Total**: 2-3 hours for complete Phase V setup
