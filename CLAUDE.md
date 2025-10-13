# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Main Project (Node.js/TypeScript)
- `npm run dev` - Start development server (Express proxy server on port 5000)
- `npm run build:server` - Build server with esbuild
- `npm start` - Start production server
- `npm run check` - TypeScript type checking
- `npm run db:push` - Push database schema changes with Drizzle

### Python Backend (FastAPI)
- `cd python_backend && python main.py` - Start FastAPI server (port 5001)
- `cd python_backend && pip install -r requirements.txt` - Install Python dependencies
- `cd python_backend && uvicorn main:app --reload --host 127.0.0.1 --port 5001` - Alternative FastAPI start

## Architecture Overview

This is a multi-service architecture for ChatToner, a personalized tone conversion system:

### Service Architecture
1. **Express Proxy Server** (`server/index.ts`) - Port 5000
   - Acts as a proxy between frontend and Python FastAPI backend
   - Handles static file serving in production
   - Filters and forwards API requests to Python backend

2. **Python FastAPI Backend** (`python_backend/`) - Port 5001  
   - ML/AI processing for tone conversion
   - OpenAI integration for text transformation
   - Uses dependency injection pattern with Container
   - Structured with services, API routes, and core modules

3. **NestJS Gateway** (`nestjs-gateway/`) - Separate service
   - Additional backend service (currently minimal setup)

4. **Frontend Client** (`client/`) - React application
   - TypeScript React frontend with modern UI components
   - Uses Radix UI components and Tailwind CSS

### Key Technologies
- **Backend**: Express.js (proxy), FastAPI (Python), NestJS
- **Frontend**: React, TypeScript, Radix UI, Tailwind CSS
- **Database**: PostgreSQL with Drizzle ORM
- **ML/AI**: OpenAI API, HuggingFace Transformers
- **Build Tools**: esbuild, Vite, tsx

### Database & Storage
- Uses Drizzle ORM for database operations
- PostgreSQL as primary database
- Session storage with express-session

### Development Workflow
1. Start Python FastAPI backend first: `cd python_backend && python main.py`
2. Start Express proxy server: `npm run dev`
3. Frontend development happens in `client/` directory

### Important Files
- `server/index.ts` - Express proxy server entry point
- `python_backend/main.py` - FastAPI application factory
- `python_backend/core/` - Core configuration and dependency injection
- `python_backend/api/v1/` - API routes and endpoints
- `src/user/` - User-related NestJS modules
- `package.json` - Main project dependencies and scripts

### Environment Configuration
- Python backend uses environment variables for OpenAI API and other settings
- Express server connects to Python backend on localhost:5001
- Production builds serve static files from `dist/public`

## GCP Cloud Deployment

### Cloud Run Services
1. **chattoner-back** (Python FastAPI Backend)
   - URL: https://chattoner-back-184664486594.asia-northeast3.run.app
   - Region: asia-northeast3
   - Image Registry: gcr.io/chattoner-project/chattoner-back:latest
   - Port: 8080 (auto-set by Cloud Run, do NOT manually set PORT env var)
   - Resources: 2Gi memory, 2 CPU
   - Scaling: 0-10 instances, max-scale 20
   - Database: Cloud SQL PostgreSQL (10.118.192.2)
   - VPC: run-to-db-connector (private-ranges-only egress)

2. **client** (React Frontend)
   - Separate Cloud Run service
   - Build config: cloudbuild.yaml (root)

### Cloud Build Triggers
- **deploy-backend** (ID: 350f774a-9a95-4852-b8f4-798a3933593a)
  - Config: `python_backend/cloudbuild.yaml`
  - Trigger: Push to main branch in python_backend/**
  - Repository: APPS-sookmyung/CHAT-TONER

- **chattoner-client** (ID: 6dd0055b-6a26-4126-bd0f-bc729668c610)
  - Config: `cloudbuild.yaml` (root)
  - Trigger: Push to main branch

### Environment Variables (chattoner-back)
```
ENVIRONMENT=production
env.FASTAPI_URL=https://chattoner-back-184664486594.asia-northeast3.run.app
DB_HOST=10.118.192.2
DB_USER=chattoner-user
DB_PASS=r~o+^[uD@6+p,kby
DB_NAME=chattoner
DB_PORT=5432
```

### Cloud SQL Connection
- Instance: chattoner-project:asia-northeast3:chattoner
- Private IP: 10.118.192.2
- Connected via VPC connector: run-to-db-connector

### Known Deployment Issues (Resolved & Pending)

#### ✅ Resolved
1. **PORT env conflict**: Cloud Run automatically sets PORT - do not set it manually in cloudbuild.yaml (Fixed)
2. **Image mismatch**: Previously Express server was deployed instead of FastAPI backend (Fixed - using main:app)
3. **SessionMiddleware**: Import path corrected to `starlette.middleware.sessions` (Currently disabled)
4. **Frontend-Backend connection**: Nginx proxy configured for `/api/*` requests (Working)

#### ⚠️ Pending
1. **DATABASE_URL special characters**: Password needs URL encoding
   - Current: `r~o+^[uD@6+p,kby`
   - Needed: `r~o%2B%5E%5BuD%406%2Bp%2Ckby`
   - Status: Currently using SQLite fallback

2. **Cloud Build Trigger File Filters**: Need to add file filters in GCP Console
   - `deploy-backend` trigger → add `python_backend/**`
   - `chattoner-client` trigger → add `client/**`
   - Currently: All triggers run on every push

### Registry Paths
- Production images: gcr.io/chattoner-project/
- Legacy source deploy: asia-northeast3-docker.pkg.dev/cloud-run-source-deploy/

### Quick Reference
- **Backend URL**: https://chattoner-back-3yj2y7svbq-du.a.run.app
- **Frontend URL**: https://client-3yj2y7svbq-du.a.run.app
- **Deployment Summary**: See `DEPLOYMENT_SUMMARY.md` for complete details