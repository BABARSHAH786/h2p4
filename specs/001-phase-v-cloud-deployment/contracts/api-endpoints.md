# API Endpoint Contracts - Phase V Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-02-10
**Status**: Complete

## Overview

This document defines the HTTP API contracts for all microservices in Phase V. All endpoints require JWT authentication unless otherwise noted.

## Authentication

**Header**: `Authorization: Bearer <jwt_token>`

All endpoints (except health checks) require a valid JWT token obtained from Better Auth.

**Token Format**:
```json
{
  "user_id": "string",
  "email": "string",
  "exp": 1234567890
}
```

**Error Response** (401 Unauthorized):
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

---

## Chat API Service (Port 8000)

### POST /api/{user_id}/chat

**Purpose**: Send a message to the AI chatbot and receive a response

**Path Parameters**:
- `user_id` (string): User identifier (must match JWT token)

**Request Body**:
```json
{
  "message": "string",
  "conversation_id": "uuid (optional)"
}
```

**Response** (200 OK):
```json
{
  "response": "string",
  "conversation_id": "uuid",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": { /* tool arguments */ },
      "result": { /* tool result */ }
    }
  ]
}
```

**Error Responses**:
- 400 Bad Request: Invalid message format
- 401 Unauthorized: Invalid JWT token
- 403 Forbidden: user_id doesn't match JWT token
- 500 Internal Server Error: Agent execution failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/user_123/chat \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task: Client presentation, high priority, due Friday 3 PM"
  }'
```

**Response**:
```json
{
  "response": "I've created a high priority task 'Client presentation' due Friday at 3 PM. I'll remind you 1 hour before.",
  "conversation_id": "conv_abc123",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "Client presentation",
        "priority": "high",
        "due_at": "2026-02-14T15:00:00Z",
        "reminder_minutes_before": 60
      },
      "result": {
        "task_id": "task_xyz789",
        "title": "Client presentation",
        "priority": "high",
        "due_at": "2026-02-14T15:00:00Z"
      }
    }
  ]
}
```

---

### GET /health/live

**Purpose**: Liveness probe for Kubernetes

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "alive",
  "service": "chat-api",
  "timestamp": "2026-02-10T14:30:00Z"
}
```

---

### GET /health/ready

**Purpose**: Readiness probe for Kubernetes

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "ready",
  "service": "chat-api",
  "checks": {
    "database": "connected",
    "mcp_server": "running",
    "dapr": "connected"
  },
  "timestamp": "2026-02-10T14:30:00Z"
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "not_ready",
  "service": "chat-api",
  "checks": {
    "database": "disconnected",
    "mcp_server": "running",
    "dapr": "connected"
  },
  "timestamp": "2026-02-10T14:30:00Z"
}
```

---

## Recurring Task Service (Port 8001)

### GET /health/live

**Purpose**: Liveness probe for Kubernetes

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "alive",
  "service": "recurring-task-service",
  "timestamp": "2026-02-10T14:30:00Z"
}
```

---

### GET /health/ready

**Purpose**: Readiness probe for Kubernetes

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "ready",
  "service": "recurring-task-service",
  "checks": {
    "database": "connected",
    "kafka_consumer": "running",
    "dapr": "connected"
  },
  "timestamp": "2026-02-10T14:30:00Z"
}
```

---

### GET /metrics (Optional)

**Purpose**: Prometheus metrics endpoint

**Authentication**: None required

**Response** (200 OK):
```
# HELP recurring_tasks_processed_total Total number of recurring tasks processed
# TYPE recurring_tasks_processed_total counter
recurring_tasks_processed_total 42

# HELP recurring_tasks_created_total Total number of next occurrences created
# TYPE recurring_tasks_created_total counter
recurring_tasks_created_total 38

# HELP recurring_tasks_processing_duration_seconds Time spent processing recurring tasks
# TYPE recurring_tasks_processing_duration_seconds histogram
recurring_tasks_processing_duration_seconds_bucket{le="0.1"} 35
recurring_tasks_processing_duration_seconds_bucket{le="0.5"} 40
recurring_tasks_processing_duration_seconds_bucket{le="1.0"} 42
recurring_tasks_processing_duration_seconds_sum 12.5
recurring_tasks_processing_duration_seconds_count 42
```

---

## Notification Service (Port 8002)

### GET /health/live

**Purpose**: Liveness probe for Kubernetes

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "alive",
  "service": "notification-service",
  "timestamp": "2026-02-10T14:30:00Z"
}
```

