# Google Cloud Tasks Setup for CCM 2.0

## Overview

This document provides step-by-step instructions for setting up Google Cloud Tasks as a general-purpose task queue system in CCM 2.0. While the initial use case is automated email sending, the system is designed to be reusable for any delayed or background processing needs.

## Prerequisites

- Google Cloud Project with billing enabled (`ccm-dev-pool` for development)
- Cloud Run service deployed (for task execution endpoints)
- Appropriate IAM permissions to create Cloud Tasks queues
- `gcloud` CLI installed and authenticated

## Step 1: Enable Cloud Tasks API

```bash
# Set project context
gcloud config set project ccm-dev-pool

# Enable the Cloud Tasks API
gcloud services enable cloudtasks.googleapis.com

# Verify API is enabled
gcloud services list --enabled --filter="name:cloudtasks.googleapis.com"
```

## Step 2: Configure CMEK Exception for Cloud Tasks

Due to the organization policy `constraints/gcp.restrictNonCmekServices`, we need to temporarily disable it to create Cloud Tasks queues, as Cloud Tasks doesn't support CMEK directly.

### Important Security Note
Cloud Tasks doesn't support Customer-Managed Encryption Keys (CMEK). We're creating queues with a temporary exception because:
1. Task data is temporary (exists only until execution)
2. We store only references/IDs in tasks, not sensitive data
3. Actual sensitive data remains in CMEK-protected Firestore
4. This is a common and accepted practice for Cloud Tasks

### Step 2a: Temporarily Disable CMEK Requirement

```bash
# Apply the policy exception to temporarily disable CMEK requirement for the project
# This uses the file: cloud-tasks-policy-exception.yaml
gcloud org-policies set-policy cloud-tasks-policy-exception.yaml --project=ccm-dev-pool
```

⚠️ **IMPORTANT**: This disables CMEK for the entire project temporarily. Proceed quickly to Step 3 to create the queues, then immediately restore the policy in Step 4.

**Security Best Practices:**
- ✅ Only store task IDs and references in Cloud Tasks payloads
- ✅ Keep sensitive data in CMEK-protected Firestore
- ✅ Document this exception in your security documentation
- ✅ Monitor task payloads to ensure no sensitive data is included

## Step 3: Create Cloud Tasks Queues (Quickly!)

**Execute these commands immediately after Step 2a while CMEK is disabled:**

```bash
# Set variables (Windows Command Prompt)
set PROJECT_ID=ccm-dev-pool
set REGION=us-east4

REM Note: Cloud Tasks doesn't support southamerica-west1
REM Using us-east4 (Northern Virginia) to match existing VPC infrastructure
REM To see all available locations: gcloud tasks locations list

# Create general-purpose queue for various background tasks
gcloud tasks queues create general-tasks --location=%REGION% --max-concurrent-dispatches=20 --max-dispatches-per-second=10 --max-attempts=3 --min-backoff=30s --max-backoff=3600s

# Create email-specific queue with controlled rate limits  
gcloud tasks queues create email-tasks --location=%REGION% --max-concurrent-dispatches=5 --max-dispatches-per-second=2 --max-attempts=3 --min-backoff=60s --max-backoff=3600s

# Create high-priority queue for urgent tasks
gcloud tasks queues create priority-tasks --location=%REGION% --max-concurrent-dispatches=10 --max-dispatches-per-second=5 --max-attempts=5 --min-backoff=10s --max-backoff=1800s

# Verify queue creation
gcloud tasks queues list --location=%REGION%
```

## Step 4: Restore CMEK Requirement (IMPORTANT!)

**Immediately after creating the queues, restore the CMEK requirement:**

```bash
# Restore the organization's CMEK policy
# This uses the file: cloud-tasks-policy-restore.yaml
gcloud org-policies set-policy cloud-tasks-policy-restore.yaml --project=ccm-dev-pool

# Verify the policy is restored
gcloud org-policies describe gcp.restrictNonCmekServices --project=ccm-dev-pool
```

✅ **Result**: The Cloud Tasks queues will continue to function normally, but CMEK protection is restored for all other services (Firestore, etc.).

### Queue Configuration Rationale

