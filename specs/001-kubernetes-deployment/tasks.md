# Tasks: Phase IV - Local Kubernetes Deployment

**Input**: Design documents from `/specs/001-kubernetes-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are minimal and focused on validation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `k8s/`
- Kubernetes manifests in `k8s/` directory
- Helm chart in `k8s/helm-chart/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Local Kubernetes environment initialization and project structure

- [ ] T001 Install and configure Minikube with 4 CPU, 8GB RAM, docker driver
- [ ] T002 Enable Minikube addons: ingress, metrics-server, dashboard
- [ ] T003 Verify Minikube cluster is operational with kubectl cluster-info
- [ ] T004 Install Helm 3.13+ and verify installation with helm version
- [ ] T005 [P] Configure Docker Desktop 4.53+ and enable Gordon (Beta Features)
- [ ] T006 [P] Install kubectl-ai CLI tool and configure OpenAI API key (optional)
- [ ] T007 Create k8s/ directory structure for Kubernetes manifests
- [ ] T008 Create k8s/helm-chart/ directory structure for Helm templates

**Checkpoint**: Local Kubernetes environment ready for deployment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Create frontend/.dockerignore excluding node_modules, .next, .git
- [x] T010 [P] Create backend/.dockerignore excluding __pycache__, .venv, *.pyc, .git
- [x] T011 Create k8s/namespace.yaml defining todo-app namespace
- [x] T012 Create k8s/config/app-secrets.yaml template for DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - First-Time Local Cluster Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy Phase III Todo Chatbot to local Kubernetes cluster with all components running as containerized services

**Independent Test**: Start Minikube, deploy all components, access frontend via NodePort, verify signup/task management/chatbot functionality works identically to Phase III

### Implementation for User Story 1

#### Containerization

- [x] T013 [P] [US1] Create frontend/Dockerfile with multi-stage build (node:20-alpine base, non-root user UID 1001)
- [x] T014 [P] [US1] Create backend/Dockerfile with multi-stage build (python:3.13-slim base, UV package manager, non-root user UID 1001)
- [x] T015 [P] [US1] Add health check endpoint GET /health to backend/app/main.py (already exists)
- [ ] T016 [US1] Build frontend Docker image: docker build -t todo-frontend:1.0.0 ./frontend
- [ ] T017 [US1] Build backend Docker image: docker build -t todo-backend:1.0.0 ./backend
- [ ] T018 [P] [US1] Test frontend container locally: docker run -p 3000:3000 todo-frontend:1.0.0
- [ ] T019 [P] [US1] Test backend container locally: docker run -p 8000:8000 todo-backend:1.0.0
- [ ] T020 [US1] Verify frontend image size < 100MB and backend < 200MB
- [ ] T021 [US1] Load frontend image to Minikube: minikube image load todo-frontend:1.0.0
- [ ] T022 [US1] Load backend image to Minikube: minikube image load todo-backend:1.0.0
- [ ] T023 [US1] Verify images in Minikube: minikube image ls | grep todo

#### Kubernetes Deployments

- [x] T024 [P] [US1] Create k8s/deployments/frontend-deployment.yaml (2 replicas, health probes, resource limits)
- [x] T025 [P] [US1] Create k8s/deployments/backend-deployment.yaml (2 replicas, health probes, resource limits)
- [ ] T026 [P] [US1] Create k8s/deployments/postgres-deployment.yaml (1 replica, PVC for data) if using in-cluster database

#### Kubernetes Services

- [x] T027 [P] [US1] Create k8s/services/frontend-service.yaml (NodePort 30080, port 3000)
- [x] T028 [P] [US1] Create k8s/services/backend-service.yaml (ClusterIP, port 8000)
- [ ] T029 [P] [US1] Create k8s/services/postgres-service.yaml (ClusterIP, port 5432) if using in-cluster database

#### Configuration Management

