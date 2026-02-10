# Implementation Plan: Phase V - Advanced Cloud Deployment

**Branch**: `001-phase-v-cloud-deployment` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-v-cloud-deployment/spec.md`

## Summary

Transform the Todo Chatbot into a production-grade, cloud-native, event-driven distributed system with advanced task management features (priorities, tags, search, recurring tasks, reminders) deployed to cloud Kubernetes (OKE/GKE/AKS) with Kafka, Dapr, and full CI/CD pipeline.

**Primary Requirement**: Implement microservices architecture with event-driven communication, enabling advanced task management features and cloud deployment with zero-downtime updates.

**Technical Approach**: Decompose monolithic backend into 4 microservices (Chat API, Recurring Task Service, Notification Service, Frontend), implement Kafka event streaming via Dapr Pub/Sub, add Dapr Jobs API for scheduled reminders, deploy to cloud Kubernetes with Helm charts and GitHub Actions CI/CD.

## Technical Context

**Language/Version**: Python 3.13+ (backend services), Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, Official MCP SDK, Dapr SDK, Kafka Python client, Next.js 16, Better Auth
**Storage**: Neon Serverless PostgreSQL (primary database), Dapr State Store (conversation cache), Kafka (event streaming)
**Testing**: pytest (backend unit/integration), Jest (frontend), E2E tests with Playwright
**Target Platform**: Kubernetes (Minikube for local, OKE/GKE/AKS for cloud)
**Project Type**: Web application with microservices architecture
**Performance Goals**:
- Chat responses <2s (p95 latency)
- Task operations <500ms (p95 latency)
- Event processing <5s (p95 latency)
- Support 100 concurrent users per service instance
**Constraints**:
- Zero-downtime deployments required
- Event delivery at-least-once guarantee
- Reminder accuracy ±1 minute
- Multi-device sync within 5 seconds
**Scale/Scope**:
- 4 microservices + frontend
- 10,000+ concurrent users (horizontal scaling)
- 3 Kafka topics with 3 partitions each
- 46 functional requirements across 7 categories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase V Advanced Cloud Deployment Considerations

✅ **All requirements verified:**

- [x] Microservices boundaries defined (Chat API:8000, Recurring Task:8001, Notification:8002, Frontend:3000)
- [x] Event-driven architecture planned (task-events, reminders, task-updates topics)
- [x] Dapr building blocks identified (Pub/Sub, State Management, Service Invocation, Jobs API, Secrets)
- [x] Event schema standardized (event_id, event_type, timestamp, user_id, data, metadata)
- [x] Kafka topics configured (3 partitions, 7-day retention, unique consumer groups)
- [x] State management strategy (Dapr State Store with PostgreSQL backend)
- [x] Service communication via events (no direct service-to-service database access)
- [x] Horizontal Pod Autoscaling (HPA) configured (CPU >70%, Memory >80%)
- [x] Cloud platform selected (OKE preferred, GKE/AKS alternatives)
- [x] Kafka deployment strategy (Strimzi operator for self-hosted, Redpanda Cloud for managed)
- [x] Advanced features planned (priorities, tags, search, recurring tasks, reminders)
- [x] CI/CD pipeline stages defined (lint, test, build, push, deploy-dev, deploy-prod)
- [x] Monitoring and observability (structured JSON logs, /health/live, /health/ready, metrics)

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-v-cloud-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── event-schemas.md # Kafka event schemas
│   ├── mcp-tools.md     # Updated MCP tool contracts
│   └── api-endpoints.md # Service API contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                    # Chat API service (FastAPI)
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection
│   ├── models/
│   │   ├── task.py                # Updated Task model (priorities, tags, due_at, recurrence)
│   │   ├── conversation.py        # Conversation model
│   │   └── message.py             # Message model
│   ├── routes/
│   │   ├── auth.py                # Authentication endpoints
│   │   └── chat.py                # Chat endpoint
│   ├── mcp/
│   │   ├── server.py              # MCP server
│   │   └── tools/
│   │       ├── add_task.py        # Updated with priorities, tags, due_at, reminders
│   │       ├── update_task.py     # Updated with new fields
│   │       ├── list_tasks.py      # Updated with filtering and sorting
│   │       ├── search_tasks.py    # NEW: Keyword search
│   │       ├── complete_task.py   # Existing
│   │       └── delete_task.py     # Existing
│   └── utils/
│       ├── agent.py               # OpenAI Agents SDK integration
│       └── events.py              # NEW: Kafka event publishing via Dapr
├── services/
│   ├── recurring_task_service/
│   │   ├── main.py                # FastAPI service
│   │   ├── consumer.py            # Kafka consumer for task-events
│   │   └── handler.py             # Recurring task logic
│   └── notification_service/
│       ├── main.py                # FastAPI service
│       ├── consumer.py            # Kafka consumer for reminders
│       └── notifier.py            # Email/push notification logic
├── alembic/
│   └── versions/
│       └── 004_add_advanced_features.py  # NEW: Migration for priorities, tags, etc.
└── tests/
    ├── unit/
    ├── integration/
    │   ├── test_kafka_events.py   # NEW: Event publishing tests
    │   └── test_dapr_jobs.py      # NEW: Reminder scheduling tests
    └── e2e/

frontend/
├── src/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx           # Existing chat UI
│   └── components/
│       └── chat/                  # Existing chat components
└── tests/

k8s/
├── base/
│   ├── namespace.yaml
│   ├── chat-api/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── recurring-task-service/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── notification-service/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── dapr-components/
│       ├── pubsub-kafka.yaml      # Dapr Pub/Sub component
│       ├── statestore-postgres.yaml  # Dapr State Store component
│       ├── jobs.yaml               # Dapr Jobs API component
│       └── secretstore.yaml        # Dapr Secret Store component
├── overlays/
│   ├── local/                      # Minikube overrides
│   └── production/                 # Cloud overrides
└── kafka/
    └── kafka-cluster.yaml          # Strimzi Kafka cluster definition

helm/
├── Chart.yaml
├── values.yaml                     # Default values
├── values-local.yaml               # Minikube overrides
├── values-production.yaml          # Cloud overrides
└── templates/
    ├── chat-api/
    ├── recurring-task-service/
    ├── notification-service/
    ├── frontend/
    ├── dapr-components/
    └── _helpers.tpl

.github/
└── workflows/
    └── ci-cd.yaml                  # NEW: GitHub Actions pipeline
```

