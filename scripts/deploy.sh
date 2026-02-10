#!/bin/bash
# Deploy Todo application to Kubernetes using Helm

set -e

echo "🚀 Deploying Todo application to Kubernetes..."

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Please start it first:"
    echo "   minikube start --cpus=4 --memory=8192"
    exit 1
fi

# Check if secrets are provided
if [ -z "$DATABASE_URL" ] || [ -z "$BETTER_AUTH_SECRET" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: Secrets not provided as environment variables."
    echo "Please set the following environment variables:"
    echo "  export DATABASE_URL='your-database-url'"
    echo "  export BETTER_AUTH_SECRET='your-auth-secret'"
    echo "  export OPENAI_API_KEY='your-openai-key'"
    echo ""
    echo "Or provide them during Helm install with --set flags."
    echo ""
fi

# Encode secrets to base64
if [ -n "$DATABASE_URL" ]; then
    DATABASE_URL_B64=$(echo -n "$DATABASE_URL" | base64)
fi
if [ -n "$BETTER_AUTH_SECRET" ]; then
    BETTER_AUTH_SECRET_B64=$(echo -n "$BETTER_AUTH_SECRET" | base64)
fi
if [ -n "$OPENAI_API_KEY" ]; then
    OPENAI_API_KEY_B64=$(echo -n "$OPENAI_API_KEY" | base64)
fi

# Deploy with Helm
echo "📦 Installing Helm chart..."
helm upgrade --install todo-app-local ./k8s/helm-chart \
    --create-namespace \
    --namespace todo-app \
    ${DATABASE_URL_B64:+--set secrets.databaseUrl="$DATABASE_URL_B64"} \
    ${BETTER_AUTH_SECRET_B64:+--set secrets.betterAuthSecret="$BETTER_AUTH_SECRET_B64"} \
    ${OPENAI_API_KEY_B64:+--set secrets.openaiApiKey="$OPENAI_API_KEY_B64"}

echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=backend -n todo-app --timeout=120s || true

echo ""
echo "📊 Deployment status:"
kubectl get pods -n todo-app
kubectl get svc -n todo-app

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access the application:"
echo "   minikube service frontend-service -n todo-app"
echo ""
echo "Or get the URL with:"
echo "   minikube service frontend-service -n todo-app --url"