- [x] T030 [P] [US1] Create k8s/config/frontend-configmap.yaml with API_URL and NEXT_PUBLIC_CHATKIT_ENABLED
- [x] T031 [P] [US1] Create k8s/config/backend-configmap.yaml with AGENT_MODEL, MAX_CONVERSATION_MESSAGES, CORS_ORIGINS
- [x] T032 [US1] Populate k8s/config/app-secrets.yaml with base64-encoded secrets

#### Deployment and Verification

- [ ] T033 [US1] Apply namespace: kubectl apply -f k8s/namespace.yaml
- [ ] T034 [US1] Apply secrets: kubectl apply -f k8s/config/app-secrets.yaml -n todo-app
- [ ] T035 [US1] Apply configmaps: kubectl apply -f k8s/config/ -n todo-app
- [ ] T036 [US1] Apply deployments: kubectl apply -f k8s/deployments/ -n todo-app
- [ ] T037 [US1] Apply services: kubectl apply -f k8s/services/ -n todo-app
- [ ] T038 [US1] Verify all pods are running: kubectl get pods -n todo-app -w
- [ ] T039 [US1] Verify all services are created: kubectl get svc -n todo-app
- [ ] T040 [US1] Get Minikube IP and access frontend at http://<minikube-ip>:30080
- [ ] T041 [US1] Test backend connectivity from frontend pod: kubectl exec -it <frontend-pod> -n todo-app -- curl backend-service:8000/health
- [ ] T042 [US1] Test database connectivity from backend pod (verify connection in logs)
- [ ] T043 [US1] End-to-end test: signup, create tasks via UI, create tasks via chatbot, verify data persists

**Checkpoint**: User Story 1 complete - Application fully deployed and functional on local Kubernetes cluster

---

## Phase 4: User Story 2 - Horizontal Scaling Under Load (Priority: P2)

**Goal**: Enable horizontal scaling of application components to handle increased load without downtime

**Independent Test**: Deploy application (US1), scale backend replicas from 2 to 4, verify new pods come online within 60 seconds, verify load distribution, verify zero downtime

### Implementation for User Story 2

- [ ] T044 [US2] Document scaling command in README.md: kubectl scale deployment backend-deployment --replicas=4 -n todo-app
- [ ] T045 [US2] Test scaling backend to 4 replicas and verify pods start within 60 seconds
- [ ] T046 [US2] Verify load distribution across all backend replicas using kubectl logs
- [ ] T047 [US2] Test scaling frontend to 3 replicas and verify zero downtime
- [ ] T048 [US2] Verify resource usage stays within limits: kubectl top pods -n todo-app
- [ ] T049 [US2] Test scaling down to 2 replicas and verify graceful termination
- [ ] T050 [US2] Document scaling best practices and resource monitoring in TROUBLESHOOTING.md

**Checkpoint**: User Story 2 complete - Horizontal scaling validated with zero downtime

---

## Phase 5: User Story 3 - Configuration Updates Without Redeployment (Priority: P2)

**Goal**: Enable configuration updates without rebuilding containers, with automatic rolling restart

**Independent Test**: Deploy application (US1), update ConfigMap values, verify services restart automatically with new configuration within 2 minutes

### Implementation for User Story 3

- [ ] T051 [US3] Update k8s/config/backend-configmap.yaml with new AGENT_MODEL value
- [ ] T052 [US3] Apply updated ConfigMap: kubectl apply -f k8s/config/backend-configmap.yaml -n todo-app
- [ ] T053 [US3] Trigger rolling restart: kubectl rollout restart deployment/backend-deployment -n todo-app
- [ ] T054 [US3] Verify rolling restart completes within 2 minutes with zero downtime
- [ ] T055 [US3] Verify new configuration is active by checking environment variables in pod
- [ ] T056 [US3] Test updating Secret values and verify secure handling (no plain-text exposure)
- [ ] T057 [US3] Document configuration update procedure in README.md
- [ ] T058 [US3] Create configuration validation script to check for invalid values before applying

