.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test clean backup

# Default target
help:
	@echo "SmartLock Backend - Docker Commands"
	@echo ""
	@echo "Production Commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs"
	@echo "  make ps             - Show running containers"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-up         - Start development environment"
	@echo "  make dev-down       - Stop development environment"
	@echo "  make dev-logs       - View development logs"
	@echo ""
	@echo "Database Commands:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make dbshell        - Open database shell"
	@echo "  make backup         - Backup database"
	@echo ""
	@echo "Django Commands:"
	@echo "  make shell          - Open Django shell"
	@echo "  make createsuperuser- Create Django superuser"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make test           - Run tests"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make rebuild        - Rebuild and restart"
	@echo "  make prune          - Clean Docker system"

# Production Commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

ps:
	docker-compose ps

# Development Commands
dev-up:
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Database Commands
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

dbshell:
	docker-compose exec db psql -U smartlock_user -d smartlock_db

backup:
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U smartlock_user smartlock_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup completed!"

# Django Commands
shell:
	docker-compose exec web python manage.py shell

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

test:
	docker-compose exec web python manage.py test

# Maintenance Commands
clean:
	docker-compose down -v
	@echo "Containers and volumes removed!"

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "Rebuild completed!"

prune:
	docker system prune -a -f
	@echo "Docker system cleaned!"

# Logs for specific services
logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

logs-nginx:
	docker-compose logs -f nginx

logs-celery:
	docker-compose logs -f celery

# Health check
health:
	@curl -s http://localhost/health/ | python -m json.tool || echo "Service not available"

# Quick setup for first time
setup:
	@echo "Setting up SmartLock Backend..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make build && make up"
