# Running as Microservices

This guide explains how to split the Flask MVC application into separate microservices.

## Architecture Overview

The application can be split into three main services:

1. **User Service** - Handles authentication and user management
2. **Role Service** - Manages roles and permissions
3. **Plugin Service** - Manages plugins and their lifecycle

## Service Setup

### 1. User Service

Create `services/user_service.py`:

```python
"""
User microservice
Handles user authentication and management
"""
from app import create_app, db
from app.config.settings import config
from flask import Flask

def create_user_service():
    """Create user service application"""
    app = create_app(config['production'])

    # Remove other blueprints, keep only user routes
    # The blueprints are registered in app/__init__.py
    # For microservices, you may want to modify the factory

    return app

if __name__ == '__main__':
    app = create_user_service()
    app.run(host='0.0.0.0', port=5001, debug=False)
```

Run the service:
```bash
python -m services.user_service
```

### 2. Role Service

Create `services/role_service.py`:

```python
"""
Role microservice
Handles role and permission management
"""
from app import create_app
from app.config.settings import config

def create_role_service():
    """Create role service application"""
    app = create_app(config['production'])
    return app

if __name__ == '__main__':
    app = create_role_service()
    app.run(host='0.0.0.0', port=5002, debug=False)
```

Run the service:
```bash
python -m services.role_service
```

### 3. Plugin Service

Create `services/plugin_service.py`:

```python
"""
Plugin microservice
Handles plugin management and lifecycle
"""
from app import create_app
from app.config.settings import config

def create_plugin_service():
    """Create plugin service application"""
    app = create_app(config['production'])
    return app

if __name__ == '__main__':
    app = create_plugin_service()
    app.run(host='0.0.0.0', port=5003, debug=False)
```

Run the service:
```bash
python -m services.plugin_service
```

## API Gateway

For production microservices, use an API gateway like:

- **NGINX** - Reverse proxy and load balancer
- **Kong** - API gateway with plugins
- **Traefik** - Modern HTTP reverse proxy

### NGINX Example Configuration

```nginx
upstream user_service {
    server localhost:5001;
}

upstream role_service {
    server localhost:5002;
}

upstream plugin_service {
    server localhost:5003;
}

server {
    listen 80;
    server_name api.example.com;

    location /api/users {
        proxy_pass http://user_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/roles {
        proxy_pass http://role_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/plugins {
        proxy_pass http://plugin_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Docker Setup

### Dockerfile for Each Service

Create `Dockerfile.user`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "-m", "services.user_service"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: flask_mvc
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  user_service:
    build:
      context: .
      dockerfile: Dockerfile.user
    ports:
      - "5001:5001"
    environment:
      DATABASE_URL: postgresql://user:password@postgres/flask_mvc
      SECRET_KEY: your-secret-key
      FLASK_ENV: production
    depends_on:
      - postgres

  role_service:
    build:
      context: .
      dockerfile: Dockerfile.role
    ports:
      - "5002:5002"
    environment:
      DATABASE_URL: postgresql://user:password@postgres/flask_mvc
      SECRET_KEY: your-secret-key
      FLASK_ENV: production
    depends_on:
      - postgres

  plugin_service:
    build:
      context: .
      dockerfile: Dockerfile.plugin
    ports:
      - "5003:5003"
    environment:
      DATABASE_URL: postgresql://user:password@postgres/flask_mvc
      SECRET_KEY: your-secret-key
      FLASK_ENV: production
    depends_on:
      - postgres

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - user_service
      - role_service
      - plugin_service

volumes:
  postgres_data:
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## Service Communication

For inter-service communication, consider:

1. **REST API calls** - HTTP requests between services
2. **Message Queue** - RabbitMQ, Redis, Kafka for async communication
3. **gRPC** - For high-performance RPC calls
4. **Service Mesh** - Istio, Linkerd for advanced routing

### Example: Service-to-Service Communication

```python
import requests

def get_user_roles(user_id, auth_token):
    """Call role service to get user roles"""
    response = requests.get(
        f'http://role-service:5002/api/users/{user_id}/roles',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    return response.json()
```

## Shared Database vs Database per Service

### Shared Database (Current Setup)
- Pros: Simple, ACID transactions, data consistency
- Cons: Tight coupling, scalability limits

### Database per Service
- Pros: Service independence, better scalability
- Cons: Complex transactions, data duplication

## Monitoring and Logging

Use these tools for microservices:

1. **Prometheus** - Metrics collection
2. **Grafana** - Metrics visualization
3. **ELK Stack** - Centralized logging
4. **Jaeger** - Distributed tracing

## Deployment Considerations

1. **Service Discovery** - Consul, etcd
2. **Load Balancing** - NGINX, HAProxy
3. **Circuit Breakers** - Prevent cascade failures
4. **Health Checks** - Kubernetes liveness/readiness probes
5. **Auto-scaling** - Kubernetes HPA

## Testing Microservices

```bash
# Test user service
curl http://localhost:5001/api/users/login -d '{"username":"admin","password":"admin123"}'

# Test role service
curl http://localhost:5002/api/roles/

# Test plugin service
curl http://localhost:5003/api/plugins/
```

## Best Practices

1. **Stateless Services** - No session state in services
2. **API Versioning** - Version your APIs
3. **Authentication** - JWT tokens work well for microservices
4. **Caching** - Use Redis for shared cache
5. **Async Processing** - Use message queues for heavy tasks
6. **Configuration** - Externalize configuration
7. **Security** - Service-to-service authentication