**Checkpoint**: User Story 3 complete - Configuration updates work without container rebuilds

---

## Phase 6: User Story 4 - Reproducible Deployments Across Environments (Priority: P3)

**Goal**: Package entire deployment as reusable Helm chart with customizable parameters

**Independent Test**: Create Helm chart, deploy to fresh cluster with custom values, verify successful deployment, test upgrade and rollback

### Implementation for User Story 4

#### Helm Chart Structure

- [x] T059 [US4] Initialize Helm chart: helm create todo-app-chart in k8s/helm-chart/
- [x] T060 [US4] Create k8s/helm-chart/Chart.yaml with name: todo-app, version: 1.0.0, appVersion: 1.0.0
- [x] T061 [US4] Create k8s/helm-chart/.helmignore excluding unnecessary files

#### Helm Templates

- [x] T062 [P] [US4] Create k8s/helm-chart/templates/namespace.yaml with parameterized namespace
- [x] T063 [P] [US4] Create k8s/helm-chart/templates/deployment.yaml with parameterized deployments (frontend, backend, postgres)
- [x] T064 [P] [US4] Create k8s/helm-chart/templates/service.yaml with parameterized services
- [x] T065 [P] [US4] Create k8s/helm-chart/templates/configmap.yaml with parameterized ConfigMaps
- [x] T066 [P] [US4] Create k8s/helm-chart/templates/secret.yaml with parameterized Secrets
- [x] T067 [US4] Create k8s/helm-chart/templates/_helpers.tpl with common template functions

#### Helm Values

- [x] T068 [US4] Create k8s/helm-chart/values.yaml with all configurable parameters (replicas, images, resources, config, secrets)
- [x] T069 [US4] Document all values.yaml parameters with inline comments
- [x] T070 [US4] Set default values for namespace, replica counts, image tags, resource limits

#### Helm Testing

- [ ] T071 [US4] Test Helm chart with dry-run: helm install todo-app-local ./k8s/helm-chart --dry-run --debug
- [ ] T072 [US4] Uninstall previous kubectl deployment: kubectl delete namespace todo-app
- [ ] T073 [US4] Install via Helm: helm install todo-app-local ./k8s/helm-chart --set secrets.databaseUrl=<encoded> --set secrets.betterAuthSecret=<encoded> --set secrets.openaiApiKey=<encoded> -n todo-app --create-namespace
- [ ] T074 [US4] Verify Helm release: helm list -n todo-app
- [ ] T075 [US4] Verify all resources created: kubectl get all -n todo-app
- [ ] T076 [US4] Test Helm upgrade with changed values: helm upgrade todo-app-local ./k8s/helm-chart --set backend.replicaCount=3 -n todo-app
- [ ] T077 [US4] Verify upgrade completes with zero downtime: kubectl rollout status deployment/backend-deployment -n todo-app
- [ ] T078 [US4] Test Helm rollback: helm rollback todo-app-local -n todo-app
- [ ] T079 [US4] Verify rollback restores previous version within 1 minute
- [ ] T080 [US4] Test Helm uninstall: helm uninstall todo-app-local -n todo-app

**Checkpoint**: User Story 4 complete - Reproducible deployments via Helm chart validated

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final testing across all user stories

