# Kubernetes Architecture - Todo Chatbot Application

## Overview

The Todo Chatbot application is deployed on Kubernetes using a microservices architecture with three main components:
- **Frontend**: Next.js application serving the user interface
- **Backend**: FastAPI application providing REST APIs and AI chatbot functionality
- **Database**: PostgreSQL for data persistence (external Neon or in-cluster)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                      (Minikube - Local)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Namespace: todo-app                    │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         Frontend (NodePort 30080)            │  │    │
│  │  │  ┌────────────┐      ┌────────────┐         │  │    │
│  │  │  │  Pod 1     │      │  Pod 2     │         │  │    │
│  │  │  │ Next.js    │      │ Next.js    │         │  │    │
│  │  │  │ Port: 3000 │      │ Port: 3000 │         │  │    │
│  │  │  └────────────┘      └────────────┘         │  │    │
│  │  │         ↓                    ↓                │  │    │
│  │  │    frontend-service (NodePort)               │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                       ↓                             │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         Backend (ClusterIP)                  │  │    │
│  │  │  ┌────────────┐      ┌────────────┐         │  │    │
│  │  │  │  Pod 1     │      │  Pod 2     │         │  │    │
│  │  │  │ FastAPI    │      │ FastAPI    │         │  │    │
│  │  │  │ Port: 8000 │      │ Port: 8000 │         │  │    │
│  │  │  └────────────┘      └────────────┘         │  │    │
│  │  │         ↓                    ↓                │  │    │
│  │  │    backend-service (ClusterIP)               │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                       ↓                             │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │      Configuration & Secrets                 │  │    │
│  │  │  ┌──────────────┐  ┌──────────────┐         │  │    │
│  │  │  │ ConfigMaps   │  │   Secrets    │         │  │    │
│  │  │  │ - frontend   │  │ - DB URL     │         │  │    │
│  │  │  │ - backend    │  │ - Auth       │         │  │    │
│  │  │  │              │  │ - OpenAI     │         │  │    │
│  │  │  └──────────────┘  └──────────────┘         │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    External Database
                  (Neon PostgreSQL - Optional)
```

## Components

### 1. Frontend Deployment

**Image**: `todo-frontend:1.0.0`
- **Base**: node:20-alpine
- **Replicas**: 2 (configurable)
- **Resources**:
  - Requests: 100m CPU, 128Mi RAM
  - Limits: 500m CPU, 512Mi RAM
- **Port**: 3000
- **Health Checks**:
  - Liveness: GET / (30s initial, 10s period)
  - Readiness: GET / (10s initial, 5s period)

**Configuration** (ConfigMap: `frontend-config`):
- `NEXT_PUBLIC_API_URL`: Backend service URL
- `NEXT_PUBLIC_CHATKIT_ENABLED`: Enable chatbot UI

### 2. Backend Deployment

**Image**: `todo-backend:1.0.0`
- **Base**: python:3.13-slim
- **Replicas**: 2 (configurable)
- **Resources**:
  - Requests: 200m CPU, 256Mi RAM
  - Limits: 1000m CPU, 1Gi RAM
- **Port**: 8000
- **Health Checks**:
  - Liveness: GET /health (30s initial, 10s period)
  - Readiness: GET /health (10s initial, 5s period)

**Configuration** (ConfigMap: `backend-config`):
- `AGENT_MODEL`: AI model (gpt-4o-mini)
- `MAX_CONVERSATION_MESSAGES`: Message history limit
- `CORS_ORIGINS`: CORS configuration

**Secrets** (Secret: `app-secrets`):
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Authentication secret
- `OPENAI_API_KEY`: OpenAI API key

### 3. Database (Optional In-Cluster)

**Image**: `postgres:16-alpine`
- **Replicas**: 1
- **Resources**:
  - Requests: 500m CPU, 512Mi RAM
  - Limits: 1000m CPU, 2Gi RAM
- **Port**: 5432
- **Storage**: 1Gi PersistentVolumeClaim

**Note**: By default, the application uses external Neon PostgreSQL. Set `database.enabled=true` in Helm values to deploy in-cluster PostgreSQL.

## Networking

### Service Types

1. **frontend-service** (NodePort)
   - Type: NodePort
   - Port: 3000
   - NodePort: 30080
   - Purpose: External access to frontend
   - Access: `http://<minikube-ip>:30080`

