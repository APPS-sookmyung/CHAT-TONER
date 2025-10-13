#!/bin/bash
# Cloud Build Triggers Setup Script
# Run this script to create all Cloud Build triggers for CI/CD

set -e

echo "========================================"
echo "Cloud Build Triggers Setup"
echo "========================================"
echo ""

# Variables
REPO_OWNER="APPS-sookmyung"
REPO_NAME="CHAT-TONER"
BRANCH_PATTERN="^main$"

echo "Repository: ${REPO_OWNER}/${REPO_NAME}"
echo "Branch: main"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "Error: Not authenticated with gcloud. Run 'gcloud auth login'"
    exit 1
fi

echo "Step 1/5: Creating 'deploy-client' trigger..."
gcloud builds triggers create github \
  --name="deploy-client" \
  --description="Deploy client to Cloud Run when client/ changes" \
  --repo-owner="${REPO_OWNER}" \
  --repo-name="${REPO_NAME}" \
  --branch-pattern="${BRANCH_PATTERN}" \
  --build-config="client/cloudbuild.yaml" \
  --included-files="client/**"

echo "✓ deploy-client trigger created"
echo ""

echo "Step 2/5: Creating 'deploy-backend' trigger..."
gcloud builds triggers create github \
  --name="deploy-backend" \
  --description="Deploy FastAPI backend to Cloud Run when python_backend/ changes" \
  --repo-owner="${REPO_OWNER}" \
  --repo-name="${REPO_NAME}" \
  --branch-pattern="${BRANCH_PATTERN}" \
  --build-config="python_backend/cloudbuild.yaml" \
  --included-files="python_backend/**,requirements.txt"

echo "✓ deploy-backend trigger created"
echo ""

echo "Step 3/5: Creating 'deploy-gateway' trigger..."
gcloud builds triggers create github \
  --name="deploy-gateway" \
  --description="Deploy NestJS gateway to Cloud Run when nestjs-gateway/ changes" \
  --repo-owner="${REPO_OWNER}" \
  --repo-name="${REPO_NAME}" \
  --branch-pattern="${BRANCH_PATTERN}" \
  --build-config="nestjs-gateway/cloudbuild.yaml" \
  --included-files="nestjs-gateway/**"

echo "✓ deploy-gateway trigger created"
echo ""

echo "Step 4/5: Creating 'run-db-migrations' manual trigger..."
gcloud builds triggers create manual \
  --name="run-db-migrations" \
  --description="Run database migrations manually" \
  --build-config="database/cloudbuild.yaml"

echo "✓ run-db-migrations trigger created"
echo ""

echo "Step 5/5: Granting Cloud Build permissions..."

PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")

# Grant Secret Manager access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None \
  > /dev/null 2>&1

# Grant Cloud Run admin
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin" \
  --condition=None \
  > /dev/null 2>&1

# Grant Service Account User
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --condition=None \
  > /dev/null 2>&1

echo "✓ Permissions granted"
echo ""

echo "========================================"
echo "✓ All triggers created successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Create secrets in Secret Manager:"
echo "   gcloud secrets create DATABASE_URL"
echo "   gcloud secrets create OPENAI_API_KEY"
echo ""
echo "2. View triggers:"
echo "   https://console.cloud.google.com/cloud-build/triggers"
echo ""
echo "3. Push to main branch to trigger automatic deployment!"
echo ""
