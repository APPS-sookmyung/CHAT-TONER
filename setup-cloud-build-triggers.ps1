# Cloud Build Triggers Setup Script (PowerShell)
# Run this script to create all Cloud Build triggers for CI/CD

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cloud Build Triggers Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$REPO_OWNER = "APPS-sookmyung"
$REPO_NAME = "CHAT-TONER"
$BRANCH_PATTERN = "^main$"

Write-Host "Repository: $REPO_OWNER/$REPO_NAME"
Write-Host "Branch: main"
Write-Host ""

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "Error: gcloud CLI is not installed" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1/5: Creating 'deploy-client' trigger..." -ForegroundColor Yellow
gcloud builds triggers create github `
  --name="deploy-client" `
  --description="Deploy client to Cloud Run when client/ changes" `
  --repo-owner="$REPO_OWNER" `
  --repo-name="$REPO_NAME" `
  --branch-pattern="$BRANCH_PATTERN" `
  --build-config="client/cloudbuild.yaml" `
  --included-files="client/**"

Write-Host "✓ deploy-client trigger created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2/5: Creating 'deploy-backend' trigger..." -ForegroundColor Yellow
gcloud builds triggers create github `
  --name="deploy-backend" `
  --description="Deploy FastAPI backend to Cloud Run when python_backend/ changes" `
  --repo-owner="$REPO_OWNER" `
  --repo-name="$REPO_NAME" `
  --branch-pattern="$BRANCH_PATTERN" `
  --build-config="python_backend/cloudbuild.yaml" `
  --included-files="python_backend/**,requirements.txt"

Write-Host "✓ deploy-backend trigger created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3/5: Creating 'deploy-gateway' trigger..." -ForegroundColor Yellow
gcloud builds triggers create github `
  --name="deploy-gateway" `
  --description="Deploy NestJS gateway to Cloud Run when nestjs-gateway/ changes" `
  --repo-owner="$REPO_OWNER" `
  --repo-name="$REPO_NAME" `
  --branch-pattern="$BRANCH_PATTERN" `
  --build-config="nestjs-gateway/cloudbuild.yaml" `
  --included-files="nestjs-gateway/**"

Write-Host "✓ deploy-gateway trigger created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4/5: Creating 'run-db-migrations' manual trigger..." -ForegroundColor Yellow
gcloud builds triggers create manual `
  --name="run-db-migrations" `
  --description="Run database migrations manually" `
  --build-config="database/cloudbuild.yaml"

Write-Host "✓ run-db-migrations trigger created" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5/5: Granting Cloud Build permissions..." -ForegroundColor Yellow

$PROJECT_ID = gcloud config get-value project
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor" `
  --condition=None `
  | Out-Null

# Grant Cloud Run admin
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" `
  --role="roles/run.admin" `
  --condition=None `
  | Out-Null

# Grant Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" `
  --role="roles/iam.serviceAccountUser" `
  --condition=None `
  | Out-Null

Write-Host "✓ Permissions granted" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ All triggers created successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create secrets in Secret Manager:"
Write-Host "   gcloud secrets create DATABASE_URL"
Write-Host "   gcloud secrets create OPENAI_API_KEY"
Write-Host ""
Write-Host "2. View triggers:"
Write-Host "   https://console.cloud.google.com/cloud-build/triggers"
Write-Host ""
Write-Host "3. Push to main branch to trigger automatic deployment!"
Write-Host ""