- [x] T081 [P] Update README.md with Kubernetes deployment instructions (prerequisites, setup, deployment, scaling, configuration updates, Helm usage)
- [x] T082 [P] Create ARCHITECTURE.md with Kubernetes architecture diagram (namespace, deployments, services, ConfigMaps, Secrets)
- [x] T083 [P] Create TROUBLESHOOTING.md for common Kubernetes issues (pod crashes, image pull errors, resource exhaustion, configuration errors)
- [x] T084 [P] Create k8s/helm-chart/README.md with Helm chart documentation (installation, configuration, upgrade, rollback)
- [x] T085 [P] Document AI DevOps tool usage in README.md (Gordon for Dockerfiles, kubectl-ai for deployments, kagent for analysis)
- [ ] T086 Test pod restart resilience: kubectl delete pod <pod-name> -n todo-app and verify auto-restart
- [ ] T087 Test data persistence: restart database pod and verify data intact
- [ ] T088 Test rolling updates: update image tag in Helm values and verify zero downtime deployment
- [ ] T089 Verify all health endpoints respond within 100ms
- [ ] T090 Verify logs are accessible within 5 seconds: kubectl logs <pod-name> -n todo-app
- [ ] T091 Verify total cluster resource usage < 4GB RAM and < 2 CPU cores for baseline deployment
- [ ] T092 Run complete end-to-end test covering all user stories (deploy, scale, update config, rollback)
- [ ] T093 Create quickstart guide for local Kubernetes setup in docs/QUICKSTART.md
- [ ] T094 Record demo video showing Kubernetes deployment process (optional)

**Checkpoint**: Phase IV complete - Application production-ready on local Kubernetes cluster

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - BLOCKS all other user stories
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (needs deployed application to scale)
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (needs deployed application to update config)
- **User Story 4 (Phase 6)**: Can start after User Story 1, but benefits from US2/US3 validation
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: FOUNDATIONAL - Must complete first. All other stories depend on this.
- **User Story 2 (P2)**: Depends on US1 (needs deployed application). Can run in parallel with US3.
- **User Story 3 (P2)**: Depends on US1 (needs deployed application). Can run in parallel with US2.
- **User Story 4 (P3)**: Depends on US1. Recommended to complete US2/US3 first for comprehensive Helm chart.

### Within Each User Story

- **US1**: Containerization → Kubernetes Resources → Deployment → Verification (sequential)
- **US2**: Deploy (US1) → Scale → Verify (sequential)
- **US3**: Deploy (US1) → Update Config → Verify (sequential)
- **US4**: Create Helm Chart → Test → Deploy → Upgrade → Rollback (sequential)

### Parallel Opportunities

- **Phase 1**: T005 and T006 can run in parallel
- **Phase 2**: T009 and T010 can run in parallel
- **US1 Containerization**: T013 and T014 can run in parallel; T018 and T019 can run in parallel
- **US1 Kubernetes Resources**: T024, T025, T026 can run in parallel; T027, T028, T029 can run in parallel; T030, T031 can run in parallel
- **US4 Helm Templates**: T062, T063, T064, T065, T066 can run in parallel
- **Phase 7**: T081, T082, T083, T084, T085 can run in parallel

---

## Parallel Example: User Story 1 - Kubernetes Resources

```bash
# Launch all deployment manifests together:
Task: "Create k8s/deployments/frontend-deployment.yaml"
Task: "Create k8s/deployments/backend-deployment.yaml"
Task: "Create k8s/deployments/postgres-deployment.yaml"

# Launch all service manifests together:
Task: "Create k8s/services/frontend-service.yaml"
Task: "Create k8s/services/backend-service.yaml"
Task: "Create k8s/services/postgres-service.yaml"

# Launch all config manifests together:
Task: "Create k8s/config/frontend-configmap.yaml"
Task: "Create k8s/config/backend-configmap.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T012)
3. Complete Phase 3: User Story 1 (T013-T043)
4. **STOP and VALIDATE**: Test User Story 1 independently - full deployment working
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test scaling → Deploy/Demo
4. Add User Story 3 → Test config updates → Deploy/Demo
5. Add User Story 4 → Test Helm chart → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once User Story 1 is complete:
   - Developer A: User Story 2 (scaling)
   - Developer B: User Story 3 (configuration)
   - Developer C: User Story 4 (Helm chart)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 1 is CRITICAL - all other stories depend on it
- Use AI DevOps tools (Gordon, kubectl-ai) to accelerate Dockerfile and manifest generation
- Always verify with dry-run before applying Kubernetes manifests
- Monitor resource usage throughout to stay within 4GB RAM / 2 CPU limits
- Test rollback procedures before considering deployment production-ready
