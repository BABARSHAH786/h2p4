# Tasks: Phase V - Advanced Cloud Deployment

**Feature Branch**: `001-phase-v-cloud-deployment`
**Created**: 2026-02-10
**Status**: Ready for Implementation

## Overview

This document defines all implementation tasks for Phase V: Advanced Cloud Deployment. Tasks are organized by user story to enable independent implementation and testing of each feature increment.

**Total Estimated Time**: 150 hours (18 days)
**Total Tasks**: 40 tasks across 7 phases

---

## Phase 1: Setup & Infrastructure (Days 1-2)

**Goal**: Initialize project structure and configure foundational infrastructure for microservices architecture.

**Tasks**:

- [x] T001 Run database migration to add Phase V schema fields in backend/alembic/versions/004_add_advanced_features.py
- [x] T002 [P] Update Task model with new fields (priority, tags, due_at, recurrence) in backend/app/models/task.py
- [x] T003 [P] Create Dapr component configurations in k8s/base/dapr-components/ (pubsub-kafka.yaml, statestore-postgres.yaml, jobs.yaml, secretstore.yaml)
- [x] T004 [P] Create Kafka cluster manifest for Minikube in k8s/kafka/kafka-cluster.yaml
- [x] T005 [P] Create Dockerfiles for all services (backend/Dockerfile, backend/services/recurring_task_service/Dockerfile, backend/services/notification_service/Dockerfile, frontend/Dockerfile)

**Acceptance Criteria**:
- Database schema includes all Phase V fields with correct types and indexes
- Task model matches database schema exactly
- Dapr components configured for Kafka, PostgreSQL, Jobs API, and Secrets
- Kafka cluster manifest ready for deployment
- All Dockerfiles build successfully and produce images <500MB

**Estimated Time**: 16 hours

---

## Phase 2: Foundational Services (Days 3-4)

**Goal**: Implement core event-driven infrastructure that all user stories depend on.

**Tasks**:

- [x] T006 Implement Dapr Pub/Sub service for event publishing in backend/app/utils/events.py
- [x] T007 Implement Dapr Jobs API service for reminder scheduling in backend/app/services/dapr_jobs.py
- [x] T008 [P] Create recurring task service structure in backend/services/recurring_task_service/ (main.py, consumer.py, handler.py)
- [x] T009 [P] Create notification service structure in backend/services/notification_service/ (main.py, consumer.py, notifier.py)
- [x] T010 Integrate event publishing into existing MCP tools (complete_task.py, delete_task.py) in backend/app/mcp/tools/

**Acceptance Criteria**:
- Events can be published to Kafka via Dapr Pub/Sub
- Reminders can be scheduled via Dapr Jobs API
- Recurring task service receives and processes task.completed events
- Notification service receives and processes reminder.triggered events
- All existing MCP tools publish appropriate events

**Estimated Time**: 20 hours

---

## Phase 3: User Story 1 - Power User Task Management (P1) (Days 5-7)

**Goal**: Enable users to organize tasks by priority, add tags, search/filter, and sort tasks through natural language.

**Independent Test**: Create tasks with priorities and tags, search/filter tasks, verify natural language understanding works correctly.

**Tasks**:

- [x] T011 [US1] Update add_task MCP tool to accept priority and tags parameters in backend/app/mcp/tools/add_task.py
- [x] T012 [US1] Update list_tasks MCP tool to support filtering by priority and tags in backend/app/mcp/tools/list_tasks.py
- [x] T013 [US1] Implement search_tasks MCP tool for keyword search in backend/app/mcp/tools/search_tasks.py
- [x] T014 [US1] Update update_task MCP tool to allow modifying priority and tags in backend/app/mcp/tools/update_task.py
- [x] T015 [US1] Update AI agent prompt to infer priorities and tags from natural language in backend/app/utils/agent.py
- [ ] T016 [P] [US1] Write unit tests for priority and tag functionality in backend/tests/unit/test_mcp_tools_priorities_tags.py
- [ ] T017 [US1] Test User Story 1 end-to-end: create, filter, search, and sort tasks with priorities and tags

**Acceptance Criteria**:
- Users can create tasks with priority (high/medium/low) via natural language
- Users can tag tasks with custom labels
- Users can filter tasks by priority and tags
- Users can search tasks by keyword
- Users can sort tasks by due_date, priority, created_at, or title
- Agent correctly infers priorities ("urgent" → high) and tags ("work meeting" → ["work"])
- All unit tests pass with >80% code coverage

