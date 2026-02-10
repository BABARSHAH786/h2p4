# Implementation Plan: Phase IV - Local Kubernetes Deployment

**Branch**: `001-kubernetes-deployment` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-kubernetes-deployment/spec.md`

## Summary

Transform the Phase III Todo Chatbot into a cloud-native application by containerizing all components (frontend, backend, database) and deploying them on a local Kubernetes cluster using Minikube. The deployment will use Helm charts for reproducibility, implement health monitoring, support horizontal scaling, and separate configuration from code using ConfigMaps and Secrets. AI-assisted DevOps tools (Gordon, kubectl-ai, kagent) will be leveraged for Dockerfile generation, deployment automation, and troubleshooting.

## Technical Context

**Language/Version**:
- Frontend: TypeScript with Next.js 15 (App Router)
- Backend: Python 3.13 with FastAPI
- Infrastructure: YAML for Kubernetes manifests, Helm templates

**Primary Dependencies**:
- Docker Desktop 4.53+ (with Gordon AI)
- Minikube 1.32+ (local Kubernetes)
- Helm 3.13+ (package manager)
- kubectl 1.28+ (cluster management)
- kubectl-ai (optional - AI-assisted deployments)
- kagent (optional - cluster analysis)

**Storage**:
- Neon PostgreSQL (external managed service) OR
- PostgreSQL 16 (in-cluster deployment)
- Persistent volumes for database data

**Testing**:
- Container testing: Docker build and run locally
- Kubernetes testing: kubectl dry-run, pod status verification
- End-to-end testing: Full user journey through NodePort access

**Target Platform**:
- Local Kubernetes cluster (Minikube on Docker driver)
- Single-node cluster (multi-node in Phase V)
- Windows 10/11, macOS, or Linux host

**Project Type**: Web application (frontend + backend + database)

**Performance Goals**:
- Deployment time: < 5 minutes from start to operational
- Container startup: < 60 seconds per service
- Scaling operations: < 60 seconds with zero downtime
- Rolling updates: < 2 minutes with zero downtime
- Health check response: < 100ms

**Constraints**:
- Total cluster resources: < 4GB RAM, < 2 CPU cores
- Container image sizes: Frontend < 100MB, Backend < 200MB
- Local deployment only (no cloud)
- Manual scaling (no HPA)
- Basic monitoring (no Prometheus/Grafana)

**Scale/Scope**:
- 2-10 replicas per service
- 3 services (frontend, backend, database)
- 1 namespace (todo-app)
- 1 Helm chart (todo-app-chart)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

- [x] **Separation of Concerns**: Frontend, backend, database, and infrastructure layers remain separate. Kubernetes orchestrates containers without mixing concerns.
- [x] **API-First Design**: Services communicate via Kubernetes Services (DNS-based). No hardcoded IPs. All Phase III APIs preserved.
- [x] **Stateless Backend**: Backend pods are stateless. Session/conversation data in database. Horizontal scaling without coordination.
- [x] **MCP-First Design**: Phase III MCP tools preserved. No changes to AI agent interface.
- [x] **Cloud-Native Principles**: All components containerized. Declarative Kubernetes manifests. Immutable infrastructure.
- [x] **Security-First**: Non-root containers (UID 1001). Secrets in Kubernetes Secrets. Network isolation (ClusterIP for internal services).
- [x] **Performance Standards**: Container images < 100MB/200MB. Pod startup < 60s. Health checks < 100ms.

### Phase IV Kubernetes Deployment Considerations

- [x] **Container images planned**:
  - Frontend: `frontend/Dockerfile` (node:20-alpine base, multi-stage)
  - Backend: `backend/Dockerfile` (python:3.13-slim base, multi-stage)
  - Database: Official postgres:16-alpine OR external Neon

- [x] **Kubernetes resources defined**:
  - Namespace: todo-app
  - Deployments: frontend-deployment (2 replicas), backend-deployment (2 replicas), postgres-deployment (1 replica)
  - Services: frontend-service (NodePort), backend-service (ClusterIP), postgres-service (ClusterIP)
  - ConfigMaps: frontend-config, backend-config
  - Secrets: app-secrets (DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY)

- [x] **Health and readiness probes designed**:
  - Frontend: GET / on port 3000
  - Backend: GET /health on port 8000
  - Liveness: 30s initial delay, 10s period
  - Readiness: 10s initial delay, 5s period

- [x] **Resource requests and limits specified**:
  - Frontend: 100m CPU / 128Mi RAM (request), 500m CPU / 512Mi RAM (limit)
  - Backend: 200m CPU / 256Mi RAM (request), 1000m CPU / 1Gi RAM (limit)
  - Database: 500m CPU / 512Mi RAM (request), 1000m CPU / 2Gi RAM (limit)

- [x] **Helm chart structure planned**:
  - Chart.yaml (metadata)
  - values.yaml (parameterized configuration)
  - templates/ (deployment.yaml, service.yaml, configmap.yaml, secret.yaml, namespace.yaml, _helpers.tpl)
  - .helmignore

- [x] **Configuration management strategy**:
  - ConfigMaps: Non-sensitive (AGENT_MODEL, MAX_CONVERSATION_MESSAGES, CORS_ORIGINS, API_URL)
  - Secrets: Sensitive (DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY) - base64 encoded
  - Environment variable injection via envFrom

- [x] **Service networking planned**:
  - Frontend: NodePort (30080) for external access
  - Backend: ClusterIP (internal only, accessed via frontend)
  - Database: ClusterIP (internal only, accessed via backend)
  - DNS: backend-service.todo-app.svc.cluster.local

- [x] **Deployment strategy defined**:
  - Rolling updates: maxUnavailable=1, maxSurge=1
  - Rollback: helm rollback todo-app-local
  - Zero downtime: Health probes ensure traffic only to ready pods

- [x] **Monitoring and logging approach**:
  - Logs to stdout/stderr (captured by Kubernetes)
  - Structured JSON logs with timestamp, level, service name
  - Access via: kubectl logs <pod-name> -n todo-app
  - Dashboard: minikube dashboard

- [x] **AI DevOps tools identified**:
  - Gordon (Docker AI): Dockerfile generation and optimization
  - kubectl-ai: Deployment command generation and troubleshooting
  - kagent: Cluster health analysis and resource optimization

### Constitution Check Result: ✅ PASS

All Phase IV requirements met. No violations. Ready to proceed with Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-kubernetes-deployment/
├── plan.md              # This file
├── research.md          # Phase 0: Container and Kubernetes best practices
├── data-model.md        # Phase 1: Kubernetes resource definitions
├── quickstart.md        # Phase 1: Local deployment guide
├── contracts/           # Phase 1: Kubernetes manifests and Helm templates
│   ├── namespace.yaml
│   ├── frontend-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── postgres-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-service.yaml
│   ├── postgres-service.yaml
│   ├── frontend-configmap.yaml
│   ├── backend-configmap.yaml
│   ├── app-secrets.yaml
│   └── helm-chart/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── tasks.md             # Phase 2: Implementation tasks (generated by /sp.tasks)
```