**general-tasks**: For standard background processing (file uploads, data processing, etc.)
- High concurrency for throughput
- Moderate retry policy
- General-purpose configuration

**email-tasks**: For email sending with rate limiting
- Lower concurrency to respect email service limits
- Conservative retry policy to avoid spam flags
- Longer backoff to handle temporary email service issues

**priority-tasks**: For urgent system notifications
- Moderate concurrency 
- Aggressive retry policy with shorter backoffs
- For critical system functions

## Step 5: Service Account and IAM Setup

```bash
# Create dedicated service account for Cloud Tasks
gcloud iam service-accounts create cloud-tasks-manager \
    --display-name="Cloud Tasks Manager" \
    --description="Service account for creating and managing Cloud Tasks across CCM 2.0"

# Grant task creation permissions
gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:cloud-tasks-manager@%PROJECT_ID%.iam.gserviceaccount.com" --role="roles/cloudtasks.enqueuer"

# Grant task execution permissions  
gcloud projects add-iam-policy-binding %PROJECT_ID% --member="serviceAccount:cloud-tasks-manager@%PROJECT_ID%.iam.gserviceaccount.com" --role="roles/cloudtasks.taskRunner"

# Allow main application service account to use Cloud Tasks service account
gcloud iam service-accounts add-iam-policy-binding cloud-tasks-manager@%PROJECT_ID%.iam.gserviceaccount.com --member="serviceAccount:gmail-email-processor@%PROJECT_ID%.iam.gserviceaccount.com" --role="roles/iam.serviceAccountTokenCreator"
```

## Step 6: Cloud Run Service Configuration

⚠️ **SKIP FOR NOW - Future Cloud Run Deployment Only**

This step is only needed when you deploy your backend to Cloud Run. For local development, skip to Step 8.

**When to return to this step:**
- After deploying your FastAPI backend to Cloud Run
- When moving from local development to production deployment
- When you have an actual Cloud Run service name to configure

### Grant Cloud Tasks permission to invoke Cloud Run

```bash
# Get your Cloud Run service name (replace with actual name)
set CLOUD_RUN_SERVICE=your-backend-service

# Allow Cloud Tasks to invoke your Cloud Run service
gcloud run services add-iam-policy-binding %CLOUD_RUN_SERVICE% --region=%REGION% --member="serviceAccount:cloud-tasks-manager@%PROJECT_ID%.iam.gserviceaccount.com" --role="roles/run.invoker"

# Also allow the default compute service account (backup)
gcloud run services add-iam-policy-binding %CLOUD_RUN_SERVICE% --region=%REGION% --member="serviceAccount:%PROJECT_ID%-compute@developer.gserviceaccount.com" --role="roles/run.invoker"
```

### Environment Variables for Cloud Run

⚠️ **SKIP FOR NOW - Future Cloud Run Deployment Only**

These environment variables are only needed for Cloud Run deployment. For local development, you'll set these in your local environment or `.env` file instead.

**Future Cloud Run deployment configuration:**

```yaml
env:
  - name: GOOGLE_CLOUD_PROJECT
    value: "ccm-dev-pool"
  - name: CLOUD_TASKS_LOCATION
    value: "us-east4"
  - name: CLOUD_TASKS_GENERAL_QUEUE
    value: "general-tasks"
  - name: CLOUD_TASKS_EMAIL_QUEUE
    value: "email-tasks"
  - name: CLOUD_TASKS_PRIORITY_QUEUE
    value: "priority-tasks"
  - name: CLOUD_RUN_URL
    value: "https://your-backend-service-url.run.app"
```

## Step 8: Python Dependencies

Add to your `requirements.txt`:

```txt
google-cloud-tasks==2.14.1
```

## Step 9: Task Queue Architecture

⚠️ **INFORMATIONAL ONLY - Code Already Implemented**

This section explains the architecture of the task queue system. The actual code is already implemented in:
- `backend/src/services/task_queue_service.py` (main service)
- `backend/src/api/routes/internal_tasks.py` (task execution endpoints)
- `backend/src/services/auto_email_service.py` (email-specific tasks)

### Task Types and Routing (Reference)

