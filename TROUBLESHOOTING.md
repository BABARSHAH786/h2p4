# Troubleshooting Guide - Phase V Todo Chatbot

## Common Issues and Solutions

### 1. Pods Not Starting

#### Symptom
```bash
kubectl get pods -n todo-app
# Shows pods in Pending, CrashLoopBackOff, or ImagePullBackOff state
```

#### Diagnosis
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app -c <container-name>
```

#### Common Causes & Solutions

**ImagePullBackOff:**
- **Cause**: Cannot pull Docker image
- **Solution**:
  ```bash
  # For local (Minikube): Ensure images are built in Minikube's Docker
  eval $(minikube docker-env)
  ./scripts/build-images.sh

  # For cloud: Check image registry and credentials
  kubectl get secret -n todo-app
  ```

**CrashLoopBackOff:**
- **Cause**: Application crashes on startup
- **Solution**:
  ```bash
  # Check logs for error messages
  kubectl logs <pod-name> -n todo-app -c chat-api

  # Common issues:
  # 1. Database connection failed - verify DATABASE_URL secret
  # 2. Missing environment variables - check secret configuration
  # 3. Port already in use - check for conflicting services
  ```

**Pending:**
- **Cause**: Insufficient cluster resources
- **Solution**:
  ```bash
  # Check node resources
  kubectl top nodes
  kubectl describe nodes

  # Reduce resource requests in values.yaml or add more nodes
  ```

---

### 2. Database Connection Issues

#### Symptom
```
Error: could not connect to database
FATAL: password authentication failed
```

#### Diagnosis
```bash
# Check if secret exists
kubectl get secret app-secrets -n todo-app

# View DATABASE_URL (base64 decoded)
kubectl get secret app-secrets -n todo-app -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

#### Solutions

**Invalid DATABASE_URL:**
```bash
# Correct format:
postgresql://user:password@host:5432/database?sslmode=require

# Update secret:
kubectl delete secret app-secrets -n todo-app
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  -n todo-app

# Restart pods to pick up new secret
kubectl rollout restart deployment/chat-api -n todo-app
```

**SSL/TLS Issues:**
```bash
# For Neon PostgreSQL, ensure sslmode=require is in connection string
# For local PostgreSQL, use sslmode=disable
```

**Connection Timeout:**
```bash
# Check if database is accessible from cluster
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n todo-app -- \
  psql "postgresql://user:password@host/database?sslmode=require"
```

---

### 3. Kafka Connection Errors

#### Symptom
```
Failed to publish event to Kafka
Connection refused: kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

#### Diagnosis
```bash
# Check if Kafka is running
kubectl get kafka -n kafka

# Check Kafka pods
kubectl get pods -n kafka

# Check Dapr Pub/Sub component
kubectl describe component pubsub -n todo-app
```

#### Solutions

**Kafka Not Ready:**
```bash
# Wait for Kafka to be ready (can take 5-10 minutes)
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka

# Check Kafka logs
kubectl logs -f kafka-cluster-kafka-0 -n kafka
```

**Wrong Kafka Broker Address:**
```bash
# Verify Dapr Pub/Sub component has correct broker address
kubectl get component pubsub -n todo-app -o yaml

# Should be: kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
```

**Topics Not Created:**
```bash
# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Create missing topics
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
```

---

### 4. Dapr Sidecar Issues

#### Symptom
```
Pods show 1/2 READY (Dapr sidecar not starting)
Error: failed to connect to Dapr sidecar
```

#### Diagnosis
```bash
# Check Dapr installation
kubectl get pods -n dapr-system

# Check Dapr sidecar logs
kubectl logs <pod-name> -n todo-app -c daprd

# Check Dapr annotations
kubectl get deployment chat-api -n todo-app -o yaml | grep dapr.io
```

#### Solutions

**Dapr Not Installed:**
```bash
# Install Dapr on Kubernetes
dapr init -k

# Verify installation
kubectl get pods -n dapr-system
```

**Missing Dapr Annotations:**
```bash
# Ensure deployment has Dapr annotations:
# dapr.io/enabled: "true"
# dapr.io/app-id: "chat-api"
# dapr.io/app-port: "8000"

# Redeploy with correct annotations
helm upgrade todo-app ./helm -f ./helm/values-local.yaml -n todo-app
```

**Dapr Component Not Found:**
```bash
# Check if Dapr components are deployed
kubectl get components -n todo-app

# Deploy components
kubectl apply -f k8s/base/dapr-components/ -n todo-app
```

---

### 5. Health Check Failures

#### Symptom
```
Readiness probe failed: HTTP probe failed with statuscode: 503
```

#### Diagnosis
```bash
# Check health endpoint manually
kubectl exec -it deployment/chat-api -n todo-app -- \
  curl http://localhost:8000/health/ready

# Check logs for errors
kubectl logs deployment/chat-api -n todo-app -c chat-api
```

#### Solutions

**Database Not Ready:**
- Wait for database connection to establish
- Check DATABASE_URL secret

**Dapr Not Ready:**
- Ensure Dapr sidecar is running
- Check Dapr component configuration

**Application Not Listening:**
```bash
# Verify application is listening on correct port
kubectl exec -it deployment/chat-api -n todo-app -- netstat -tlnp
```

---

### 6. Ingress/LoadBalancer Issues

#### Symptom
```
Cannot access application via ingress URL
Connection timeout or refused
```

#### Diagnosis
```bash
# Check ingress status
kubectl get ingress -n todo-app

# Check ingress controller
kubectl get pods -n ingress-nginx  # or kube-system

# Check service
kubectl get svc frontend -n todo-app
```

#### Solutions

**Ingress Controller Not Installed:**
```bash
# For Minikube
minikube addons enable ingress