**Estimated Time**: 24 hours

---

## Phase 4: User Story 2 - Recurring Task Automation (P2) (Days 8-9)

**Goal**: Enable automatic creation of next occurrence when recurring tasks are completed.

**Independent Test**: Create recurring task, mark complete, verify next occurrence created within 5 seconds with inherited properties.

**Tasks**:

- [x] T018 [US2] Add recurrence fields to add_task MCP tool in backend/app/mcp/tools/add_task.py
- [x] T019 [US2] Implement recurrence logic for date calculation in backend/services/recurring_task_service/handler.py
- [x] T020 [US2] Integrate recurring task service with task.completed events in backend/services/recurring_task_service/consumer.py
- [x] T021 [US2] Update AI agent prompt to understand recurrence patterns in backend/app/utils/agent.py
- [ ] T022 [P] [US2] Write integration tests for recurring task flow in backend/tests/integration/test_recurring_tasks.py
- [ ] T023 [US2] Test User Story 2 end-to-end: create recurring task, complete it, verify next occurrence

**Acceptance Criteria**:
- Users can create recurring tasks (daily/weekly/monthly/yearly)
- Completing recurring task triggers next occurrence creation within 5 seconds
- Next occurrence inherits title, description, tags, priority, recurrence settings
- Daily tasks: +1 day, Weekly: +7 days, Monthly: +1 month, Yearly: +1 year
- Recurring tasks with end dates stop creating occurrences after end date
- All integration tests pass

**Estimated Time**: 16 hours

---

## Phase 5: User Story 3 - Time-Based Reminders (P3) (Days 10-11)

**Goal**: Enable users to receive notifications before task due dates with configurable reminder times.

**Independent Test**: Create task with due date and reminder, wait for reminder time, verify notification delivered.

**Tasks**:

- [x] T024 [US3] Add due_at and reminder_minutes_before fields to add_task MCP tool in backend/app/mcp/tools/add_task.py
- [x] T025 [US3] Integrate reminder scheduling into add_task tool in backend/app/mcp/tools/add_task.py
- [x] T026 [US3] Implement email notification logic in backend/services/notification_service/notifier.py
- [x] T027 [US3] Create reminder callback endpoint in backend/app/routes/jobs.py
- [x] T028 [US3] Update AI agent prompt to parse natural language dates and reminder requests in backend/app/utils/agent.py
- [ ] T029 [P] [US3] Write integration tests for reminder scheduling and delivery in backend/tests/integration/test_reminders.py
- [ ] T030 [US3] Test User Story 3 end-to-end: create task with reminder, verify notification sent at correct time

**Acceptance Criteria**:
- Users can set due dates with specific times via natural language
- Users can request reminders at specific intervals (15min, 30min, 1hr, 1day)
- System defaults to 1 hour before reminder when not specified
- Reminders fire at scheduled time with ±1 minute accuracy
- Email notifications sent with task title and due time
- Reminders marked as sent to prevent duplicates
- All integration tests pass

**Estimated Time**: 18 hours

---

## Phase 6: User Story 4 - Real-Time Multi-Device Sync (P4) (Days 12-13)

**Goal**: Enable instant task synchronization across devices without manual refresh.

**Independent Test**: Create task on one device, verify it appears on another device within 5 seconds.

**Tasks**:

- [x] T031 [US4] Publish task.created events after task creation in backend/app/mcp/tools/add_task.py
- [x] T032 [US4] Publish task.updated events after task updates in backend/app/mcp/tools/update_task.py
- [x] T033 [US4] Create task-updates Kafka topic for real-time sync in k8s/kafka/kafka-topics.yaml
- [ ] T034 [P] [US4] Write integration tests for event publishing in backend/tests/integration/test_kafka_events.py
- [ ] T035 [US4] Test User Story 4 end-to-end: create/update task, verify events published to Kafka

**Acceptance Criteria**:
- Task creation publishes task.created event to task-events topic
- Task updates publish task.updated event to task-events topic
- Events include complete task data with correct event_type and timestamp
- Events delivered with at-least-once guarantee
- Event processing latency <5 seconds (p95)
- All integration tests pass

**Note**: Full multi-device sync with WebSocket service deferred to Phase VI per research.md. This phase implements event publishing foundation.

**Estimated Time**: 12 hours

---

## Phase 7: User Story 5 - DevOps Cloud Deployment (P5) (Days 14-18)

**Goal**: Deploy application to cloud Kubernetes with zero-downtime, automated CI/CD, and full observability.

