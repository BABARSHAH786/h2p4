# Docker Compose Local Testing

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
BETTER_AUTH_SECRET=your-secret-key
OPENAI_API_KEY=sk-your-openai-key
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### 4. Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Testing

### Test Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### Test Frontend

Open browser: http://localhost:3000

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Troubleshooting

### Backend Not Starting

Check logs:
```bash
docker-compose logs backend
```

Common issues:
- Missing environment variables
- Database connection failed
- Invalid OpenAI API key

### Frontend Not Accessible

Check if backend is running:
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Restart Services

```bash
docker-compose restart
```

## Notes

- This is for **local testing only**
- For production, use Kubernetes deployment
- Images are already built (todo-frontend:1.0.0, todo-backend:1.0.0)
- Network isolation provided by Docker bridge network