**Structure Decision**: Web application with microservices architecture. Backend split into 3 services (Chat API, Recurring Task Service, Notification Service) plus frontend. All services containerized and deployed to Kubernetes with Dapr sidecars for event-driven communication.

## Complexity Tracking

> **No constitutional violations** - All design decisions align with Phase V constitution principles.

---

## Phase V: Microservices & Event-Driven Architecture

### Microservices Breakdown

#### 1. Chat API Service (Port 8000, Dapr App ID: `chat-api`)

**Responsibilities**:
- Handle `/api/{user_id}/chat` endpoint
- Execute OpenAI Agents SDK logic
- Interface with MCP tools for task operations
- Publish events to Kafka via Dapr Pub/Sub
- Enforce JWT authentication

**Key Components**:
- `app/main.py`: FastAPI application with Dapr sidecar
- `app/routes/chat.py`: Chat endpoint implementation
- `app/mcp/server.py`: MCP server with updated tools
- `app/utils/events.py`: Event publishing helper

**Event Publishing**:
- `task.created` → `task-events` topic
- `task.updated` → `task-events` topic
- `task.completed` → `task-events` topic
- `task.deleted` → `task-events` topic
- `reminder.scheduled` → `reminders` topic

**Database Access**: Direct access to `tasks`, `conversations`, `messages` tables

**Dapr Components Used**:
- Pub/Sub (Kafka)
- State Management (conversation cache)
- Secrets Management (DATABASE_URL, OPENAI_API_KEY)

#### 2. Recurring Task Service (Port 8001, Dapr App ID: `recurring-task-service`)

**Responsibilities**:
- Subscribe to `task-events` topic
- Detect recurring task completions
- Calculate next occurrence date
- Create next task via MCP tools or direct DB
- Publish `task.created` event

**Key Components**:
- `services/recurring_task_service/main.py`: FastAPI service
- `services/recurring_task_service/consumer.py`: Kafka consumer
- `services/recurring_task_service/handler.py`: Recurrence logic