```python
# This configuration is already implemented in task_queue_service.py
TASK_QUEUES = {
    'email': {
        'queue_name': 'email-tasks',
        'endpoint': '/api/internal/tasks/email',
        'max_delay_seconds': 86400  # 24 hours
    },
    'data_processing': {
        'queue_name': 'general-tasks', 
        'endpoint': '/api/internal/tasks/data-processing',
        'max_delay_seconds': 3600   # 1 hour
    },
    'notifications': {
        'queue_name': 'priority-tasks',
        'endpoint': '/api/internal/tasks/notifications', 
        'max_delay_seconds': 300    # 5 minutes
    },
    'file_processing': {
        'queue_name': 'general-tasks',
        'endpoint': '/api/internal/tasks/file-processing',
        'max_delay_seconds': 7200   # 2 hours
    }
}
```

### Internal API Endpoints Structure (Reference)

These endpoints are already implemented in `backend/src/api/routes/internal_tasks.py`:

All task execution endpoints follow the pattern: `/api/internal/tasks/{task_type}`

- `POST /api/internal/tasks/email` - Email sending tasks
- `POST /api/internal/tasks/data-processing` - Data processing tasks  
- `POST /api/internal/tasks/notifications` - System notifications
- `POST /api/internal/tasks/file-processing` - File upload/processing tasks

## Step 10: Security Implementation

ℹ️ **INFORMATIONAL ONLY - Security Already Implemented**

The security features described below are already implemented in the task queue service code. This section is for reference and understanding.

### Task Authentication Headers (Automatic)

Cloud Tasks automatically includes these headers:

```http
X-CloudTasks-QueueName: projects/PROJECT_ID/locations/LOCATION/queues/QUEUE_NAME
X-CloudTasks-TaskName: projects/PROJECT_ID/locations/LOCATION/queues/QUEUE_NAME/tasks/TASK_NAME
X-CloudTasks-TaskRetryCount: 0
X-CloudTasks-TaskExecutionCount: 1
```

### Request Verification Middleware (Already Implemented)

This security verification is already implemented in `backend/src/services/task_queue_service.py`:

```python
# This code is already implemented in task_queue_service.py
def verify_cloud_task_request(request):
    """Verify request authenticity from Cloud Tasks"""
    # Check required headers exist
    queue_name = request.headers.get('X-CloudTasks-QueueName')
    task_name = request.headers.get('X-CloudTasks-TaskName')
    
    if not queue_name or not task_name:
        raise HTTPException(status_code=401, detail="Missing Cloud Tasks headers")
    
    # Verify queue belongs to our project
    expected_queues = ['general-tasks', 'email-tasks', 'priority-tasks']
    if not any(queue in queue_name for queue in expected_queues):
        raise HTTPException(status_code=401, detail="Invalid task queue")
    
    return True
```

## Step 11: Monitoring and Observability

ℹ️ **INFORMATIONAL ONLY - Future Reference**

This section provides monitoring queries you can use later to monitor your Cloud Tasks performance. No action needed now.

### Useful Cloud Monitoring Metrics (Future Reference)

```sql
-- Task execution rate by queue
cloudtasks.googleapis.com/api/request_count{queue_name=~".*"}

-- Task queue depth (pending tasks)
cloudtasks.googleapis.com/queue/depth{queue_name=~".*"}

-- Task execution latency
cloudtasks.googleapis.com/task/attempt_delay{queue_name=~".*"}

-- Failed task rate
cloudtasks.googleapis.com/api/request_count{response_code!="200"}
```

### Cloud Logging Queries

```sql
-- All Cloud Tasks related logs
resource.type="cloud_tasks_queue"
resource.labels.project_id="ccm-dev-pool"

-- Failed task executions
resource.type="cloud_tasks_queue" 
severity>=ERROR

-- Specific queue activity
resource.type="cloud_tasks_queue"
resource.labels.queue_id="email-tasks"
```

## Step 12: Development vs Production Configuration

### Development Environment (`ccm-dev-pool`)
- Uses existing service accounts and IAM setup
- Lower rate limits for testing
- Shorter retry delays for faster development cycles
- All queues in `southamerica-west1` region

### Production Environment (Future)
- Dedicated service accounts per environment
- Production-grade rate limits and retry policies
- Multi-region deployment for high availability
- Enhanced monitoring and alerting

