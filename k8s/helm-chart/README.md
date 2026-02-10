# Todo App Helm Chart

A Helm chart for deploying the Todo Chatbot application on Kubernetes.

## Prerequisites

- Kubernetes 1.28+
- Helm 3.13+
- Docker images built and loaded to cluster

## Installation

### Quick Start

1. **Build and load Docker images** (for Minikube):
```bash
# Build images
docker build -t todo-frontend:1.0.0 ./frontend
docker build -t todo-backend:1.0.0 ./backend

# Load to Minikube
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0
```

2. **Prepare secrets**:
```bash
# Encode secrets to base64
echo -n "your-database-url" | base64
echo -n "your-auth-secret" | base64
echo -n "your-openai-key" | base64
```

3. **Install the chart**:
```bash
helm install todo-app-local ./k8s/helm-chart \
  --create-namespace \
  --namespace todo-app \
  --set secrets.databaseUrl="<base64-encoded-db-url>" \
  --set secrets.betterAuthSecret="<base64-encoded-secret>" \
  --set secrets.openaiApiKey="<base64-encoded-key>"
```

### Using Environment Variables

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export BETTER_AUTH_SECRET="your-secret"
export OPENAI_API_KEY="sk-..."

# Encode and install
helm install todo-app-local ./k8s/helm-chart \
  --create-namespace \
  --namespace todo-app \
  --set secrets.databaseUrl="$(echo -n $DATABASE_URL | base64)" \
  --set secrets.betterAuthSecret="$(echo -n $BETTER_AUTH_SECRET | base64)" \
  --set secrets.openaiApiKey="$(echo -n $OPENAI_API_KEY | base64)"
```

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `namespace` | Kubernetes namespace | `todo-app` |
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `1.0.0` |
| `frontend.service.type` | Frontend service type | `NodePort` |
| `frontend.service.nodePort` | NodePort for frontend | `30080` |
| `backend.replicaCount` | Number of backend replicas | `2` |
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `1.0.0` |
| `backend.config.agentModel` | AI model to use | `gpt-4o-mini` |
| `database.enabled` | Enable in-cluster PostgreSQL | `false` |
| `secrets.databaseUrl` | Base64 encoded database URL | `""` |
| `secrets.betterAuthSecret` | Base64 encoded auth secret | `""` |
| `secrets.openaiApiKey` | Base64 encoded OpenAI key | `""` |

### Custom Values File

Create a `custom-values.yaml`:

```yaml
frontend:
  replicaCount: 3
  resources:
    requests:
      cpu: 150m
      memory: 256Mi

backend:
  replicaCount: 4
  config:
    agentModel: "gpt-4o"
```

Install with custom values:
```bash
helm install todo-app-local ./k8s/helm-chart \
  -f custom-values.yaml \
  --set secrets.databaseUrl="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.openaiApiKey="..."
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-app-local ./k8s/helm-chart \
  --set backend.replicaCount=4

# Verify upgrade
kubectl rollout status deployment/backend-deployment -n todo-app
```

## Rollback

```bash
# Rollback to previous version
helm rollback todo-app-local -n todo-app

# Rollback to specific revision
helm rollback todo-app-local 2 -n todo-app
```

## Uninstallation

```bash
# Uninstall the release
helm uninstall todo-app-local -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

## Accessing the Application

### Minikube

```bash
# Open in browser
minikube service frontend-service -n todo-app

# Get URL
minikube service frontend-service -n todo-app --url
```

### Port Forward (alternative)

```bash
kubectl port-forward -n todo-app svc/frontend-service 3000:3000
# Access at http://localhost:3000
```

## Monitoring

### View Pods
```bash
kubectl get pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
```

### View Logs
```bash
# Frontend logs
kubectl logs -f deployment/frontend-deployment -n todo-app

# Backend logs
kubectl logs -f deployment/backend-deployment -n todo-app
```

### Resource Usage
```bash
kubectl top pods -n todo-app
kubectl top nodes
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app
```

### Image Pull Errors

For Minikube, ensure images are loaded:
```bash
minikube image ls | grep todo
```

If missing, load them:
```bash
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0
```

### Configuration Issues

Check ConfigMaps and Secrets:
```bash
kubectl get configmaps -n todo-app
kubectl get secrets -n todo-app

# View ConfigMap
kubectl describe configmap backend-config -n todo-app
```

## Development

### Dry Run

Test chart without installing:
```bash
helm install todo-app-local ./k8s/helm-chart \
  --dry-run --debug \
  --set secrets.databaseUrl="test" \
  --set secrets.betterAuthSecret="test" \
  --set secrets.openaiApiKey="test"
```

### Template Rendering

Render templates locally:
```bash
helm template todo-app-local ./k8s/helm-chart \
  --set secrets.databaseUrl="test" \
  --set secrets.betterAuthSecret="test" \
  --set secrets.openaiApiKey="test"
```

## Support

For issues or questions, refer to:
- Main README: `../../README.md`
- Architecture docs: `../../docs/ARCHITECTURE.md`
- Troubleshooting guide: `../../docs/TROUBLESHOOTING.md`