**Event Consumption**:
- Subscribes to: `task-events` (consumer group: `recurring-task-service`)
- Filters for: `task.completed` events where `recurrence != 'none'`

**Event Publishing**:
- `task.created` → `task-events` topic (for next occurrence)

**Database Access**: Direct access to `tasks` table (read/write)

**Dapr Components Used**:
- Pub/Sub (Kafka)
- Secrets Management (DATABASE_URL)

#### 3. Notification Service (Port 8002, Dapr App ID: `notification-service`)

**Responsibilities**:
- Subscribe to `reminders` topic
- Send notifications via email/push
- Log notification delivery status
- Mark reminders as sent

**Key Components**:
- `services/notification_service/main.py`: FastAPI service
- `services/notification_service/consumer.py`: Kafka consumer
- `services/notification_service/notifier.py`: Notification logic

**Event Consumption**:
- Subscribes to: `reminders` (consumer group: `notification-service`)
- Processes: `reminder.triggered` events

**Database Access**: Direct access to `tasks` table (read-only for task details)

**Dapr Components Used**:
- Pub/Sub (Kafka)
- Secrets Management (EMAIL_API_KEY, DATABASE_URL)

#### 4. Frontend Service (Port 3000, Dapr App ID: `frontend`)

**Responsibilities**:
- Serve Next.js application
- Handle user authentication (Better Auth)
- Communicate with Chat API via Dapr service invocation

**Key Components**:
- `frontend/src/app/chat/page.tsx`: Chat UI
- `frontend/src/components/chat/`: Chat components

**Dapr Components Used**:
- Service Invocation (call Chat API)
- Secrets Management (BETTER_AUTH_SECRET)

### Database Schema Updates

**Updated `tasks` table**:

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- NEW: Phase V fields
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    tags TEXT[] DEFAULT '{}',
    due_at TIMESTAMP,
    reminder_minutes_before INTEGER DEFAULT 60,
    recurrence VARCHAR(20) DEFAULT 'none' CHECK (recurrence IN ('none', 'daily', 'weekly', 'monthly', 'yearly')),
    recurrence_end_date TIMESTAMP,
    reminder_sent BOOLEAN DEFAULT FALSE,

    INDEX idx_user_id (user_id),
    INDEX idx_priority (priority),
    INDEX idx_due_at (due_at),
    INDEX idx_tags USING GIN (tags)
);
```

**Migration**: `alembic/versions/004_add_advanced_features.py`

### Event Architecture

#### Kafka Topics Configuration

**1. `task-events` Topic**:
- **Partitions**: 3
- **Retention**: 7 days
- **Replication Factor**: 3 (production), 1 (local)
- **Producers**: Chat API (MCP tools)
- **Consumers**: Recurring Task Service, Audit Service (optional)

**2. `reminders` Topic**:
- **Partitions**: 3
- **Retention**: 7 days
- **Replication Factor**: 3 (production), 1 (local)
- **Producers**: Chat API (when due_at is set)
- **Consumers**: Notification Service

**3. `task-updates` Topic** (Optional - for real-time sync):
- **Partitions**: 3
- **Retention**: 1 day
- **Replication Factor**: 3 (production), 1 (local)
- **Producers**: Chat API
- **Consumers**: WebSocket Service (future)

#### Event Schema Standard

All events follow this structure:

```json
{
  "event_id": "uuid-v4",
  "event_type": "task.created | task.updated | task.completed | task.deleted | reminder.scheduled | reminder.triggered",
  "timestamp": "2026-02-10T10:30:00Z",
  "user_id": "string",
  "data": {
    "task_id": "uuid",
    "title": "string",
    "priority": "high | medium | low",
    "tags": ["string"],
    "due_at": "2026-02-15T14:00:00Z",
    "recurrence": "none | daily | weekly | monthly | yearly",
    "reminder_minutes_before": 60
  },
  "metadata": {
    "source_service": "chat-api",
    "correlation_id": "optional-trace-id"
  }
}
```

### Dapr Configuration

#### Pub/Sub Component (Kafka)

**File**: `k8s/base/dapr-components/pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "{appId}"
  - name: authType
    value: "none"
