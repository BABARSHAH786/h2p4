# 🤖 Todo Chatbot Application

[![Phase](https://img.shields.io/badge/Phase-IV-blue.svg)](https://github.com/yourusername/hackathon-todo)
[![Status](https://img.shields.io/badge/Status-Kubernetes%20Ready-success.svg)](https://github.com/yourusername/hackathon-todo)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Hackathon II - The Evolution of Todo**
> From traditional task management to intelligent conversational AI, now deployed on Kubernetes for cloud-native scalability.

## 🎯 Overview

A full-stack todo application with AI-powered chatbot capabilities, now containerized and ready for Kubernetes deployment. Built with Next.js, FastAPI, OpenAI, and deployed using Helm charts on local or cloud Kubernetes clusters.

### 🌟 What Makes This Special?

- **Natural Language Interface**: Talk to your todo list like a personal assistant
- **Real-Time Database Operations**: All changes persist immediately to PostgreSQL
- **Cloud-Native Architecture**: Containerized microservices with Kubernetes orchestration
- **Horizontal Scalability**: Scale frontend and backend independently
- **Zero-Downtime Deployments**: Rolling updates with health checks
- **Production-Ready**: Helm charts, monitoring, and comprehensive documentation

---

## ✨ Features

### Phase IV: Kubernetes Deployment (Current)

#### 🐳 Containerization
- **Multi-stage Docker builds**: Optimized images (Frontend < 100MB, Backend < 200MB)
- **Non-root containers**: Security-first with UID 1001
- **Health checks**: Liveness and readiness probes for all services
- **Resource limits**: CPU and memory constraints prevent exhaustion

#### ☸️ Kubernetes Resources
- **Namespace isolation**: Dedicated `todo-app` namespace
- **Deployments**: Frontend (2 replicas), Backend (2 replicas)
- **Services**: NodePort for frontend, ClusterIP for backend
- **ConfigMaps**: Separate configuration from code
- **Secrets**: Secure storage for sensitive data

#### 📦 Helm Chart
- **Reproducible deployments**: Version-controlled infrastructure
- **Parameterized configuration**: Customize via values.yaml
- **Rolling updates**: Zero-downtime deployments
- **Rollback capability**: Instant recovery from failures

#### 🔧 DevOps Tools
- **Automated scripts**: Build, deploy, and cleanup with one command
- **Comprehensive docs**: Architecture, troubleshooting, and quickstart guides
- **Monitoring ready**: Kubernetes dashboard and metrics integration

### Phase III: AI-Powered Chatbot

#### 🗣️ Conversational Task Management
- **Natural Language Processing**: Commands like "Add groceries" or "Show pending tasks"
- **Context-Aware Responses**: AI remembers conversation flow
- **Action Confirmation**: Friendly confirmations with specific details

#### 🔧 MCP Tools Implementation
Five production-ready tools:
1. **`add_task`** - Create new tasks
2. **`list_tasks`** - Query and filter tasks
3. **`complete_task`** - Mark tasks complete
4. **`update_task`** - Modify task details
5. **`delete_task`** - Remove tasks

#### 💾 Stateless Architecture
- Full conversation history from database
- No in-memory session storage
- Horizontal scalability ready
- Server restarts don't lose data

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI Library**: OpenAI ChatKit
- **Authentication**: Better Auth with JWT
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Container**: node:20-alpine

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **AI Integration**: OpenAI Agents SDK
- **MCP**: Official Python MCP SDK
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Container**: python:3.13-slim

### Infrastructure
- **Orchestration**: Kubernetes (Minikube local, cloud-ready)
- **Package Manager**: Helm 3.13+
- **Container Runtime**: Docker Desktop 4.53+
- **Monitoring**: Kubernetes Dashboard, metrics-server

---

## 🚀 Quick Start

### Option 1: Kubernetes Deployment (Recommended)

**Prerequisites:**
- Docker Desktop 4.53+
- Minikube 1.32+
- kubectl 1.28+
- Helm 3.13+
- 4 CPU cores, 8GB RAM

**One-Command Deployment:**

```bash
# Set your secrets
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
export BETTER_AUTH_SECRET="your-secret-key"
export OPENAI_API_KEY="sk-your-openai-key"

# Deploy everything
./scripts/deploy-all.sh

# Access the application
minikube service frontend-service -n todo-app
```

**Manual Deployment:**

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Build Docker images
./scripts/build-images.sh

# 3. Load images to Minikube
./scripts/load-images.sh

# 4. Deploy with Helm
./scripts/deploy.sh

# 5. Access application
minikube service frontend-service -n todo-app
```

📖 **Detailed Guide**: See [docs/QUICKSTART.md](docs/QUICKSTART.md)

### Option 2: Local Development

**Backend:**
```bash
cd backend
uv sync
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📚 Documentation

### Kubernetes Deployment
- **[Quickstart Guide](docs/QUICKSTART.md)** - Get running in 10 minutes
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Helm Chart](k8s/helm-chart/README.md)** - Advanced configuration

### Application
- **[API Documentation](backend/README.md)** - Backend API reference
- **[Frontend Guide](frontend/README.md)** - UI components and features

---

## 🏗️ Architecture

### Kubernetes Architecture

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
│  │  │  └────────────┘      └────────────┘         │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                       ↓                             │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         Backend (ClusterIP)                  │  │    │
│  │  │  ┌────────────┐      ┌────────────┐         │  │    │
│  │  │  │  Pod 1     │      │  Pod 2     │         │  │    │
│  │  │  │ FastAPI    │      │ FastAPI    │         │  │    │
│  │  │  └────────────┘      └────────────┘         │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    External Database
                  (Neon PostgreSQL)
```

---

## 🔧 Common Operations

### Scaling

```bash
# Scale backend to 4 replicas
kubectl scale deployment backend-deployment --replicas=4 -n todo-app

# Scale frontend to 3 replicas
kubectl scale deployment frontend-deployment --replicas=3 -n todo-app
```

### Monitoring

```bash
# View logs
kubectl logs -f deployment/backend-deployment -n todo-app

# Resource usage
kubectl top pods -n todo-app

# Open dashboard
minikube dashboard
```

### Configuration Updates

```bash
# Update ConfigMap
kubectl edit configmap backend-config -n todo-app

# Restart pods to apply changes
kubectl rollout restart deployment/backend-deployment -n todo-app
```

### Cleanup

```bash
# Remove application
./scripts/cleanup.sh

# Stop Minikube
minikube stop
```

---

## 📊 Performance

**Deployment Metrics:**
- Deployment time: < 5 minutes
- Container startup: < 60 seconds
- Scaling time: < 60 seconds (zero downtime)
- Rolling update: < 2 minutes (zero downtime)

**Resource Usage** (baseline 2+2 replicas):
- CPU: ~1.3 cores (requests), ~5 cores (limits)
- Memory: ~1.5Gi (requests), ~5.5Gi (limits)

---

## 🔐 Security

- **Non-root containers**: All services run as UID 1001
- **Secrets management**: Kubernetes Secrets with base64 encoding
- **Network isolation**: ClusterIP for internal services
- **Resource limits**: Prevent resource exhaustion attacks
- **JWT authentication**: Secure user sessions
- **CORS configuration**: Controlled cross-origin access

---

## 🛣️ Roadmap

### Phase V: Cloud Deployment (Planned)
- [ ] Cloud deployment (Azure/GCP/AWS)
- [ ] Ingress controller with TLS/HTTPS
- [ ] Horizontal Pod Autoscaler (HPA)
- [ ] Persistent volume provisioning
- [ ] Monitoring stack (Prometheus + Grafana)
- [ ] Service mesh (Istio)
- [ ] CI/CD pipeline integration

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o-mini and Agents SDK
- **Anthropic** - Model Context Protocol (MCP)
- **Neon** - Serverless PostgreSQL
- **Kubernetes** - Container orchestration
- **Helm** - Package management

---

## 📞 Support

- **Documentation**: Check [docs/](docs/) directory
- **Issues**: Report bugs via GitHub Issues
- **Troubleshooting**: See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**🎉 Ready to deploy?** Start with the [Quickstart Guide](docs/QUICKSTART.md)!
