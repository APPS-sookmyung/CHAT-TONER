# Cloud Build Setup Guide

## Overview
This project uses separate Cloud Build configurations for each service to enable independent builds and deployments.

## File Structure
```
├── client/cloudbuild.yaml          # Frontend (React)
├── python_backend/cloudbuild.yaml  # FastAPI Backend
├── nestjs-gateway/cloudbuild.yaml  # NestJS Gateway
└── database/cloudbuild.yaml        # Database Migrations
```

---

## Prerequisites

### 1. Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Create Secrets in Secret Manager
```bash
# Database connection string
gcloud secrets create DATABASE_URL --data-file=- <<< "postgresql://user:pass@host:5432/dbname"

# OpenAI API Key (for backend)
gcloud secrets create OPENAI_API_KEY --data-file=- <<< "sk-..."
```

### 3. Grant Cloud Build Permissions
```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Grant Cloud Run admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

---

## Setting Up Cloud Build Triggers

### Option 1: Using gcloud CLI

#### 1. Client (Frontend) Trigger
```bash
gcloud builds triggers create github \
  --name="deploy-client" \
  --repo-name="2025-CHATTONER-Server" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="client/cloudbuild.yaml" \
  --included-files="client/**" \
  --description="Build and deploy frontend when client/ changes"
```

#### 2. Python Backend Trigger
```bash
gcloud builds triggers create github \
  --name="deploy-backend" \
  --repo-name="2025-CHATTONER-Server" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="python_backend/cloudbuild.yaml" \
  --included-files="python_backend/**,requirements.txt" \
  --description="Build and deploy FastAPI backend when python_backend/ changes"
```

#### 3. NestJS Gateway Trigger
```bash
gcloud builds triggers create github \
  --name="deploy-gateway" \
  --repo-name="2025-CHATTONER-Server" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="nestjs-gateway/cloudbuild.yaml" \
  --included-files="nestjs-gateway/**" \
  --description="Build and deploy NestJS gateway when nestjs-gateway/ changes"
```

#### 4. Database Migration Trigger (Manual)
```bash
gcloud builds triggers create manual \
  --name="run-db-migrations" \
  --build-config="database/cloudbuild.yaml" \
  --description="Run database migrations manually"
```

### Option 2: Using Google Cloud Console

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click **"CREATE TRIGGER"**
3. Configure each trigger:

#### Client Trigger
- **Name**: `deploy-client`
- **Event**: Push to branch
- **Source**: Connect your GitHub repository
- **Branch**: `^main$`
- **Build configuration**: Cloud Build configuration file
- **Location**: `client/cloudbuild.yaml`
- **Included files filter**: `client/**`

#### Backend Trigger
- **Name**: `deploy-backend`
- **Event**: Push to branch
- **Source**: Connect your GitHub repository
- **Branch**: `^main$`
- **Build configuration**: Cloud Build configuration file
- **Location**: `python_backend/cloudbuild.yaml`
- **Included files filter**: `python_backend/**,requirements.txt`

#### Gateway Trigger
- **Name**: `deploy-gateway`
- **Event**: Push to branch
- **Source**: Connect your GitHub repository
- **Branch**: `^main$`
- **Build configuration**: Cloud Build configuration file
- **Location**: `nestjs-gateway/cloudbuild.yaml`
- **Included files filter**: `nestjs-gateway/**`

#### Database Migration Trigger
- **Name**: `run-db-migrations`
- **Event**: Manual invocation
- **Build configuration**: Cloud Build configuration file
- **Location**: `database/cloudbuild.yaml`

---

## Manual Build Commands

### Build and Deploy Client
```bash
gcloud builds submit --config=client/cloudbuild.yaml client/
```

### Build and Deploy Backend
```bash
gcloud builds submit --config=python_backend/cloudbuild.yaml python_backend/
```

### Build and Deploy Gateway
```bash
gcloud builds submit --config=nestjs-gateway/cloudbuild.yaml nestjs-gateway/
```

### Run Database Migrations
```bash
gcloud builds submit --config=database/cloudbuild.yaml .
```

---

## Environment Variables

### Python Backend
Required secrets (stored in Secret Manager):
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key

Environment variables (set in cloudbuild.yaml):
- `ENVIRONMENT=production`
- `PORT=8080`

### NestJS Gateway
Environment variables (set in cloudbuild.yaml):
- `NODE_ENV=production`
- `PORT=3000`
- `BACKEND_API_URL` - URL of the FastAPI backend (update after first backend deployment)

**Important**: After deploying the backend, update `BACKEND_API_URL` in `nestjs-gateway/cloudbuild.yaml`:
```yaml
--set-env-vars
- 'NODE_ENV=production,PORT=3000,BACKEND_API_URL=https://chattoner-backend-XXXXX-an.a.run.app'
```

---

## Deployment Flow

### Initial Setup (First Time)
1. Run database migrations:
   ```bash
   gcloud builds submit --config=database/cloudbuild.yaml .
   ```

2. Deploy backend:
   ```bash
   gcloud builds submit --config=python_backend/cloudbuild.yaml python_backend/
   ```

3. Get backend URL and update gateway config:
   ```bash
   gcloud run services describe chattoner-backend --region=asia-northeast3 --format="value(status.url)"
   ```
   Update `BACKEND_API_URL` in `nestjs-gateway/cloudbuild.yaml`

4. Deploy gateway:
   ```bash
   gcloud builds submit --config=nestjs-gateway/cloudbuild.yaml nestjs-gateway/
   ```

5. Deploy client:
   ```bash
   gcloud builds submit --config=client/cloudbuild.yaml client/
   ```

### Subsequent Updates (Automatic via GitHub)
After setting up triggers, pushing to `main` branch will automatically:
- Build only the changed service
- Deploy to Cloud Run
- Keep other services unchanged

---

## Monitoring Builds

### View Build History
```bash
gcloud builds list --limit=10
```

### View Specific Build Logs
```bash
gcloud builds log BUILD_ID
```

### View in Console
[Cloud Build History](https://console.cloud.google.com/cloud-build/builds)

---

## Troubleshooting

### Build Fails: "Permission Denied"
Grant Cloud Build service account the required permissions (see Prerequisites section)

### Build Fails: "Secret not found"
Create secrets in Secret Manager:
```bash
gcloud secrets create DATABASE_URL
gcloud secrets create OPENAI_API_KEY
```

### Gateway Can't Connect to Backend
Update `BACKEND_API_URL` in `nestjs-gateway/cloudbuild.yaml` with the actual backend URL

### Database Migration Fails
Check PostgreSQL connection string in `DATABASE_URL` secret

---

## Cost Optimization

Each service uses:
- **E2_HIGHCPU_8** machine type (adjust to E2_MEDIUM for smaller projects)
- Separate builds only trigger when specific paths change
- Cloud Run scales to zero when not in use

To reduce costs:
- Change `machineType: 'E2_MEDIUM'` in cloudbuild.yaml files
- Reduce `diskSizeGb` if builds are small
- Use `--min-instances=0` for services (already configured)

---

## Service URLs

After deployment, get service URLs:
```bash
# Backend
gcloud run services describe chattoner-backend --region=asia-northeast3 --format="value(status.url)"

# Gateway
gcloud run services describe chattoner-gateway --region=asia-northeast3 --format="value(status.url)"

# Client
gcloud run services describe chattoner-client --region=asia-northeast3 --format="value(status.url)"
```