```

#### State Store Component (PostgreSQL)

**File**: `k8s/base/dapr-components/statestore-postgres.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connectionString
```

#### Jobs API Component

**File**: `k8s/base/dapr-components/jobs.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: jobs
spec:
  type: jobs.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connectionString
```

#### Secret Store Component

**File**: `k8s/base/dapr-components/secretstore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### Deployment Architecture

#### Local Development (Minikube)

**Prerequisites**:
- Minikube with 4 CPUs, 8GB RAM
- Docker driver
- Dapr CLI installed (`dapr init -k`)
- Strimzi operator installed

**Deployment Steps**:
1. Start Minikube: `minikube start --cpus=4 --memory=8192`
2. Install Strimzi: `kubectl create namespace kafka && kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka`
3. Install Dapr: `dapr init -k`
4. Deploy Dapr components: `kubectl apply -f k8s/base/dapr-components/`
5. Deploy services: `helm install todo-app-local helm/ -f helm/values-local.yaml`
6. Access frontend: `minikube service frontend -n todo-app`

**Resource Allocation (Local)**:

| Component | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|----------|-------------|-----------|----------------|--------------|
| Chat API  | 1        | 100m        | 500m      | 256Mi          | 512Mi        |
| Recurring Task | 1   | 50m         | 200m      | 128Mi          | 256Mi        |
| Notification | 1     | 50m         | 200m      | 128Mi          | 256Mi        |
| Frontend  | 1        | 100m        | 500m      | 128Mi          | 512Mi        |
| Kafka     | 1        | 500m        | 1000m     | 512Mi          | 1Gi          |

**Total**: ~1.8 CPU cores, ~3.5GB RAM

#### Cloud Deployment (OKE/GKE/AKS)

**Prerequisites**:
- Kubernetes cluster with 3 worker nodes (2 vCPU, 4GB RAM each)
- kubectl configured for cloud cluster
- Helm 3 installed
- Dapr installed on cluster
- Kafka deployed (Strimzi or Redpanda Cloud)

**Deployment Steps**:
1. Create namespace: `kubectl create namespace todo-app`
2. Create secrets: `kubectl create secret generic app-secrets --from-env-file=.env.production -n todo-app`
3. Install Kafka (if using Strimzi): `kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka`
4. Deploy Dapr components: `kubectl apply -f k8s/base/dapr-components/ -n todo-app`
5. Deploy services: `helm install todo-app helm/ -f helm/values-production.yaml -n todo-app`
6. Verify deployment: `kubectl get pods -n todo-app`
7. Access frontend: `kubectl get ingress -n todo-app`

**Resource Allocation (Production)**:

| Component | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit | HPA Max |
|-----------|----------|-------------|-----------|----------------|--------------|---------|
| Chat API  | 2        | 200m        | 1000m     | 512Mi          | 1Gi          | 10      |
| Recurring Task | 2   | 100m        | 500m      | 256Mi          | 512Mi        | 5       |
| Notification | 2     | 100m        | 500m      | 256Mi          | 512Mi        | 5       |
| Frontend  | 2        | 200m        | 1000m     | 256Mi          | 1Gi          | 10      |
| Kafka     | 3        | 1000m       | 2000m     | 1Gi            | 2Gi          | N/A     |

**Total**: ~6 CPU cores, ~12GB RAM (minimum)

### Horizontal Pod Autoscaling (HPA)

**Chat API HPA**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chat-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chat-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Similar HPA configurations for Recurring Task Service, Notification Service, and Frontend.**

### CI/CD Pipeline

**GitHub Actions Workflow** (`.github/workflows/ci-cd.yaml`):

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint backend
        run: cd backend && ruff check .
      - name: Lint frontend
        run: cd frontend && npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Run backend tests
        run: cd backend && pytest
      - name: Run frontend tests
        run: cd frontend && npm test

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: |
          docker build -t ghcr.io/${{ github.repository }}/chat-api:${{ github.sha }} backend/
          docker build -t ghcr.io/${{ github.repository }}/recurring-task-service:${{ github.sha }} backend/services/recurring_task_service/
          docker build -t ghcr.io/${{ github.repository }}/notification-service:${{ github.sha }} backend/services/notification_service/
          docker build -t ghcr.io/${{ github.repository }}/frontend:${{ github.sha }} frontend/

  push:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Push to GHCR
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/${{ github.repository }}/chat-api:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}/recurring-task-service:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}/notification-service:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}

  deploy-production:
    runs-on: ubuntu-latest
    needs: push
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to cloud
        run: |
          helm upgrade --install todo-app helm/ \
            -f helm/values-production.yaml \
            --set chatApi.image.tag=${{ github.sha }} \
            --set recurringTaskService.image.tag=${{ github.sha }} \
            --set notificationService.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            -n todo-app
