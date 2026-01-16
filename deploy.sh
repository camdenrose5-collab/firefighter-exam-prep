#!/bin/bash
# =============================================================================
# Google Cloud Run Deployment Script
# Firefighter Exam Prep API
# =============================================================================

set -e  # Exit on error

# -----------------------------------------------------------------------------
# CONFIGURATION - Update these values
# -----------------------------------------------------------------------------
PROJECT_ID="project-bdf7b730-5186-489d-b01"           # Your Google Cloud project ID
SERVICE_NAME="firefighter-prep-api"     # Cloud Run service name
REGION="us-central1"                    # Deployment region
REPO_NAME="firefighter-repo"            # Artifact Registry repository name
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

# -----------------------------------------------------------------------------
# ENVIRONMENT VARIABLES - These will be set in Cloud Run
# Copy values from your .env.production file
# -----------------------------------------------------------------------------
# IMPORTANT: Don't commit real secrets! Set these before running or use Secret Manager

SECRET_KEY="${SECRET_KEY:-CHANGE_ME}"
DATA_STORE_ID="${DATA_STORE_ID:-your-data-store-id}"

# -----------------------------------------------------------------------------
# PRE-FLIGHT CHECKS
# -----------------------------------------------------------------------------
echo "🔥 Firefighter Exam Prep - Cloud Run Deployment"
echo "================================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if logged in
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null)
if [ -z "$ACCOUNT" ]; then
    echo "❌ Not logged in to gcloud. Run: gcloud auth login"
    exit 1
fi

echo "✅ Logged in as: $ACCOUNT"
echo "📦 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🐳 Image: $IMAGE_NAME"
echo ""

# Confirm before proceeding
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# -----------------------------------------------------------------------------
# STEP 1: Set the project
# -----------------------------------------------------------------------------
echo ""
echo "📌 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# -----------------------------------------------------------------------------
# STEP 2: Enable required APIs (if not already enabled)
# -----------------------------------------------------------------------------
echo ""
echo "🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    discoveryengine.googleapis.com \
    --quiet

# -----------------------------------------------------------------------------
# STEP 3: Build and push the container image
# -----------------------------------------------------------------------------
echo ""
echo "🐳 Building container image with Cloud Build..."
gcloud builds submit --tag $IMAGE_NAME .

# -----------------------------------------------------------------------------
# STEP 4: Deploy to Cloud Run
# -----------------------------------------------------------------------------
echo ""
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars="NODE_ENV=production" \
    --set-env-vars="SECRET_KEY=${SECRET_KEY}" \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars="DATA_STORE_ID=${DATA_STORE_ID}" \
    --set-env-vars="VERTEX_MODEL=gemini-2.0-flash-001"

# -----------------------------------------------------------------------------
# STEP 5: Get the service URL
# -----------------------------------------------------------------------------
echo ""
echo "✅ Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "   1. Update your frontend NEXT_PUBLIC_API_URL to: $SERVICE_URL"
echo "   2. Test the health endpoint: curl $SERVICE_URL/api/health"
echo "   3. Check logs: gcloud run logs tail $SERVICE_NAME --region $REGION"
echo ""
echo "🔥 Your Firefighter Exam Prep API is live!"
