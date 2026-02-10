# Kubernetes Troubleshooting Guide

## Common Issues and Solutions

### 1. Pods Not Starting

#### Symptoms
```bash
kubectl get pods -n todo-app
# Shows: CrashLoopBackOff, ImagePullBackOff, or Pending
```

#### Diagnosis
```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

#### Solutions

**CrashLoopBackOff**:
- Check application logs for errors
- Verify environment variables and secrets
- Check health probe configuration
- Ensure database connectivity

**ImagePullBackOff**:
- For Minikube, verify images are loaded:
  ```bash
  minikube image ls | grep todo
  ```
- Load missing images:
  ```bash
  minikube image load todo-frontend:1.0.0
  minikube image load todo-backend:1.0.0
  ```

**Pending**:
- Check resource availability:
  ```bash
  kubectl describe node
  kubectl top nodes
  ```
- Reduce resource requests if cluster is constrained

### 2. Image Pull Errors

#### Symptoms
```
Failed to pull image "todo-frontend:1.0.0": rpc error: code = Unknown desc = Error response from daemon: pull access denied
```

#### Solutions

**For Minikube**:
1. Ensure `imagePullPolicy: Never` in deployment
2. Load images to Minikube:
   ```bash
   minikube image load todo-frontend:1.0.0
   minikube image load todo-backend:1.0.0
   ```

**For Remote Registry**:
1. Change `imagePullPolicy` to `IfNotPresent` or `Always`
2. Push images to registry:
   ```bash
   docker tag todo-frontend:1.0.0 your-registry/todo-frontend:1.0.0
   docker push your-registry/todo-frontend:1.0.0
   ```

### 3. Configuration Errors

#### Symptoms
- Application starts but behaves incorrectly
- Missing environment variables
- Database connection failures

#### Diagnosis
```bash
# Check ConfigMaps
kubectl get configmaps -n todo-app
kubectl describe configmap backend-config -n todo-app

# Check Secrets
kubectl get secrets -n todo-app
kubectl describe secret app-secrets -n todo-app

# Verify environment in pod
kubectl exec -it <pod-name> -n todo-app -- env | grep -E 'DATABASE|OPENAI|AGENT'
```

#### Solutions

**Missing or incorrect ConfigMap**:
```bash
# Edit ConfigMap
kubectl edit configmap backend-config -n todo-app

# Or update via Helm
helm upgrade todo-app-local ./k8s/helm-chart \
  --set backend.config.agentModel="gpt-4o"
```

**Missing or incorrect Secrets**:
```bash
# Encode new secret
echo -n "new-value" | base64

# Update via Helm
helm upgrade todo-app-local ./k8s/helm-chart \
  --set secrets.openaiApiKey="<base64-encoded-key>"

# Restart pods to pick up changes
kubectl rollout restart deployment/backend-deployment -n todo-app
```

### 4. Database Connection Issues

#### Symptoms
```
sqlalchemy.exc.OperationalError: could not connect to server
```

#### Diagnosis
```bash
# Check backend logs
kubectl logs -f deployment/backend-deployment -n todo-app

# Test database connectivity from pod
kubectl exec -it <backend-pod> -n todo-app -- \
  python -c "import asyncpg; print('Testing connection...')"
```

#### Solutions

**External Database (Neon)**:
1. Verify DATABASE_URL is correct
2. Check network connectivity
3. Verify database credentials
4. Ensure database allows connections from cluster

**In-Cluster Database**:
1. Check postgres pod status:
   ```bash
   kubectl get pods -l app=postgres -n todo-app
   ```
2. Verify service DNS:
   ```bash
   kubectl exec -it <backend-pod> -n todo-app -- \
     nslookup postgres-service
   ```

### 5. Health Check Failures

#### Symptoms
```
Liveness probe failed: HTTP probe failed with statuscode: 500
Readiness probe failed: Get "http://10.244.0.5:8000/health": dial tcp 10.244.0.5:8000: connect: connection refused
```

#### Diagnosis
```bash
# Check health endpoint manually
kubectl exec -it <pod-name> -n todo-app -- \
  curl http://localhost:8000/health

# Check application logs
kubectl logs <pod-name> -n todo-app
```

#### Solutions

**Application not ready**:
- Increase `initialDelaySeconds` in probe configuration
- Check application startup time
- Verify health endpoint implementation

**Health endpoint failing**:
- Check database connectivity
- Verify all dependencies are available
- Review application logs for errors

### 6. Resource Exhaustion

#### Symptoms
```
0/1 nodes are available: 1 Insufficient memory, 1 Insufficient cpu
```

#### Diagnosis
```bash
# Check node resources
kubectl top nodes
kubectl describe node

# Check pod resources
kubectl top pods -n todo-app

# Check resource requests
kubectl describe deployment backend-deployment -n todo-app
```

#### Solutions

**Reduce resource requests**:
```bash
helm upgrade todo-app-local ./k8s/helm-chart \
  --set backend.resources.requests.cpu="100m" \
  --set backend.resources.requests.memory="128Mi"
