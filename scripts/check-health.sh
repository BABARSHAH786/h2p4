#!/bin/bash
# Verify deployment health

set -e

NAMESPACE=${1:-todo-app}

echo "🔍 Checking deployment health in namespace: ${NAMESPACE}"

# Check if namespace exists
if ! kubectl get namespace ${NAMESPACE} >/dev/null 2>&1; then
    echo "❌ Namespace ${NAMESPACE} does not exist"
    exit 1
fi

# Check pods
echo ""
echo "📦 Pods:"
kubectl get pods -n ${NAMESPACE}

# Check if all pods are running
NOT_RUNNING=$(kubectl get pods -n ${NAMESPACE} --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
if [ "$NOT_RUNNING" -gt 0 ]; then
    echo "⚠️  Warning: ${NOT_RUNNING} pods are not running"
fi

# Check services
echo ""
echo "🌐 Services:"
kubectl get svc -n ${NAMESPACE}

# Check HPA
echo ""
echo "📊 Horizontal Pod Autoscalers:"
kubectl get hpa -n ${NAMESPACE} 2>/dev/null || echo "No HPAs found"

# Check ingress
echo ""
echo "🔗 Ingress:"
kubectl get ingress -n ${NAMESPACE} 2>/dev/null || echo "No ingress found"

# Health check endpoints
echo ""
echo "🏥 Health Checks:"

# Chat API
if kubectl get pod -l app=chat-api -n ${NAMESPACE} >/dev/null 2>&1; then
    CHAT_POD=$(kubectl get pod -l app=chat-api -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
    echo -n "  Chat API: "
    kubectl exec ${CHAT_POD} -n ${NAMESPACE} -c chat-api -- curl -s http://localhost:8000/health/ready | grep -q "ready" && echo "✅ Ready" || echo "❌ Not Ready"
fi

# Recurring Task Service
if kubectl get pod -l app=recurring-task-service -n ${NAMESPACE} >/dev/null 2>&1; then
    RTS_POD=$(kubectl get pod -l app=recurring-task-service -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
    echo -n "  Recurring Task Service: "
    kubectl exec ${RTS_POD} -n ${NAMESPACE} -c recurring-task-service -- curl -s http://localhost:8001/health/ready | grep -q "ready" && echo "✅ Ready" || echo "❌ Not Ready"
fi

# Notification Service
if kubectl get pod -l app=notification-service -n ${NAMESPACE} >/dev/null 2>&1; then
    NS_POD=$(kubectl get pod -l app=notification-service -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}')
    echo -n "  Notification Service: "
    kubectl exec ${NS_POD} -n ${NAMESPACE} -c notification-service -- curl -s http://localhost:8002/health/ready | grep -q "ready" && echo "✅ Ready" || echo "❌ Not Ready"
fi

# Check Kafka
echo ""
echo "📨 Kafka Status:"
kubectl get kafka -n kafka 2>/dev/null || echo "Kafka not found in kafka namespace"

# Check Dapr
echo ""
echo "🔧 Dapr Status:"
kubectl get pods -n dapr-system 2>/dev/null || echo "Dapr not installed"

echo ""
echo "✅ Health check complete!"
