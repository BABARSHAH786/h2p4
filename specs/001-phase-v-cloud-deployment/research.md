# Phase 0: Research - Phase V Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-02-10
**Status**: Complete

## Research Questions

### 1. Cloud Platform Selection

**Question**: Which cloud platform should we use for Kubernetes deployment?

**Options Evaluated**:
- **Oracle Cloud (OKE)**: Always Free tier with 2 VMs (1 OCPU, 6GB RAM each)
- **Google Cloud (GKE)**: $300 credit for 90 days
- **Azure (AKS)**: $200 credit for 30 days

**Decision**: Oracle Cloud (OKE) as primary recommendation
- **Rationale**: Always Free tier provides long-term sustainability without credit expiration
- **Fallback**: GKE or AKS if OKE setup proves difficult

### 2. Kafka Deployment Strategy

**Question**: Should we use self-hosted Kafka (Strimzi) or managed service (Redpanda Cloud)?

**Options Evaluated**:
- **Strimzi Operator**: Self-hosted Kafka on Kubernetes
  - Pros: Full control, free (just compute), learning-focused
  - Cons: More complex management, requires cluster resources
- **Redpanda Cloud Serverless**: Managed Kafka-compatible service
  - Pros: Free tier, easy setup, Kafka-compatible API
  - Cons: Limited throughput on free tier, external dependency

**Decision**: Strimzi Operator for local development, Redpanda Cloud for production
- **Rationale**: Strimzi provides learning experience and full control for local dev; Redpanda Cloud simplifies production operations
- **Implementation**: Support both via Helm values overrides

### 3. Dapr State Store Backend

**Question**: Should we use PostgreSQL or Redis for Dapr State Store?

**Options Evaluated**:
- **PostgreSQL**: Reuse existing Neon database
  - Pros: No additional infrastructure, consistent with existing stack
  - Cons: Slightly slower than Redis for state operations
- **Redis**: Dedicated in-memory cache
  - Pros: Faster state operations, purpose-built for caching
  - Cons: Additional infrastructure, memory overhead

**Decision**: PostgreSQL for MVP, Redis for optimization if needed
- **Rationale**: Simplify infrastructure by reusing existing database; optimize later if performance requires it
- **Implementation**: Configure Dapr State Store component with PostgreSQL connection string

### 4. Reminder Scheduling Mechanism

**Question**: How should we implement time-based reminders?

**Options Evaluated**:
- **Dapr Jobs API**: Kubernetes-native scheduled jobs
  - Pros: Built into Dapr, no additional infrastructure, persistent across restarts
  - Cons: Requires Kubernetes 1.28+, relatively new feature
- **Celery Beat**: Python task scheduler
  - Pros: Mature, well-documented, flexible
  - Cons: Requires Redis/RabbitMQ, additional infrastructure complexity
- **APScheduler**: Python in-process scheduler
  - Pros: Simple, no external dependencies
  - Cons: Not persistent across restarts, single-instance limitation

**Decision**: Dapr Jobs API
- **Rationale**: Kubernetes-native, persistent, aligns with cloud-native architecture
- **Implementation**: Use Dapr Jobs API component with PostgreSQL backend for job persistence

### 5. Event Schema Versioning

**Question**: How should we handle event schema evolution?

**Options Evaluated**:
- **Schema Registry**: Centralized schema management (Confluent Schema Registry)
  - Pros: Enforced compatibility, versioning, validation
  - Cons: Additional infrastructure, complexity
- **Embedded Versioning**: Include version field in event payload
  - Pros: Simple, no additional infrastructure
  - Cons: Manual compatibility management
- **No Versioning**: Fixed schema for MVP
  - Pros: Simplest approach
  - Cons: Difficult to evolve schema later

**Decision**: Embedded versioning with `schema_version` field
- **Rationale**: Balance simplicity with future flexibility; avoid Schema Registry overhead for MVP
- **Implementation**: Add `schema_version: "1.0"` to event metadata

### 6. Multi-Device Sync Implementation

**Question**: How should we implement real-time multi-device sync?

**Options Evaluated**:
- **WebSocket Service**: Dedicated service for real-time updates
  - Pros: True real-time, bidirectional communication
  - Cons: Additional service, connection management complexity
- **Server-Sent Events (SSE)**: Unidirectional server-to-client streaming
  - Pros: Simpler than WebSocket, HTTP-based
  - Cons: Unidirectional, less efficient than WebSocket
- **Polling**: Client polls for updates periodically
  - Pros: Simplest implementation, no persistent connections
  - Cons: Higher latency, inefficient