### Source Code (repository root)

```text
# Web application structure (existing from Phase III)
backend/
├── Dockerfile           # NEW: Multi-stage Python container
├── .dockerignore        # NEW: Exclude unnecessary files
├── app/
│   ├── main.py          # Existing FastAPI app
│   ├── models/          # Existing database models
│   ├── routes/          # Existing API routes
│   ├── mcp/             # Existing MCP server
│   └── utils/           # Existing utilities
├── alembic/             # Existing database migrations
├── pyproject.toml       # Existing dependencies
└── uv.lock              # Existing lock file

frontend/
├── Dockerfile           # NEW: Multi-stage Next.js container
├── .dockerignore        # NEW: Exclude unnecessary files
├── app/                 # Existing Next.js app
├── components/          # Existing React components
├── hooks/               # Existing custom hooks
├── lib/                 # Existing utilities
├── public/              # Existing static assets
├── package.json         # Existing dependencies
└── next.config.ts       # Existing Next.js config

# NEW: Kubernetes deployment files
k8s/
├── namespace.yaml
├── deployments/
│   ├── frontend-deployment.yaml
│   ├── backend-deployment.yaml
│   └── postgres-deployment.yaml
├── services/
│   ├── frontend-service.yaml
│   ├── backend-service.yaml
│   └── postgres-service.yaml
├── config/
│   ├── frontend-configmap.yaml
│   ├── backend-configmap.yaml
│   └── app-secrets.yaml
└── helm-chart/
    ├── Chart.yaml
    ├── values.yaml
    ├── .helmignore
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        ├── configmap.yaml
        ├── secret.yaml
        ├── namespace.yaml
        └── _helpers.tpl
```