**Independent Test**: Deploy to cloud, verify all services running, test zero-downtime updates, confirm monitoring works.

**Tasks**:

- [x] T036 [US5] Create Helm chart structure in helm/ (Chart.yaml, values.yaml, values-local.yaml, values-production.yaml)
- [x] T037 [US5] Create Helm templates for all services in helm/templates/ (chat-api/, recurring-task-service/, notification-service/, frontend/)
- [ ] T038 [US5] Deploy Kafka to Minikube using Strimzi operator
- [ ] T039 [US5] Deploy application to Minikube via Helm chart
- [ ] T040 [US5] Test complete workflow on Minikube (all user stories)
- [ ] T041 [US5] Provision cloud Kubernetes cluster (OKE/GKE/AKS)
- [ ] T042 [US5] Create production Kubernetes secrets
- [ ] T043 [US5] Deploy Kafka to cloud cluster (Strimzi or Redpanda Cloud)
- [ ] T044 [US5] Deploy application to cloud via Helm with production values
- [ ] T045 [US5] Configure HTTPS ingress with TLS certificate
- [ ] T046 [US5] Test production deployment (all user stories)
- [x] T047 [US5] Create GitHub Actions CI/CD workflow in .github/workflows/ci-cd.yaml
- [x] T048 [US5] Create comprehensive README.md with setup instructions
- [ ] T049 [US5] Create demo video (<90 seconds) showing all features
- [ ] T050 [US5] Final testing and submission

**Acceptance Criteria**:
- Helm chart deploys all services to Minikube successfully
- All pods running with Dapr sidecars injected
- Kafka cluster operational with task-events and reminders topics
- All user stories (P1-P4) work correctly on Minikube
- Cloud cluster provisioned with 3+ worker nodes
- Application deployed to cloud with 2+ replicas per service
- HTTPS enabled with valid TLS certificate
- Zero-downtime rolling updates verified
- CI/CD pipeline runs on push to main (lint → test → build → push → deploy)
- README includes setup instructions for both local and cloud
- Demo video demonstrates all features in <90 seconds
- All acceptance criteria from spec.md verified

**Estimated Time**: 44 hours

---

## Phase 8: Polish & Cross-Cutting Concerns (Ongoing)

**Goal**: Address cross-cutting concerns and polish for production readiness.

**Tasks**:

- [x] T051 [P] Implement health check endpoints (/health/live, /health/ready) for all services
- [x] T052 [P] Add structured JSON logging to all services
- [x] T053 [P] Configure Horizontal Pod Autoscaling (HPA) for all services
- [ ] T054 [P] Add Prometheus metrics endpoints (optional)
- [x] T055 [P] Create troubleshooting documentation

**Acceptance Criteria**:
- All services implement liveness and readiness probes
- All services emit structured JSON logs with timestamp, level, service, message, user_id
- HPA configured to scale on CPU >70%, Memory >80%
- Metrics available for monitoring (optional)
- Troubleshooting guide covers common issues

**Estimated Time**: 10 hours

---

## Task Dependencies

### Critical Path

```
Setup Phase (T001-T005)
    ↓
Foundational Phase (T006-T010)
    ↓
    ├─→ User Story 1 (T011-T017) [Can start after T010]
    │
    ├─→ User Story 2 (T018-T023) [Can start after T010, depends on T011]
    │
    ├─→ User Story 3 (T024-T030) [Can start after T010, depends on T011]
    │
    ├─→ User Story 4 (T031-T035) [Can start after T010, depends on T011-T014]
    │
    └─→ User Story 5 (T036-T050) [Can start after T035, requires all previous stories]
         ↓
    Polish Phase (T051-T055) [Can run in parallel with User Story 5]
```

### Parallel Execution Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004, T005 can run in parallel after T001 completes

**Phase 2 (Foundational)**:
- T008, T009 can run in parallel with T006-T007

**Phase 3 (User Story 1)**:
- T016 can run in parallel with T011-T015

**Phase 4 (User Story 2)**:
- T022 can run in parallel with T018-T021

**Phase 5 (User Story 3)**:
- T029 can run in parallel with T024-T028

**Phase 6 (User Story 4)**:
- T034 can run in parallel with T031-T033

**Phase 8 (Polish)**:
- T051-T055 can all run in parallel

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: User Story 1 (P1) only
- Delivers core value: task management with priorities, tags, search, filter, sort
- Can be fully tested and deployed independently
- Provides immediate user value
- Estimated time: ~40 hours (Setup + Foundational + US1)