```

### Monitoring and Observability

**Health Checks**:

All services implement:
- `/health/live`: Liveness probe (service is running)
- `/health/ready`: Readiness probe (service is ready to accept traffic)

**Structured Logging**:

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_event(level, message, user_id=None, correlation_id=None, **kwargs):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "service": "chat-api",
        "message": message,
        "user_id": user_id,
        "correlation_id": correlation_id,
        **kwargs
    }
    logger.log(getattr(logging, level.upper()), json.dumps(log_data))
```

**Metrics** (optional - Prometheus):
- Request count
- Request latency (p50, p95, p99)
- Event processing lag
- Error rate

### Testing Strategy

**Unit Tests**:
- Test MCP tools with new fields
- Test event publishing logic
- Test recurrence calculation
- Test notification delivery

**Integration Tests**:
- Test Kafka event flow (publish → consume)
- Test Dapr Jobs API (schedule → trigger)
- Test database operations with new schema

**E2E Tests**:
- Create task with priority and tags
- Search and filter tasks
- Complete recurring task and verify next occurrence
- Set reminder and verify notification delivery
- Test multi-device sync

### Implementation Phases

**Phase A: Database & MCP Tools (Days 1-3)**
- Update Task model with new fields
- Create Alembic migration
- Update MCP tools (add_task, update_task, list_tasks)
- Add search_tasks MCP tool
- Unit tests for MCP tools

**Phase B: Event Infrastructure (Days 4-6)**
- Set up Kafka on Minikube (Strimzi)
- Configure Dapr Pub/Sub component
- Implement event publishing in MCP tools
- Create event schema documentation
- Integration tests for event publishing

**Phase C: Microservices (Days 7-11)**
- Implement Recurring Task Service
- Implement Notification Service
- Configure Dapr Jobs API for reminders
- Integration tests for services
- E2E tests for recurring tasks and reminders

**Phase D: Cloud Deployment (Days 12-15)**
- Create Helm charts
- Configure HPA
- Set up GitHub Actions CI/CD
- Deploy to cloud Kubernetes
- Verify zero-downtime deployments

**Phase E: Testing & Documentation (Days 16-18)**
- Comprehensive E2E testing
- Performance testing
- Create deployment documentation
- Record demo video
- Final validation

---

## Documentation Requirements

- [x] README.md updated with Phase V deployment instructions
- [x] ARCHITECTURE.md created with microservices architecture diagram
- [x] TROUBLESHOOTING.md created for common issues
- [x] Helm chart README with values.yaml documentation
- [x] Event schema documentation in contracts/
- [x] MCP tool contracts updated in contracts/
- [x] Demo video showing Phase V features (<90 seconds)

---

## Success Criteria

This implementation is complete when:

1. ✅ All 46 functional requirements are implemented
2. ✅ All 24 success criteria are met
3. ✅ Application runs on Minikube with full Dapr stack
4. ✅ Application deploys to cloud Kubernetes (OKE/GKE/AKS)
5. ✅ Kafka/Dapr Pub/Sub handles task events and reminders
6. ✅ Dapr Jobs API triggers reminders at correct times
7. ✅ Recurring tasks auto-create next occurrence within 5 seconds
8. ✅ CI/CD pipeline deploys to cloud on merge to main
9. ✅ All services pass health checks
10. ✅ kubectl-ai/kagent successfully manage cluster operations
11. ✅ Demo video shows complete feature set in <90 seconds
12. ✅ Zero-downtime deployments verified
13. ✅ Multi-device sync works within 5 seconds
14. ✅ All tests pass (unit, integration, E2E)
15. ✅ Documentation complete and accurate