**Structure Decision**: Web application structure with new Kubernetes deployment files. Existing Phase III application code remains unchanged. New Dockerfiles added to frontend/ and backend/ directories. Kubernetes manifests organized in k8s/ directory. Helm chart in k8s/helm-chart/ for reproducible deployments.

## Complexity Tracking

> No constitution violations. This section is not applicable.

---

## Phase IV: Kubernetes Deployment Plan

### Container Strategy

**Frontend Container**:
- **Base image**: node:20-alpine (minimal size, security updates)
- **Build strategy**: Multi-stage build
  - Stage 1 (builder): Install dependencies, build Next.js app
  - Stage 2 (runtime): Copy build artifacts, run production server
- **Size target**: < 100MB
- **Health endpoint**: GET / on port 3000 (Next.js default)
- **Non-root user**: UID 1001 (appuser)
- **Exposed port**: 3000
- **Environment variables**: NEXT_PUBLIC_API_URL (from ConfigMap)

**Backend Container**:
- **Base image**: python:3.13-slim (minimal size, official Python)
- **Build strategy**: Multi-stage build
  - Stage 1 (builder): Install UV, sync dependencies
  - Stage 2 (runtime): Copy app code and dependencies
- **Size target**: < 200MB
- **Health endpoint**: GET /health on port 8000 (FastAPI endpoint)
- **Non-root user**: UID 1001 (appuser)
- **Exposed port**: 8000
- **Environment variables**: DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET (from Secret), AGENT_MODEL, MAX_CONVERSATION_MESSAGES, CORS_ORIGINS (from ConfigMap)

**Database Container**:
- **Strategy**: Two options
  - Option A: External Neon PostgreSQL (recommended for Phase IV)
  - Option B: In-cluster postgres:16-alpine (for testing)
- **Persistence**:
  - Option A: Managed by Neon
  - Option B: PersistentVolumeClaim (1Gi)
- **Exposed port**: 5432 (ClusterIP only)

### Kubernetes Resources

**Namespace**: `todo-app`
- Isolates all Phase IV resources
- Enables resource quotas and network policies (future)

**Deployments**:
1. **frontend-deployment**:
   - Replicas: 2 (high availability)
   - Image: todo-frontend:1.0.0
   - Resources: 100m/128Mi (request), 500m/512Mi (limit)
   - Liveness probe: HTTP GET / :3000 (30s initial, 10s period)
   - Readiness probe: HTTP GET / :3000 (10s initial, 5s period)
   - Rolling update: maxUnavailable=1, maxSurge=1

2. **backend-deployment**:
   - Replicas: 2 (high availability)
   - Image: todo-backend:1.0.0
   - Resources: 200m/256Mi (request), 1000m/1Gi (limit)
   - Liveness probe: HTTP GET /health :8000 (30s initial, 10s period)
   - Readiness probe: HTTP GET /health :8000 (10s initial, 5s period)
   - Rolling update: maxUnavailable=1, maxSurge=1

