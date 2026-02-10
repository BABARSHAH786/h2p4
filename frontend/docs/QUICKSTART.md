# Kubernetes Deployment Quickstart Guide

Get the Todo Chatbot application running on Kubernetes in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Docker Desktop 4.53+** installed and running
- ✅ **Minikube 1.32+** installed
- ✅ **kubectl 1.28+** installed
- ✅ **Helm 3.13+** installed
- ✅ **4 CPU cores and 8GB RAM** available for Minikube
- ✅ **OpenAI API key** (for chatbot functionality)
- ✅ **Database URL** (Neon PostgreSQL or other)

### Installation Links

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)

## Quick Start (Automated)

### Option 1: One-Command Deployment

```bash
# Set your secrets as environment variables
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
export BETTER_AUTH_SECRET="your-secret-key"
export OPENAI_API_KEY="sk-your-openai-key"

# Run the complete deployment script
./scripts/deploy-all.sh
```

This script will:
1. ✅ Check prerequisites
2. ✅ Start Minikube
3. ✅ Build Docker images
4. ✅ Load images to Minikube
5. ✅ Deploy application with Helm
6. ✅ Display access information

**Access the application:**
```bash
minikube service frontend-service -n todo-app
```

---

## Manual Deployment (Step-by-Step)

### Step 1: Start Minikube

```bash
# Start Minikube with required resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
```

### Step 2: Build Docker Images

```bash
# Build frontend image
cd frontend
docker build -t todo-frontend:1.0.0 .
cd ..

# Build backend image
cd backend
docker build -t todo-backend:1.0.0 .
cd ..

# Verify images
docker images | grep todo
```

**Expected output:**
```
todo-frontend   1.0.0   abc123   2 minutes ago   85MB
todo-backend    1.0.0   def456   3 minutes ago   180MB
```

### Step 3: Load Images to Minikube

```bash
# Load frontend image
minikube image load todo-frontend:1.0.0

# Load backend image
minikube image load todo-backend:1.0.0

# Verify images in Minikube
minikube image ls | grep todo
```

### Step 4: Prepare Secrets

```bash
# Set your actual values
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
export BETTER_AUTH_SECRET="your-secret-key"
export OPENAI_API_KEY="sk-your-openai-key"

# Encode to base64
export DATABASE_URL_B64=$(echo -n "$DATABASE_URL" | base64)
export BETTER_AUTH_SECRET_B64=$(echo -n "$BETTER_AUTH_SECRET" | base64)
export OPENAI_API_KEY_B64=$(echo -n "$OPENAI_API_KEY" | base64)
```

### Step 5: Deploy with Helm

```bash
# Install the application
helm install todo-app-local ./k8s/helm-chart \
  --create-namespace \
  --namespace todo-app \
  --set secrets.databaseUrl="$DATABASE_URL_B64" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET_B64" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY_B64"

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n todo-app --timeout=120s
```

### Step 6: Verify Deployment

```bash
# Check pod status
kubectl get pods -n todo-app

# Expected output:
# NAME                                   READY   STATUS    RESTARTS   AGE
# backend-deployment-xxx-yyy             1/1     Running   0          2m
# backend-deployment-xxx-zzz             1/1     Running   0          2m
# frontend-deployment-aaa-bbb            1/1     Running   0          2m
# frontend-deployment-aaa-ccc            1/1     Running   0          2m

# Check services
kubectl get svc -n todo-app

# Expected output:
# NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
# backend-service    ClusterIP   10.96.1.1       <none>        8000/TCP         2m
# frontend-service   NodePort    10.96.1.2       <none>        3000:30080/TCP   2m
```

### Step 7: Access the Application

```bash
# Option 1: Open in browser automatically
minikube service frontend-service -n todo-app

# Option 2: Get URL and open manually
minikube service frontend-service -n todo-app --url
# Then open the URL in your browser
```

---

## Verification Checklist

After deployment, verify everything works:

- [ ] **Frontend accessible**: Can open the application in browser
- [ ] **User signup**: Can create a new account
- [ ] **Task management**: Can add, complete, and delete tasks
- [ ] **Chatbot**: Can interact with AI chatbot to manage tasks
- [ ] **Data persistence**: Tasks remain after page refresh

---

## Common Operations

### View Logs