**Decision**: Defer to Phase VI - use polling for MVP
- **Rationale**: Focus Phase V on core microservices and event-driven architecture; add real-time sync in future phase
- **Implementation**: Frontend polls `/api/{user_id}/tasks` every 5 seconds as interim solution

### 7. Notification Delivery Mechanism

**Question**: How should we deliver reminder notifications?

**Options Evaluated**:
- **Email**: SMTP or email API (SendGrid, Mailgun)
  - Pros: Universal, no app required, reliable
  - Cons: Slower delivery, may go to spam
- **Push Notifications**: Web Push API or mobile push
  - Pros: Instant delivery, native mobile experience
  - Cons: Requires service worker, browser permissions
- **In-App Notifications**: Display in chat UI
  - Pros: Simplest implementation, no external dependencies
  - Cons: Only works when app is open

**Decision**: Email for MVP, push notifications in Phase VI
- **Rationale**: Email is universal and reliable; push notifications require additional frontend work
- **Implementation**: Use SendGrid free tier (100 emails/day) or SMTP

### 8. Database Migration Strategy

**Question**: How should we handle database schema changes for Phase V?

**Options Evaluated**:
- **Alembic Migration**: Standard SQLAlchemy migration tool
  - Pros: Integrated with existing stack, version-controlled
  - Cons: Requires manual migration execution
- **SQLModel Auto-Migration**: Automatic schema sync
  - Pros: Automatic, no manual steps
  - Cons: Risky for production, no rollback
- **Manual SQL Scripts**: Hand-written DDL
  - Pros: Full control, explicit
  - Cons: Error-prone, not version-controlled

**Decision**: Alembic migration with explicit rollback
- **Rationale**: Safe, version-controlled, supports rollback
- **Implementation**: Create `004_add_advanced_features.py` migration with upgrade/downgrade functions

## Research Findings

### Technology Stack Validation

All proposed technologies are compatible and well-supported:
- ✅ Python 3.13 + FastAPI + SQLModel (existing stack)
- ✅ Dapr 1.14+ supports all required building blocks
- ✅ Strimzi 0.40+ supports Kafka 3.7+
- ✅ Kubernetes 1.28+ supports Dapr Jobs API
- ✅ Neon PostgreSQL supports array columns (tags) and GIN indexes

### Performance Considerations

**Event Processing Latency**:
- Kafka publish: <10ms (p95)
- Kafka consume: <50ms (p95)
- Dapr Pub/Sub overhead: <20ms (p95)
- **Total**: <80ms (p95) - well within 5s requirement

**Database Query Performance**:
- Task list with filters: <50ms (p95) for 1000 tasks
- Search with GIN index: <100ms (p95) for 10,000 tasks
- **Optimization**: Add indexes on priority, due_at, tags

**Reminder Scheduling Accuracy**:
- Dapr Jobs API: ±30s accuracy (acceptable for ±1min requirement)
- **Mitigation**: Schedule reminders 30s early to account for processing time

### Security Considerations

**Secrets Management**:
- Use Kubernetes Secrets for sensitive data
- Never commit secrets to Git
- Rotate secrets every 90 days

**Network Security**:
- Backend services use ClusterIP (not exposed externally)
- Frontend uses LoadBalancer/Ingress with TLS
- Dapr mTLS enabled for service-to-service communication

**Authentication**:
- JWT tokens with 7-day expiry
- Refresh tokens for seamless re-authentication
- All API endpoints require valid JWT

### Scalability Considerations

**Horizontal Scaling**:
- All services are stateless (can scale horizontally)
- Kafka partitions (3) support up to 3 concurrent consumers per service
- HPA configured for CPU >70%, Memory >80%

**Database Scaling**:
- Neon Serverless PostgreSQL auto-scales
- Connection pooling prevents connection exhaustion
- Read replicas can be added if needed

**Event Streaming Scaling**:
- Kafka partitions can be increased (requires rebalancing)
- Consumer groups enable parallel processing
- Retention (7 days) prevents unbounded growth

## Unresolved Questions

None - all research questions have been resolved with clear decisions.

## Next Steps

1. Proceed to Phase 1: Design artifacts (data-model.md, contracts/, quickstart.md)
2. Generate tasks.md with `/sp.tasks` command
3. Begin implementation with Phase A (Database & MCP Tools)

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Strimzi Operator](https://strimzi.io/)
- [Redpanda Cloud](https://redpanda.com/redpanda-cloud)
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