2. **backend-service** (ClusterIP)
   - Type: ClusterIP
   - Port: 8000
   - Purpose: Internal backend API
   - DNS: `backend-service.todo-app.svc.cluster.local`

3. **postgres-service** (ClusterIP) - Optional
   - Type: ClusterIP
   - Port: 5432
   - Purpose: Internal database access
   - DNS: `postgres-service.todo-app.svc.cluster.local`

### Network Flow

1. **External User** → NodePort (30080) → Frontend Service → Frontend Pods
2. **Frontend** → ClusterIP → Backend Service → Backend Pods
3. **Backend** → ClusterIP → Database Service → Database Pod (or external Neon)

## Security

### Container Security

- **Non-root user**: All containers run as UID 1001
- **Read-only filesystem**: Where applicable
- **No privilege escalation**: Security context enforced
- **Resource limits**: Prevent resource exhaustion

### Secrets Management

- **Kubernetes Secrets**: Base64 encoded sensitive data
- **Environment injection**: Secrets injected as environment variables
- **No plain-text exposure**: Secrets not visible in pod specs or logs

### Network Security

- **ClusterIP for internal services**: Backend and database not externally accessible
- **NodePort for frontend only**: Controlled external access point
- **CORS configuration**: Backend validates origins

## Scaling

### Horizontal Scaling

```bash
# Scale backend
kubectl scale deployment backend-deployment --replicas=4 -n todo-app

# Scale frontend
kubectl scale deployment frontend-deployment --replicas=3 -n todo-app

# Using Helm
helm upgrade todo-app-local ./k8s/helm-chart \
  --set backend.replicaCount=4 \
  --set frontend.replicaCount=3
```

### Resource Scaling

Total cluster resources for baseline (2+2 replicas):
- **CPU**: ~1.3 cores (requests), ~5 cores (limits)
- **Memory**: ~1.5Gi (requests), ~5.5Gi (limits)

Recommended Minikube configuration:
- **CPUs**: 4
- **Memory**: 8GB
- **Disk**: 20GB

## High Availability

### Rolling Updates

- **Strategy**: RollingUpdate
- **maxUnavailable**: 1 pod
- **maxSurge**: 1 pod
- **Zero downtime**: Health probes ensure traffic only to ready pods

### Health Monitoring

- **Liveness probes**: Detect and restart dead containers
- **Readiness probes**: Remove unhealthy pods from service load balancer
- **Startup time**: 30s initial delay for application startup

## Deployment Strategy

### Helm-Based Deployment

1. **Package Management**: Helm chart for reproducible deployments
2. **Parameterization**: All values configurable via `values.yaml`
3. **Version Control**: Chart versioning for rollback capability
4. **Environment Flexibility**: Same chart for dev/staging/prod

### Rollback Capability

```bash
# View release history
helm history todo-app-local -n todo-app

# Rollback to previous version
helm rollback todo-app-local -n todo-app

# Rollback to specific revision
helm rollback todo-app-local 2 -n todo-app
```

## Monitoring & Observability

### Logs

```bash
# View logs
kubectl logs -f deployment/backend-deployment -n todo-app
kubectl logs -f deployment/frontend-deployment -n todo-app

# View logs from all pods
kubectl logs -l app=backend -n todo-app --tail=100
```

### Metrics

```bash
# Pod resource usage
kubectl top pods -n todo-app

# Node resource usage
kubectl top nodes
```

### Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard
```

## Disaster Recovery

### Backup Strategy

1. **Database**: Regular backups of PostgreSQL data
2. **Configuration**: Version-controlled Helm values
3. **Images**: Tagged Docker images in registry

### Recovery Procedure

1. Restore database from backup
2. Deploy application using Helm chart
3. Verify health checks and functionality

## Future Enhancements (Phase V)

- **Ingress Controller**: TLS/HTTPS support
- **Horizontal Pod Autoscaler**: Automatic scaling based on metrics
- **Persistent Volumes**: Dynamic provisioning
- **Service Mesh**: Istio for advanced traffic management
- **Monitoring Stack**: Prometheus + Grafana
- **Multi-node Cluster**: High availability across nodes
- **Cloud Deployment**: Azure/GCP/AWS