3. **postgres-deployment** (if in-cluster):
   - Replicas: 1 (StatefulSet in production)
   - Image: postgres:16-alpine
   - Resources: 500m/512Mi (request), 1000m/2Gi (limit)
   - PersistentVolumeClaim: 1Gi
   - Environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD (from Secret)

**Services**:
1. **frontend-service**:
   - Type: NodePort
   - Port: 3000 → NodePort 30080
   - Selector: app=frontend
   - External access: http://<minikube-ip>:30080

2. **backend-service**:
   - Type: ClusterIP (internal only)
   - Port: 8000
   - Selector: app=backend
   - DNS: backend-service.todo-app.svc.cluster.local

3. **postgres-service** (if in-cluster):
   - Type: ClusterIP (internal only)
   - Port: 5432
   - Selector: app=postgres
   - DNS: postgres-service.todo-app.svc.cluster.local

**ConfigMaps**:
1. **frontend-config**:
   ```yaml
   data:
     API_URL: "http://backend-service:8000"
     NEXT_PUBLIC_CHATKIT_ENABLED: "true"
   ```

2. **backend-config**:
   ```yaml
   data:
     AGENT_MODEL: "gpt-4o-mini"
     MAX_CONVERSATION_MESSAGES: "50"
     CORS_ORIGINS: "*"
   ```

**Secrets**:
1. **app-secrets**:
   ```yaml
   data:
     DATABASE_URL: <base64-encoded>
     BETTER_AUTH_SECRET: <base64-encoded>
     OPENAI_API_KEY: <base64-encoded>
   ```

### Helm Chart Design

**Chart Structure**:
```
todo-app-chart/
├── Chart.yaml           # name: todo-app, version: 1.0.0, appVersion: 1.0.0
├── values.yaml          # Default configuration values
├── .helmignore          # Exclude unnecessary files
└── templates/
    ├── namespace.yaml   # Namespace definition
    ├── deployment.yaml  # Parameterized deployments (frontend, backend, postgres)
    ├── service.yaml     # Parameterized services
    ├── configmap.yaml   # Parameterized ConfigMaps
    ├── secret.yaml      # Parameterized Secrets
    └── _helpers.tpl     # Template helper functions
```

**values.yaml Structure**:
```yaml
namespace: todo-app

frontend:
  replicaCount: 2
  image:
    repository: todo-frontend
    tag: "1.0.0"
    pullPolicy: IfNotPresent
  service:
    type: NodePort
    port: 3000
    nodePort: 30080
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  config:
    apiUrl: "http://backend-service:8000"
    chatkitEnabled: "true"

backend:
  replicaCount: 2
  image:
    repository: todo-backend
    tag: "1.0.0"
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  config:
    agentModel: "gpt-4o-mini"
    maxConversationMessages: "50"
    corsOrigins: "*"

database:
  enabled: false  # Set to true for in-cluster PostgreSQL
  image:
    repository: postgres
    tag: "16-alpine"
  service:
    port: 5432
  persistence:
    enabled: true
    size: 1Gi
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi

secrets:
  databaseUrl: ""  # Set during installation
  betterAuthSecret: ""
  openaiApiKey: ""
```

**Helm Release Naming**: `todo-app-local`

**Helm Commands**:
```bash
# Install
helm install todo-app-local ./k8s/helm-chart \
  --set secrets.databaseUrl="<encoded>" \
  --set secrets.betterAuthSecret="<encoded>" \
  --set secrets.openaiApiKey="<encoded>"

# Upgrade
helm upgrade todo-app-local ./k8s/helm-chart

# Rollback
helm rollback todo-app-local

# Uninstall
helm uninstall todo-app-local
```

### Resource Allocation

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Frontend (per pod) | 100m | 500m | 128Mi | 512Mi |
| Backend (per pod) | 200m | 1000m | 256Mi | 1Gi |
| Database (if in-cluster) | 500m | 1000m | 512Mi | 2Gi |
| **Total (baseline: 2+2+1 pods)** | **1.3 CPU** | **5 CPU** | **1.5Gi** | **5.5Gi** |