---

### GET /health/ready

**Purpose**: Readiness probe for Kubernetes

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "ready",
  "service": "notification-service",
  "checks": {
    "kafka_consumer": "running",
    "dapr": "connected",
    "email_service": "connected"
  },
  "timestamp": "2026-02-10T14:30:00Z"
}
```

---

### GET /metrics (Optional)

**Purpose**: Prometheus metrics endpoint

**Authentication**: None required

**Response** (200 OK):
```
# HELP notifications_sent_total Total number of notifications sent
# TYPE notifications_sent_total counter
notifications_sent_total{channel="email",status="delivered"} 120
notifications_sent_total{channel="email",status="failed"} 5

# HELP notification_delivery_duration_seconds Time to deliver notifications
# TYPE notification_delivery_duration_seconds histogram
notification_delivery_duration_seconds_bucket{le="1.0"} 100
notification_delivery_duration_seconds_bucket{le="5.0"} 120
notification_delivery_duration_seconds_bucket{le="10.0"} 125
notification_delivery_duration_seconds_sum 450.0
notification_delivery_duration_seconds_count 125
```

---

## Frontend Service (Port 3000)

### GET /

**Purpose**: Serve Next.js application

**Authentication**: None required (handled by Better Auth)

**Response**: HTML page

---

### GET /api/auth/*

**Purpose**: Better Auth endpoints (login, logout, session management)

**Authentication**: Varies by endpoint

**Documentation**: See [Better Auth Documentation](https://better-auth.com/docs)

---

## Error Response Format

All services use consistent error response format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    // Optional additional context
  },
  "timestamp": "2026-02-10T14:30:00Z",
  "request_id": "req_abc123"
}
```

**Common Error Types**:
- `ValidationError`: Invalid input data
- `NotFoundError`: Resource not found
- `PermissionError`: Insufficient permissions
- `AuthenticationError`: Invalid or missing JWT token
- `InternalError`: Server-side error

---

## Rate Limiting

**Chat API**:
- 60 requests per minute per user
- 429 Too Many Requests response when exceeded

**Other Services**:
- No rate limiting (internal services)

---

## CORS Configuration

**Chat API**:
- Allowed origins: Frontend URL (configured via environment variable)
- Allowed methods: GET, POST, OPTIONS
- Allowed headers: Authorization, Content-Type
- Credentials: true

**Other Services**:
- No CORS (internal services, not exposed externally)

---

## Request/Response Logging

All services log requests and responses in structured JSON format:

```json
{
  "timestamp": "2026-02-10T14:30:00Z",
  "level": "INFO",
  "service": "chat-api",
  "method": "POST",
  "path": "/api/user_123/chat",
  "status": 200,
  "duration_ms": 1250,
  "user_id": "user_123",
  "request_id": "req_abc123"
}
```

---

## Service-to-Service Communication

Services communicate via Dapr service invocation (not direct HTTP):

**Example** (Frontend → Chat API):
```python
# Frontend calls Chat API via Dapr
response = requests.post(
    "http://localhost:3500/v1.0/invoke/chat-api/method/api/user_123/chat",
    headers={"Authorization": f"Bearer {jwt_token}"},
    json={"message": "Add a task"}
)
```

**Dapr Sidecar Port**: 3500 (default)

---

## Testing

**Integration Tests**:
```python
def test_chat_endpoint_creates_task():
    response = client.post(
        "/api/user_123/chat",
        headers={"Authorization": f"Bearer {valid_jwt}"},
        json={"message": "Add a task: Test task"}
    )
    assert response.status_code == 200
    assert "task" in response.json()["response"].lower()

def test_health_check_returns_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_unauthorized_request_returns_401():
    response = client.post(
        "/api/user_123/chat",
        json={"message": "Test"}
    )
    assert response.status_code == 401
```

---

## Performance Expectations

**Chat API**:
- p50 latency: <1s
- p95 latency: <2s
- p99 latency: <5s

**Health Checks**:
- p95 latency: <50ms

**Metrics Endpoints**:
- p95 latency: <100ms

---

## Summary

Phase V defines HTTP API contracts for 4 services:
- **Chat API**: Main user-facing endpoint for chat interactions
- **Recurring Task Service**: Internal service with health checks only
- **Notification Service**: Internal service with health checks only
- **Frontend**: Next.js application with Better Auth integration

All services implement standardized health checks, error responses, and structured logging for observability.