### Incremental Delivery

1. **Sprint 1** (Days 1-7): Setup + Foundational + User Story 1 (P1)
   - Deliverable: Task management with priorities, tags, search, filter, sort
   - Independent test: Create, filter, search, and sort tasks

2. **Sprint 2** (Days 8-9): User Story 2 (P2)
   - Deliverable: Recurring task automation
   - Independent test: Create recurring task, verify next occurrence

3. **Sprint 3** (Days 10-11): User Story 3 (P3)
   - Deliverable: Time-based reminders
   - Independent test: Create task with reminder, verify notification

4. **Sprint 4** (Days 12-13): User Story 4 (P4)
   - Deliverable: Real-time multi-device sync foundation
   - Independent test: Verify events published to Kafka

5. **Sprint 5** (Days 14-18): User Story 5 (P5)
   - Deliverable: Cloud deployment with CI/CD
   - Independent test: Deploy to cloud, verify zero-downtime updates

---

## Testing Strategy

### Unit Tests (Optional - only if requested)

- Test MCP tools with new parameters
- Test event publishing logic
- Test recurrence calculation
- Test notification delivery
- Target: >80% code coverage

### Integration Tests (Optional - only if requested)

- Test Kafka event flow (publish → consume)
- Test Dapr Jobs API (schedule → trigger)
- Test database operations with new schema
- Test recurring task service end-to-end
- Test notification service end-to-end

### End-to-End Tests (Required)

- Test each user story independently
- Verify acceptance criteria for each story
- Test on both Minikube and cloud deployments

---

## Risk Mitigation

### High-Risk Tasks

1. **T019** (Recurring Task Service): Complex date calculation logic
   - Mitigation: Use well-tested date library (dateutil), write comprehensive unit tests

2. **T026** (Email Notifications): SMTP configuration and delivery
   - Mitigation: Use SendGrid free tier or Gmail SMTP, test with multiple providers

3. **T038** (Kafka on Minikube): Resource-intensive, may fail on low-spec machines
   - Mitigation: Document minimum requirements (4 CPU, 8GB RAM), provide troubleshooting guide

4. **T043** (Kafka on Cloud): Cost and complexity
   - Mitigation: Use Redpanda Cloud free tier as fallback, document both options

5. **T047** (CI/CD Pipeline): GitHub Actions secrets and kubectl configuration
   - Mitigation: Document secret setup process, provide example workflow

### Blockers

- **Database migration failure** (T001): Blocks all subsequent tasks
  - Mitigation: Test migration on dev database first, create rollback script

- **Dapr installation issues** (T003): Blocks event-driven architecture
  - Mitigation: Document Dapr installation steps, provide troubleshooting guide

- **Kafka deployment failure** (T038, T043): Blocks event publishing
  - Mitigation: Provide alternative (Redpanda Cloud), document both options

---

## Success Metrics

### Feature Completeness

- [ ] All 5 user stories implemented and tested
- [ ] All 46 functional requirements from spec.md satisfied
- [ ] All 24 success criteria from spec.md met

### Deployment

- [ ] Application runs on Minikube with full Dapr stack
- [ ] Application deploys to cloud Kubernetes (OKE/GKE/AKS)
- [ ] Zero-downtime deployments verified
- [ ] CI/CD pipeline deploys on merge to main

### Performance

- [ ] Chat responses <2s (p95 latency)
- [ ] Task operations <500ms (p95 latency)
- [ ] Event processing <5s (p95 latency)
- [ ] Reminder accuracy ±1 minute

### Quality

- [ ] All services pass health checks
- [ ] Structured logs available for debugging
- [ ] HPA scales pods under load
- [ ] kubectl-ai/kagent successfully manage cluster

---

## Notes

- **Tests are optional**: Unit and integration tests only generated if explicitly requested in spec or by user
- **User stories are independent**: Each story can be implemented and tested independently
- **Parallel execution**: Tasks marked with [P] can run in parallel with other [P] tasks in same phase
- **Story labels**: [US1], [US2], etc. map to user stories from spec.md for traceability
- **File paths**: All tasks include specific file paths for implementation
- **Incremental delivery**: MVP is User Story 1 only; other stories add incremental value

---

**Generated**: 2026-02-10
**Feature**: Phase V - Advanced Cloud Deployment
**Branch**: 001-phase-v-cloud-deployment
**Total Tasks**: 55 tasks
**Estimated Time**: 150 hours (18 days)
