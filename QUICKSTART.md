# Quick Start Guide - Phase V Deployment

## 🚀 5-Minute Local Deployment

### Prerequisites Check
```bash
# Verify installations
minikube version  # Should be v1.32+
kubectl version --client  # Should be v1.28+
helm version  # Should be v3.14+
dapr version  # Should be v1.14+
docker --version
```

### Step 1: Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Step 2: Set Environment Variables
```bash
export DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
export OPENAI_API_KEY="sk-..."
export BETTER_AUTH_SECRET="your-secret-key-min-32-chars"
```

### Step 3: Deploy Everything
```bash
chmod +x scripts/deploy-local.sh
./scripts/deploy-local.sh
```

**This script will:**
- ✅ Install Dapr on Kubernetes
- ✅ Install Kafka (Strimzi operator)
- ✅ Build all 4 Docker images
- ✅ Deploy Dapr components
- ✅ Deploy application via Helm
- ✅ Wait for all pods to be ready

### Step 4: Access Application
```bash
# Get URL
minikube service frontend -n todo-app --url

# Or port forward
kubectl port-forward svc/frontend 3000:3000 -n todo-app
```

Visit: http://localhost:3000

---

## 🌐 Cloud Deployment (15 Minutes)

### Step 1: Provision Kubernetes Cluster

**Oracle Cloud (OKE):**
```bash
# Via OCI Console: Container Engine for Kubernetes
# - Create cluster with 3 worker nodes (2 vCPU, 4GB RAM each)
# - Download kubeconfig

oci ce cluster create-kubeconfig --cluster-id <ocid>
export KUBECONFIG=~/.kube/config-oke
```

**Google Cloud (GKE):**
```bash
gcloud container clusters create todo-cluster \
  --num-nodes=3 \
  --machine-type=e2-standard-2 \
  --zone=us-central1-a

gcloud container clusters get-credentials todo-cluster
```

**Azure (AKS):**
```bash
az aks create \
  --resource-group todo-rg \
  --name todo-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3

az aks get-credentials --resource-group todo-rg --name todo-cluster
```

### Step 2: Set Environment Variables
```bash
export DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
export OPENAI_API_KEY="sk-..."
export BETTER_AUTH_SECRET="your-production-secret"
export EMAIL_API_KEY="your-sendgrid-key"  # Optional
export IMAGE_TAG="latest"
```

### Step 3: Deploy to Cloud
```bash
chmod +x scripts/deploy-cloud.sh
./scripts/deploy-cloud.sh
```

**This script will:**
- ✅ Install Dapr on Kubernetes
- ✅ Install Kafka (Strimzi operator)
- ✅ Install cert-manager for TLS
- ✅ Deploy Kafka cluster (3 replicas)
- ✅ Deploy Dapr components
- ✅ Deploy application via Helm
- ✅ Configure ingress with TLS

### Step 4: Configure DNS
```bash
# Get ingress IP
kubectl get ingress -n todo-app

# Add DNS A record:
# todo.yourdomain.com → <INGRESS_IP>
```

### Step 5: Access Application
Visit: https://todo.yourdomain.com

---

## 🔍 Verify Deployment

### Check Health
```bash
chmod +x scripts/check-health.sh
./scripts/check-health.sh
```

### View Pods
```bash
kubectl get pods -n todo-app
```

Expected output:
```
NAME                                      READY   STATUS    RESTARTS   AGE
chat-api-xxx                              2/2     Running   0          2m
recurring-task-service-xxx                2/2     Running   0          2m
notification-service-xxx                  2/2     Running   0          2m
frontend-xxx                              2/2     Running   0          2m
```

### View Logs
```bash
# Chat API
kubectl logs -f deployment/chat-api -n todo-app -c chat-api

# All services
kubectl logs -f deployment/chat-api -n todo-app -c chat-api &
kubectl logs -f deployment/recurring-task-service -n todo-app -c recurring-task-service &
kubectl logs -f deployment/notification-service -n todo-app -c notification-service &
```

### Test Kafka
```bash
# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Expected: task-events, reminders, task-updates
```

---

## 🧪 Test Features

### 1. Create Task with Priority
```
User: "Add a task: Client presentation, high priority, due Friday 3 PM"
```

### 2. Filter by Priority
```
User: "Show me all high priority tasks"
```

### 3. Search Tasks
```
User: "Find tasks about presentation"
```

### 4. Create Recurring Task
```
User: "Add weekly team standup every Monday at 10 AM"
```

### 5. Complete Recurring Task
```
User: "Mark team standup as complete"
# Wait 5 seconds, then check for next occurrence
User: "Show me my tasks"
```

---

## 🧹 Cleanup

### Local (Minikube)
```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

### Cloud
```bash
./scripts/cleanup.sh

# Then delete cluster:
# OKE: oci ce cluster delete --cluster-id <ocid>
# GKE: gcloud container clusters delete todo-cluster
# AKS: az aks delete --resource-group todo-rg --name todo-cluster
```

---

## 🆘 Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app -c <container-name>
```

### Kafka Issues
```bash
kubectl get kafka -n kafka
kubectl logs -f kafka-cluster-kafka-0 -n kafka
```

### Database Connection
```bash
kubectl get secret app-secrets -n todo-app -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Dapr Issues
```bash
kubectl get pods -n dapr-system
kubectl logs -f deployment/chat-api -n todo-app -c daprd
```

---

## 📚 Next Steps

1. **Configure CI/CD**: Set up GitHub Actions for automated deployments
2. **Add Monitoring**: Install Prometheus + Grafana
3. **Configure Alerts**: Set up alerting for critical issues
4. **Load Testing**: Test with multiple concurrent users
5. **Backup Strategy**: Configure database backups

---

## 🎯 Success Criteria

- ✅ All pods running (2/2 READY)
- ✅ Health checks passing
- ✅ Kafka topics created
- ✅ Frontend accessible
- ✅ Can create/list/search tasks
- ✅ Events published to Kafka
- ✅ HPA configured (production)
- ✅ Ingress with TLS (production)