## Step 13: Testing the Setup

### Manual Task Creation Test

**Prerequisites:** Make sure your local backend is running on `http://localhost:8000`

```cmd
REM Set variables for Windows
set REGION=us-east4
set BACKEND_URL=http://localhost:8000

REM Test general tasks queue
gcloud tasks create-http-task test-general-task-%RANDOM% --queue=general-tasks --location=%REGION% --url="%BACKEND_URL%/api/internal/tasks/data-processing" --method=POST --body-content="{\"test\": \"general task\", \"timestamp\": \"2024-08-28T19:30:00Z\"}" --header="Content-Type: application/json"

REM Test email tasks queue  
gcloud tasks create-http-task test-email-task-%RANDOM% --queue=email-tasks --location=%REGION% --url="%BACKEND_URL%/api/internal/tasks/email" --method=POST --body-content="{\"test\": \"email task\", \"timestamp\": \"2024-08-28T19:30:00Z\"}" --header="Content-Type: application/json"

REM Test priority tasks queue
gcloud tasks create-http-task test-priority-task-%RANDOM% --queue=priority-tasks --location=%REGION% --url="%BACKEND_URL%/api/internal/tasks/notifications" --method=POST --body-content="{\"test\": \"priority task\", \"timestamp\": \"2024-08-28T19:30:00Z\"}" --header="Content-Type: application/json"

REM Test with 2-minute delay (scheduled execution)
gcloud tasks create-http-task test-scheduled-task-%RANDOM% --queue=priority-tasks --location=%REGION% --url="%BACKEND_URL%/api/internal/tasks/notifications" --method=POST --body-content="{\"test\": \"scheduled task\", \"timestamp\": \"2024-08-28T19:30:00Z\"}" --header="Content-Type: application/json" --schedule-time="2024-08-28T19:32:00Z"
```

**Getting Current UTC Time:**
```cmd
REM Get current UTC time (for immediate tasks)
powershell -Command "Get-Date (Get-Date).ToUniversalTime() -Format 'yyyy-MM-ddTHH:mm:ssZ'"

REM Get UTC time 5 minutes from now (for scheduled tasks)
powershell -Command "Get-Date (Get-Date).ToUniversalTime().AddMinutes(5) -Format 'yyyy-MM-ddTHH:mm:ssZ'"
```

**Note:** 
- For immediate tasks, the timestamp in `--body-content` is just metadata
- For scheduled tasks, update the `--schedule-time` parameter with a future UTC time
- All times use UTC timezone (indicated by the "Z" suffix)

### Verification Commands

```bash
# List all queues and their status
gcloud tasks queues list --location=$REGION

# Check queue details and stats
gcloud tasks queues describe general-tasks --location=$REGION
gcloud tasks queues describe email-tasks --location=$REGION
gcloud tasks queues describe priority-tasks --location=$REGION

# List active tasks (if any)
gcloud tasks list --queue=general-tasks --location=$REGION
gcloud tasks list --queue=email-tasks --location=$REGION
gcloud tasks list --queue=priority-tasks --location=$REGION
```

## Configuration Summary

### Queues Created
- **general-tasks**: High throughput, general-purpose processing
- **email-tasks**: Rate-limited email sending with conservative retries
- **priority-tasks**: Fast execution for urgent system tasks

### Service Accounts
- **cloud-tasks-manager**: Dedicated for Cloud Tasks operations
- Integrated with existing **gmail-email-processor** service account

### Security Features
- Request header verification for task authenticity
- IAM-based access control for queue operations
- Service-to-service authentication for Cloud Run invocation

### Monitoring
- Built-in Cloud Monitoring metrics for all queues
- Centralized logging for task execution and failures
- Performance and reliability dashboards available

This setup provides a robust, scalable, and reusable task queue foundation that can support automated email sending and future background processing needs across the CCM 2.0 platform.

---

**Next Steps:**
1. Execute the setup commands in your `ccm-dev-pool` project
2. Update your Cloud Run service with the environment variables
3. Implement the TaskQueueService class (see implementation documentation)
4. Test with manual task creation to verify end-to-end functionality