#!/bin/bash
# Build Docker images for Todo application

set -e

echo "🔨 Building Docker images for Todo application..."

# Build frontend image
echo "📦 Building frontend image..."
cd frontend
docker build -t todo-frontend:1.0.0 .
cd ..

# Build backend image
echo "📦 Building backend image..."
cd backend
docker build -t todo-backend:1.0.0 .
cd ..

# Display image sizes
echo ""
echo "✅ Build complete! Image sizes:"
docker images | grep todo-

echo ""
echo "📊 Image size verification:"
FRONTEND_SIZE=$(docker images todo-frontend:1.0.0 --format "{{.Size}}")
BACKEND_SIZE=$(docker images todo-backend:1.0.0 --format "{{.Size}}")

echo "Frontend: $FRONTEND_SIZE (target: < 100MB)"
echo "Backend: $BACKEND_SIZE (target: < 200MB)"

echo ""
echo "✅ Images built successfully!"
echo "Next steps:"
echo "  1. Load images to Minikube: ./scripts/load-images.sh"
echo "  2. Deploy to Kubernetes: ./scripts/deploy.sh"