```

**Increase Minikube resources**:
```bash
minikube stop
minikube delete
minikube start --cpus=4 --memory=8192
```

**Scale down replicas**:
```bash
kubectl scale deployment backend-deployment --replicas=1 -n todo-app
kubectl scale deployment frontend-deployment --replicas=1 -n todo-app
```

### 7. Service Not Accessible

#### Symptoms
- Cannot access frontend via NodePort
- Backend not reachable from frontend

#### Diagnosis
```bash
# Check services
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app

# Test service from within cluster
kubectl run test-pod --rm -it --image=busybox -n todo-app -- \
  wget -O- http://backend-service:8000/health
```

#### Solutions

**NodePort not accessible**:
```bash
# Get Minikube IP
minikube ip

# Get service URL
minikube service frontend-service -n todo-app --url

# Open in browser
minikube service frontend-service -n todo-app
```

**Service selector mismatch**:
```bash
# Check service selector
kubectl describe svc frontend-service -n todo-app

# Check pod labels
kubectl get pods -n todo-app --show-labels

# Ensure labels match
```

### 8. Helm Installation Failures

#### Symptoms
```
Error: INSTALLATION FAILED: unable to build kubernetes objects from release manifest
```

#### Diagnosis
```bash
# Dry run to check for errors
helm install todo-app-local ./k8s/helm-chart \
  --dry-run --debug \
  --set secrets.databaseUrl="test"

# Validate chart
helm lint ./k8s/helm-chart
```

#### Solutions

**Template errors**:
- Check YAML syntax in templates
- Verify all required values are set
- Use `helm template` to render locally

**Missing required values**:
```bash
# Ensure all secrets are provided
helm install todo-app-local ./k8s/helm-chart \
  --set secrets.databaseUrl="<value>" \
  --set secrets.betterAuthSecret="<value>" \
  --set secrets.openaiApiKey="<value>"
```

### 9. Rolling Update Stuck

#### Symptoms
```
Waiting for deployment "backend-deployment" rollout to finish: 1 old replicas are pending termination
```

#### Diagnosis
```bash
# Check rollout status
kubectl rollout status deployment/backend-deployment -n todo-app

# Check pod status
kubectl get pods -n todo-app

# Check events
kubectl describe deployment backend-deployment -n todo-app
```

#### Solutions

**Force rollout**:
```bash
# Delete old pods
kubectl delete pod <old-pod-name> -n todo-app

# Restart rollout
kubectl rollout restart deployment/backend-deployment -n todo-app
```

**Rollback if needed**:
```bash
helm rollback todo-app-local -n todo-app
```

### 10. Persistent Data Loss

#### Symptoms
- Data disappears after pod restart
- Database resets

#### Diagnosis
```bash
# Check PVC status
kubectl get pvc -n todo-app

# Check volume mounts
kubectl describe pod <postgres-pod> -n todo-app
```

#### Solutions

**Enable persistence**:
```bash
helm upgrade todo-app-local ./k8s/helm-chart \
  --set database.enabled=true \
  --set database.persistence.enabled=true
```

**Use external database**:
- Configure Neon PostgreSQL
- Set DATABASE_URL in secrets

## Debugging Commands

### Quick Diagnostics
```bash
# Overall cluster health
kubectl get all -n todo-app

# Pod details
kubectl describe pod <pod-name> -n todo-app

# Logs (last 100 lines)
kubectl logs --tail=100 <pod-name> -n todo-app

# Follow logs
kubectl logs -f <pod-name> -n todo-app

# Previous container logs (if crashed)
kubectl logs --previous <pod-name> -n todo-app

# Execute command in pod
kubectl exec -it <pod-name> -n todo-app -- /bin/sh

# Port forward for local testing
kubectl port-forward <pod-name> 8000:8000 -n todo-app
```

### Resource Monitoring
```bash
# Pod resource usage
kubectl top pods -n todo-app

# Node resource usage
kubectl top nodes

# Watch pod status
kubectl get pods -n todo-app -w
```

### Network Debugging
```bash
# Test DNS resolution
kubectl exec -it <pod-name> -n todo-app -- nslookup backend-service

# Test HTTP connectivity
kubectl exec -it <pod-name> -n todo-app -- \
  curl -v http://backend-service:8000/health

# Check service endpoints
kubectl get endpoints -n todo-app
```

## Getting Help

If issues persist:

1. **Check logs**: Application logs often contain the root cause
2. **Review events**: Kubernetes events show cluster-level issues
3. **Verify configuration**: Double-check ConfigMaps, Secrets, and values
4. **Test locally**: Build and run containers locally first
5. **Consult documentation**: Review README and architecture docs

## Useful Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- Project README: `../README.md`
- Architecture: `./ARCHITECTURE.md`