```bash
# Frontend logs
kubectl logs -f deployment/frontend-deployment -n todo-app

# Backend logs
kubectl logs -f deployment/backend-deployment -n todo-app

# All backend pods
kubectl logs -l app=backend -n todo-app --tail=50
```

### Scale Application

```bash
# Scale backend to 4 replicas
kubectl scale deployment backend-deployment --replicas=4 -n todo-app

# Scale frontend to 3 replicas
kubectl scale deployment frontend-deployment --replicas=3 -n todo-app

# Verify scaling
kubectl get pods -n todo-app
```

### Update Configuration

```bash
# Update backend configuration
kubectl edit configmap backend-config -n todo-app

# Restart pods to pick up changes
kubectl rollout restart deployment/backend-deployment -n todo-app

# Monitor rollout
kubectl rollout status deployment/backend-deployment -n todo-app
```

### Monitor Resources

```bash
# Pod resource usage
kubectl top pods -n todo-app

# Node resource usage
kubectl top nodes

# Open Kubernetes dashboard
minikube dashboard
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for details
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app
```

### Image Pull Errors

```bash
# Verify images are loaded in Minikube
minikube image ls | grep todo

# If missing, load them
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0
```

### Cannot Access Application

```bash
# Get Minikube IP
minikube ip

# Get service URL
minikube service frontend-service -n todo-app --url

# Check service status
kubectl get svc -n todo-app
kubectl describe svc frontend-service -n todo-app
```

### Database Connection Issues

```bash
# Check backend logs for errors
kubectl logs -l app=backend -n todo-app --tail=100

# Verify secrets are set
kubectl get secret app-secrets -n todo-app -o yaml

# Test database connectivity from pod
kubectl exec -it <backend-pod> -n todo-app -- \
  python -c "import os; print(os.getenv('DATABASE_URL'))"
```

For more troubleshooting, see [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)

---

## Cleanup

### Remove Application

```bash
# Uninstall Helm release
helm uninstall todo-app-local -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

### Stop Minikube

```bash
# Stop Minikube (preserves cluster)
minikube stop

# Delete Minikube cluster (removes everything)
minikube delete
```

---

## Next Steps

- 📖 **Architecture**: Learn about the system design in [ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- 🔧 **Troubleshooting**: Detailed solutions in [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
- 📦 **Helm Chart**: Advanced configuration in [helm-chart/README.md](../k8s/helm-chart/README.md)
- 🚀 **Scaling**: Test horizontal scaling and rolling updates
- 📊 **Monitoring**: Explore Kubernetes dashboard and metrics

---

## Advanced Topics

### Using Custom Values

Create `custom-values.yaml`:
```yaml
frontend:
  replicaCount: 3
backend:
  replicaCount: 4
  config:
    agentModel: "gpt-4o"
```

Deploy with custom values:
```bash
helm install todo-app-local ./k8s/helm-chart \
  -f custom-values.yaml \
  --set secrets.databaseUrl="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.openaiApiKey="..."
```

### Rolling Updates

```bash
# Update image tag in values.yaml
# Then upgrade
helm upgrade todo-app-local ./k8s/helm-chart

# Monitor rollout
kubectl rollout status deployment/backend-deployment -n todo-app

# Rollback if needed
helm rollback todo-app-local -n todo-app
```

### In-Cluster Database

To use in-cluster PostgreSQL instead of external Neon:

```bash
helm install todo-app-local ./k8s/helm-chart \
  --set database.enabled=true \
  --set database.persistence.enabled=true \
  --set secrets.databaseUrl="<postgres-connection-string>"
```

---

## Performance Benchmarks

**Deployment Time**: < 5 minutes from start to operational
**Container Startup**: < 60 seconds per service
**Scaling Time**: < 60 seconds with zero downtime
**Rolling Update**: < 2 minutes with zero downtime

**Resource Usage** (baseline 2+2 replicas):
- CPU: ~1.3 cores (requests), ~5 cores (limits)
- Memory: ~1.5Gi (requests), ~5.5Gi (limits)

---

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
2. Review [ARCHITECTURE.md](../docs/ARCHITECTURE.md)
3. Consult [Helm Chart README](../k8s/helm-chart/README.md)
4. Check Kubernetes logs and events

---

**🎉 Congratulations!** You now have a production-ready Kubernetes deployment of the Todo Chatbot application!
