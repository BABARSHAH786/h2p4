---
id: 0002
title: phase-v-cloud-deployment-planning
stage: plan
date: 2026-02-10
surface: agent
model: claude-haiku-4-5
feature: 001-phase-v-cloud-deployment
branch: 001-phase-v-cloud-deployment
user: user
command: /sp.plan
labels: ["phase-v", "cloud-deployment", "microservices", "event-driven", "kafka", "dapr", "kubernetes", "planning"]
links:
  spec: specs/001-phase-v-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-v-cloud-deployment/plan.md
  - specs/001-phase-v-cloud-deployment/research.md
  - specs/001-phase-v-cloud-deployment/data-model.md
  - specs/001-phase-v-cloud-deployment/quickstart.md
  - specs/001-phase-v-cloud-deployment/contracts/event-schemas.md
  - specs/001-phase-v-cloud-deployment/contracts/mcp-tools.md
  - specs/001-phase-v-cloud-deployment/contracts/api-endpoints.md
tests:
  - No tests run (planning phase - design artifacts only)
---

## Prompt

```text
/sp.plan # Phase V Plan - Advanced Cloud Deployment

[User provided extensive pre-filled implementation plan content including microservices architecture, deployment strategies, event-driven communication patterns, Dapr configuration, Kafka topics, CI/CD pipeline, and implementation phases A-E]

Key planning requirements:
- Decompose monolithic backend into 4 microservices (Chat API, Recurring Task Service, Notification Service, Frontend)
- Implement Kafka event streaming via Dapr Pub/Sub
- Add Dapr Jobs API for scheduled reminders
- Deploy to cloud Kubernetes (OKE/GKE/AKS) with Helm charts
- Configure GitHub Actions CI/CD pipeline
- Support horizontal pod autoscaling (HPA)
- Implement zero-downtime deployments
```

## Response snapshot

Successfully executed Phase V planning workflow with comprehensive design artifacts.

**Planning Artifacts Created**:

1. **plan.md** (Main Implementation Plan):
   - Microservices breakdown (4 services with ports, responsibilities, Dapr App IDs)
   - Database schema updates (7 new fields for tasks table)
   - Event architecture (3 Kafka topics with event schemas)
   - Dapr configuration (Pub/Sub, State Store, Jobs API, Secrets)
   - Deployment architecture (Minikube local, OKE/GKE/AKS cloud)
   - Resource allocation tables (local and production)
   - HPA configuration (CPU >70%, Memory >80%)
   - CI/CD pipeline (6-stage GitHub Actions workflow)
   - Implementation phases A-E (18 days total)

2. **research.md** (Phase 0):
   - Cloud platform selection: Oracle Cloud (OKE) primary, GKE/AKS fallback
   - Kafka deployment: Strimzi for local, Redpanda Cloud for production
   - Dapr State Store: PostgreSQL (reuse existing database)
   - Reminder scheduling: Dapr Jobs API (Kubernetes-native)
   - Event schema versioning: Embedded versioning with schema_version field
   - Multi-device sync: Defer to Phase VI (polling for MVP)
   - Notification delivery: Email for MVP (SendGrid/SMTP)
   - Database migration: Alembic with explicit rollback

3. **data-model.md** (Phase 1):
   - Updated tasks table schema with 7 new fields
   - Entity relationship diagram
   - Alembic migration script (004_add_advanced_features.py)
   - Data access patterns with code examples
   - Performance considerations (index usage, query optimization)
   - Data validation rules

4. **contracts/event-schemas.md**:
   - 6 event types: task.created, task.updated, task.completed, task.deleted, reminder.scheduled, reminder.triggered
   - Standardized event schema structure
   - Event flow diagrams (task creation, recurring task completion, reminder scheduling)
   - Event ordering guarantees and retention policies
   - Error handling and schema evolution strategy

5. **contracts/mcp-tools.md**:
   - Updated add_task, update_task, list_tasks tools with new fields
   - New search_tasks tool for keyword search
   - Natural language understanding examples
   - Input/output schemas with validation rules
   - Performance expectations (<100-300ms p95)

6. **contracts/api-endpoints.md**:
   - Chat API endpoints (POST /api/{user_id}/chat, health checks)
   - Recurring Task Service endpoints (health checks, metrics)
   - Notification Service endpoints (health checks, metrics)
   - Frontend endpoints (Next.js, Better Auth)
   - Error response format and rate limiting

7. **quickstart.md**:
   - Part 1: Local development setup (Minikube, Dapr, Kafka, Helm)
   - Part 2: Testing the application (5 test scenarios)
   - Part 3: Cloud deployment (OKE setup, DNS, TLS)
   - Part 4: CI/CD setup (GitHub Actions)
   - Part 5: Monitoring and troubleshooting
   - Part 6: Cleanup procedures

**Key Design Decisions**:
- Microservices architecture with 4 services (Chat API:8000, Recurring Task:8001, Notification:8002, Frontend:3000)
- Event-driven communication via Kafka (3 topics: task-events, reminders, task-updates)
- Dapr building blocks: Pub/Sub, State Management, Service Invocation, Jobs API, Secrets
- Database: Neon PostgreSQL with 7 new fields (priority, tags, due_at, reminder_minutes_before, recurrence, recurrence_end_date, reminder_sent)
- Deployment: Minikube for local (1.8 CPU, 3.5GB RAM), OKE/GKE/AKS for cloud (6 CPU, 12GB RAM minimum)
- HPA: Scale on CPU >70%, Memory >80%
- CI/CD: 6-stage GitHub Actions pipeline (lint, test, build, push, deploy-dev, deploy-prod)

## Outcome

- ✅ Impact: Comprehensive Phase V implementation plan created with complete microservices architecture, event-driven design, and cloud deployment strategy
- 🧪 Tests: No tests run (planning phase - design artifacts only)
- 📁 Files: 7 files created (plan.md, research.md, data-model.md, quickstart.md, 3 contract files)
- 🔁 Next prompts:
  - `/sp.tasks` to generate actionable implementation tasks from the plan
  - `/sp.adr` to document architectural decisions (Kafka deployment strategy, Dapr building blocks, microservices boundaries)
  - Begin implementation with Phase A (Database & MCP Tools)
- 🧠 Reflection: Phase V planning successfully balances ambitious technical scope (microservices, event-driven architecture, cloud deployment) with practical implementation strategy. The 5-phase implementation plan (A-E over 18 days) provides clear milestones and dependencies. Research phase resolved all technology selection questions with clear rationale. Design artifacts provide comprehensive contracts for event schemas, MCP tools, and API endpoints. Quickstart guide enables both local development and cloud deployment. Ready to proceed to task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully with all required artifacts
- Graders run and results (PASS/FAIL): Planning Quality Checklist - PASS (all design artifacts complete, no unresolved questions)
- Prompt variant (if applicable): Standard /sp.plan workflow with comprehensive user-provided plan content
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to generate actionable implementation tasks and validate that the plan provides sufficient detail for task breakdown
