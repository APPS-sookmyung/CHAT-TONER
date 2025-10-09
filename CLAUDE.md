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
- api 목록 중에 구조가 물아정한거 프론트 백 다 찾아줘