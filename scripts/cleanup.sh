#!/bin/bash
# Cleanup Kubernetes resources

set -e

echo "🧹 Cleaning up Kubernetes resources..."

# Uninstall Helm release
echo "📦 Uninstalling Helm release..."
helm uninstall todo-app-local -n todo-app || echo "Helm release not found"

# Delete namespace (this will delete all resources)
echo "🗑️  Deleting namespace..."
kubectl delete namespace todo-app --ignore-not-found=true

echo ""
echo "⏳ Waiting for namespace deletion..."
kubectl wait --for=delete namespace/todo-app --timeout=60s || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "To stop Minikube:"
echo "   minikube stop"
echo ""
echo "To delete Minikube cluster:"
echo "   minikube delete"