**Cluster Requirements**:
- Minimum: 4 CPU cores, 8GB RAM (Minikube configuration)
- Baseline deployment: ~1.3 CPU, ~1.5GB RAM
- Headroom: ~2.7 CPU, ~6.5GB RAM for scaling and system overhead

### Health Probes Configuration

**Liveness Probes** (detect dead containers):
```yaml
livenessProbe:
  httpGet:
    path: /health  # or / for frontend
    port: 8000     # or 3000 for frontend
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Readiness Probes** (detect not-ready containers):
```yaml
readinessProbe:
  httpGet:
    path: /health  # or / for frontend
    port: 8000     # or 3000 for frontend
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Health Endpoint Requirements**:
- Backend: Implement GET /health endpoint in FastAPI
  - Returns 200 OK when healthy
  - Checks database connectivity
  - Response time < 100ms
  - No side effects (idempotent)
- Frontend: Use default Next.js / endpoint
  - Returns 200 OK when server is ready
  - Response time < 100ms

### Deployment Strategy

**Rolling Update**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1  # Max 1 pod down during update
    maxSurge: 1        # Max 1 extra pod during update
```

**Rollback Plan**:
```bash
# Automatic rollback on failure
helm rollback todo-app-local

# Manual rollback to specific revision
helm rollback todo-app-local <revision-number>

# Verify rollback
kubectl get pods -n todo-app
kubectl rollout status deployment/backend-deployment -n todo-app
```

**Zero Downtime Strategy**:
1. Health probes ensure traffic only to ready pods
2. Rolling update brings up new pods before terminating old ones
3. Service load balancer distributes traffic across healthy pods
4. maxUnavailable=1 ensures at least 1 pod always available

### AI DevOps Tools Usage

**Gordon (Docker AI)**:
- **Use for**: Dockerfile generation and optimization
- **Example interactions**:
  ```bash
  docker ai "Create optimized multi-stage Dockerfile for FastAPI app with UV package manager"
  docker ai "Why is my container image 500MB? Suggest optimizations"
  docker ai "Container exits immediately after starting, analyze logs"
  ```
- **Integration**: Use Gordon suggestions to create initial Dockerfiles, then refine manually
- **Documentation**: Record Gordon interactions in implementation notes

**kubectl-ai**:
- **Use for**: Deployment command generation and troubleshooting
- **Example interactions**:
  ```bash
  kubectl-ai "deploy todo frontend with 2 replicas and 100m CPU limit"
  kubectl-ai "check why pods are in CrashLoopBackOff"
  kubectl-ai "scale backend to handle 100 requests per second"
  kubectl-ai "show me logs of failing pods"
  ```
- **Integration**: Use kubectl-ai to generate initial YAML, then review and apply
- **Validation**: Always review generated YAML before applying (kubectl apply --dry-run)

**kagent** (if available):
- **Use for**: Cluster health analysis and resource optimization
- **Example interactions**:
  ```bash
  kagent "analyze cluster health and resource usage"
  kagent "suggest resource allocation improvements"
  kagent "identify bottlenecks in the deployment"
  ```
- **Integration**: Use kagent insights to optimize resource requests/limits
- **Optional**: Core functionality works without kagent

### Testing Strategy

**Container Testing**:
1. Build images locally:
   ```bash
   docker build -t todo-frontend:1.0.0 ./frontend
   docker build -t todo-backend:1.0.0 ./backend
   ```
2. Test images locally:
   ```bash
   docker run -p 3000:3000 todo-frontend:1.0.0
   docker run -p 8000:8000 -e DATABASE_URL=... todo-backend:1.0.0
   ```
3. Verify health endpoints:
   ```bash
   curl http://localhost:3000/
   curl http://localhost:8000/health
   ```
4. Check image sizes:
   ```bash
   docker images | grep todo
   ```

**Kubernetes Testing**:
1. Dry-run manifests:
   ```bash
   kubectl apply --dry-run=client -f k8s/
   ```
2. Apply manifests:
   ```bash
   kubectl apply -f k8s/
   ```
3. Watch pod status:
   ```bash
   kubectl get pods -n todo-app -w
   ```
4. Verify services:
   ```bash
   kubectl get svc -n todo-app
   ```
5. Test connectivity:
   ```bash
   kubectl exec -it <frontend-pod> -n todo-app -- curl backend-service:8000/health
   ```

**End-to-End Testing**:
1. Get Minikube IP:
   ```bash
   minikube ip
   ```
2. Access frontend:
   ```
   http://<minikube-ip>:30080
   ```
3. Test user journeys:
   - Sign up new user
   - Add tasks via web UI
   - Add tasks via chatbot
   - Verify data persists
4. Test scaling:
   ```bash
   kubectl scale deployment backend-deployment --replicas=4 -n todo-app
   kubectl get pods -n todo-app
   ```
5. Test rollback:
   ```bash
   helm rollback todo-app-local
   kubectl get pods -n todo-app
   ```

### Monitoring and Logging

**Logging Strategy**:
- All logs to stdout/stderr (captured by Kubernetes)
- Structured JSON format:
  ```json
  {
    "timestamp": "2026-02-07T10:30:00Z",
    "level": "INFO",
    "service": "backend",
    "message": "User authenticated successfully",
    "user_id": "user123"
  }
  ```
- No sensitive data in logs (passwords, API keys)

**Log Access**:
```bash
# View logs for specific pod
kubectl logs <pod-name> -n todo-app