# For cloud, install nginx-ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx
```

**DNS Not Configured:**
```bash
# Get LoadBalancer IP
kubectl get ingress -n todo-app

# Add DNS A record pointing to this IP
# Or use /etc/hosts for local testing:
echo "<INGRESS_IP> todo.example.com" | sudo tee -a /etc/hosts
```

**TLS Certificate Issues:**
```bash
# Check cert-manager
kubectl get pods -n cert-manager

# Check certificate status
kubectl get certificate -n todo-app
kubectl describe certificate todo-tls -n todo-app
```

---

### 7. HPA Not Scaling

#### Symptom
```
HPA shows UNKNOWN for current metrics
Pods not scaling despite high CPU/memory
```

#### Diagnosis
```bash
# Check HPA status
kubectl get hpa -n todo-app
kubectl describe hpa chat-api-hpa -n todo-app

# Check metrics-server
kubectl get pods -n kube-system | grep metrics-server
```

#### Solutions

**Metrics Server Not Installed:**
```bash
# For Minikube
minikube addons enable metrics-server

# For cloud
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Resource Requests Not Set:**
```bash
# Ensure deployments have resource requests defined
# HPA requires resource requests to calculate utilization percentage
# Check values.yaml and ensure requests are set
```

---

### 8. Event Publishing Failures

#### Symptom
```
Failed to publish event to Kafka
Events not appearing in Kafka topics
```

#### Diagnosis
```bash
# Check if events are being published
kubectl logs deployment/chat-api -n todo-app -c chat-api | grep "publish"

# Check Kafka consumer
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

#### Solutions

**Dapr Pub/Sub Not Configured:**
```bash
# Verify Pub/Sub component exists
kubectl get component pubsub -n todo-app

# Check component configuration
kubectl describe component pubsub -n todo-app
```

**Kafka Topic Doesn't Exist:**
```bash
# Create topics
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
```

---

### 9. Recurring Tasks Not Creating

#### Symptom
```
Completed recurring task but next occurrence not created
```

#### Diagnosis
```bash
# Check recurring task service logs
kubectl logs deployment/recurring-task-service -n todo-app -c recurring-task-service

# Check if task.completed events are being published
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning | grep "task.completed"
```

#### Solutions

**Service Not Consuming Events:**
```bash
# Restart recurring task service
kubectl rollout restart deployment/recurring-task-service -n todo-app

# Check Dapr Pub/Sub subscription
kubectl logs deployment/recurring-task-service -n todo-app -c daprd
```

**Database Connection Issues:**
```bash
# Check if service can connect to database
kubectl logs deployment/recurring-task-service -n todo-app -c recurring-task-service | grep "database"
```

---

### 10. Reminders Not Sending

#### Symptom
```
Reminder time passed but no notification received
```

#### Diagnosis
```bash
# Check notification service logs
kubectl logs deployment/notification-service -n todo-app -c notification-service

# Check if reminder.triggered events are being published
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic reminders \
  --from-beginning
```

#### Solutions

**Dapr Jobs API Not Configured:**
```bash
# Check jobs component
kubectl get component jobs -n todo-app
kubectl describe component jobs -n todo-app
```

**Email Service Not Configured:**
```bash
# Check if EMAIL_API_KEY is set
kubectl get secret app-secrets -n todo-app -o jsonpath='{.data.EMAIL_API_KEY}' | base64 -d

# If not set, notifications will be logged but not sent
# Add EMAIL_API_KEY to secret for actual email delivery
```

---

## Debugging Commands

### View All Resources
```bash
kubectl get all -n todo-app
kubectl get all -n kafka
kubectl get all -n dapr-system
```

### View Events
```bash
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### View Logs (All Services)
```bash
# Chat API
kubectl logs -f deployment/chat-api -n todo-app -c chat-api

# Recurring Task Service
kubectl logs -f deployment/recurring-task-service -n todo-app -c recurring-task-service

# Notification Service
kubectl logs -f deployment/notification-service -n todo-app -c notification-service

# Dapr Sidecars
kubectl logs -f deployment/chat-api -n todo-app -c daprd
```

### Port Forward for Local Access
```bash
# Frontend
kubectl port-forward svc/frontend 3000:3000 -n todo-app

# Chat API
kubectl port-forward svc/chat-api 8000:8000 -n todo-app

# Kafka
kubectl port-forward svc/kafka-cluster-kafka-bootstrap 9092:9092 -n kafka
```

### Execute Commands in Pods
```bash
# Test database connection
kubectl exec -it deployment/chat-api -n todo-app -- \
  curl http://localhost:8000/health/ready

# Test Dapr metadata
kubectl exec -it deployment/chat-api -n todo-app -- \
  curl http://localhost:3500/v1.0/metadata
```

---

## Performance Issues

### High CPU Usage
```bash
# Check resource usage
kubectl top pods -n todo-app

# Increase CPU limits in values.yaml
# Or let HPA scale up automatically
```

### High Memory Usage
```bash
# Check for memory leaks
kubectl top pods -n todo-app

# Restart pods if memory keeps growing
kubectl rollout restart deployment/chat-api -n todo-app
```

### Slow Response Times
```bash
# Check database query performance
# Check Kafka lag
# Check network latency between services
```

---

## Getting Help

1. **Check logs first**: Most issues are visible in pod logs
2. **Use health check script**: `./scripts/check-health.sh`
3. **Review documentation**: README.md, QUICKSTART.md, DEPLOYMENT-STATUS.md
4. **Check GitHub Issues**: Search for similar problems
5. **Contact support**: Provide logs and error messages

---

## Useful Links

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Strimzi Documentation](https://strimzi.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