# Follow logs in real-time
kubectl logs -f <pod-name> -n todo-app

# View logs for all pods with label
kubectl logs -l app=backend -n todo-app

# View previous container logs (if crashed)
kubectl logs <pod-name> -n todo-app --previous
```

**Monitoring Endpoints**:
- `/health` - Health check (liveness)
- `/ready` - Readiness check (optional, can use /health)
- `/metrics` - Prometheus metrics (Phase V)

**Dashboard Access**:
```bash
minikube dashboard
```

### Documentation Requirements

- [ ] README.md: Updated with Kubernetes deployment instructions
- [ ] ARCHITECTURE.md: Kubernetes architecture diagram
- [ ] TROUBLESHOOTING.md: Common Kubernetes issues and solutions
- [ ] k8s/helm-chart/README.md: Helm chart documentation
- [ ] k8s/helm-chart/values.yaml: Inline comments for all options
- [ ] Demo video: Showing Kubernetes deployment process

---

## Phase 0: Research (To be completed)

Research tasks to be executed:
1. Docker multi-stage build best practices for Next.js and FastAPI
2. Kubernetes resource sizing for web applications
3. Helm chart templating patterns and best practices
4. Health probe configuration for Node.js and Python applications
5. Kubernetes Secrets management and base64 encoding
6. Minikube configuration and addon requirements
7. Container image optimization techniques
8. Kubernetes rolling update strategies
9. AI DevOps tools (Gordon, kubectl-ai, kagent) capabilities and limitations
10. Database persistence strategies in Kubernetes

**Output**: research.md with findings and decisions

## Phase 1: Design (To be completed)

Design tasks to be executed:
1. Create data-model.md with Kubernetes resource definitions
2. Generate Kubernetes manifests in contracts/ directory
3. Create Helm chart structure in contracts/helm-chart/
4. Create quickstart.md with step-by-step deployment guide
5. Update agent context with Phase IV technologies

**Output**: data-model.md, contracts/*, quickstart.md, updated agent context

## Phase 2: Tasks (To be completed by /sp.tasks)

Task generation will be handled by `/sp.tasks` command after Phase 1 completion.

---

## Next Steps

1. Execute Phase 0 research to resolve any remaining technical questions
2. Execute Phase 1 design to create Kubernetes manifests and Helm charts
3. Run `/sp.tasks` to generate implementation tasks
4. Begin implementation following the task list

**Status**: Plan complete. Ready for Phase 0 research.
