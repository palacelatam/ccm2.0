# Google Cloud Platform: `palace.cl` Organization Architecture & Security Summary

**Document Version:** 1.2  
**Date:** August 14, 2025  
**Author:** Gemini AI Assistant (Updated by Claude Code)

## 1.0 Introduction & Strategic Objectives

This document provides a detailed and comprehensive summary of the foundational setup for the Google Cloud Platform (GCP) Organization `palace.cl`. The primary objective of this foundation is to provide a secure, scalable, and compliant platform for the development and operation of enterprise-level Software-as-a-Service (SaaS) applications, with a specific focus on meeting the stringent requirements of the industry.

The entire foundation was configured using the Google Cloud Foundation Setup guide and was ultimately downloaded as a complete Infrastructure as Code (IaC) project using Terraform. This ensures that the environment is repeatable, version-controllable, and managed according to modern best practices.

The key strategic pillars underpinning this architecture are:
* **Security by Default:** Implementing a strong security posture from the outset, using Google Cloud's recommended best practices for identity, network security, and data encryption.
* **Scalability & Flexibility:** Building a resource hierarchy and network architecture that can support both shared (pooled) and dedicated (siloed) tenancy models to cater to a diverse range of banking clients.
* **Operational Excellence:** Leveraging Infrastructure as Code (IaC) for all foundational components to ensure reliability, prevent configuration drift, and enable automated, auditable changes.
* **Compliance Readiness:** Establishing a framework with centralized logging, organization-wide security policies, and customer-managed encryption keys to simplify the process of meeting financial industry compliance standards.

Please bear in mind that this was built using the best of our knowledge at the time. However, there may have been some amendments since then that have not been fully documented here.

---

## 2.0 SaaS Tenancy Model Strategy

* **Architecture:** A single, robust multi-tenant application is hosted within the production Shared VPC. This application serves many different clients from a shared infrastructure base.
* **Data Isolation:** Data segregation is enforced at the application and database layers. This is achieved through strict code logic and database design (e.g., ensuring every database query is scoped to the authenticated client's `tenant_id`, or using separate schemas per client within a shared database).
* **Prerequisites for Sale:** To successfully offer this model to financial clients, it is understood that rigorous proof of security is required. This includes obtaining third-party security certifications and audits, specifically **ISO 27001**, which validates the effectiveness of the application-level isolation controls.

---

## 3.0 Identity and Access Management (IAM)

The IAM strategy is built on the principle of least privilege and centralized, group-based management.

### 3.1 Identity Provider

* The foundation uses **Google Cloud Identity** as the central directory for managing users and groups associated with the **`palace.cl`** domain.
* The initial Super Administrator user is **`ben.clark@palace.cl`**.

### 3.2 Group-Based Permissions

All permissions are assigned to groups rather than individual users to simplify administration and reduce the risk of error. The Google Cloud Foundation setup created a comprehensive set of administrative groups, including:
* `gcp-organization-admins@palace.cl`: For top-level organization administration.
* `gcp-billing-admins@palace.cl`: For managing the billing account.
* `gcp-security-admins@palace.cl`: For managing security policies and monitoring.
* `gcp-network-admins@palace.cl`: For managing VPCs, subnets, and firewalls.
* `gcp-developers@palace.cl`: For application developers.
* `gcp-logging-monitoring-admins@palace.cl`: For administrators of the logging and monitoring services.
* `prod1-service@palace.cl`, `prod2-service@palace.cl`, etc.: Specific groups created for managing access to individual service projects.

### 3.3 IAM Role Assignments

The Terraform deployment applied a detailed set of IAM policies at the organization, folder, and project levels.
* **Organization Level:** Key administrative groups were granted high-level roles. For example, the `gcp-organization-admins` group was granted the `roles/resourcemanager.organizationAdmin` role, and the `gcp-billing-admins` group was granted the `roles/billing.admin` role.
* **Folder & Project Levels:** Permissions become more granular down the hierarchy. For example, the `gcp-developers` group was granted roles like `roles/compute.instanceAdmin.v1` at the folder level for non-production environments but has no inherent permissions at the organization level. This ensures developers have the access they need in development environments without having excessive permissions in production.

---

## 4.0 Resource Hierarchy

The organization follows a **"Simple, environment-oriented hierarchy"** model, designed for clarity and strong isolation between environments.

* **Organization:** `palace.cl` (ID: `165254678508`)
* **Folders:** The organization is structured into four top-level folders:
    * **`Production`**: Contains all projects and resources related to the live, customer-facing SaaS application. Access to this folder is the most restricted.
    * **`Non-Production`**: A container for all pre-production environments, including staging, QA, and user acceptance testing.
    * **`Development`**: Houses sandbox projects for developers to experiment and build new features without affecting shared testing environments. Contains the `ccm-dev-pool` project with CMEK-enabled Firestore database for persistent development data.
    * **`Common`**: A dedicated folder for shared services and resources that span across all environments. This includes the VPC host projects, the centralized logging and monitoring project, and the KMS Autokey projects.
* **Projects:** The Terraform deployment created a set of foundational projects, including:
    * **Host Projects:**
      * `vpc-host-prod-oj681-ps264` (Production networking)
      * `vpc-host-nonprod-pf819-wa214` (Non-production networking)
      * Located in the `Common` folder
    * **Service Projects:**
      * **Production:** `prod1-svc-5q4z`, `prod2-svc-5q4z` (in folder ID: 484625400602)
      * **Non-Production:** `nonprod1-svc-5q4z`, `nonprod2-svc-5q4z` (in folder ID: 441320525926)
    * **Development Service Project:** `ccm-dev-pool` (CCM2 - Dev Pool), located in the `Development` folder (ID: 802429588971), used for application development with persistent CMEK-enabled Firestore.
    * **Central Services Project:** `central-log-monitor-rp135-mx78`, located in the `Common` folder (ID: 883920606702).
    * **KMS Projects:**
      * Production: `kms-proj-g5c6fwjtocz9`
      * Non-Production: `kms-proj-3zwv12e1sndn`
      * Development: `kms-proj-nqs0vivc9gcm`

---

## 5.0 Networking (VPC Configuration)

The network architecture is built on the **Shared VPC** model and is designed for high availability and security.

### 5.1 Production Network: `vpc-prod-shared`

* **Host Project:** `vpc-host-prod-oj681-ps264`
* **Architecture:** Multi-regional for high availability.
* **Configuration:**
    * **`subnet-prod-1`**:
        * **Region:** `southamerica-west1` (Santiago)
        * **IP Range:** `10.1.1.0/24`
        * **Linked Service Project:** `prod1-svc-5q4z`
    * **`subnet-prod-2`**:
        * **Region:** `us-east4` (N. Virginia)
        * **IP Range:** `10.1.2.0/24`
        * **Linked Service Project:** `prod2-svc-5q4z`
    * **Common Settings:** For both subnets, **VPC Flow Logs** and **Private Google Access** are **On**, while **Cloud NAT** is **Off**. The network includes 3 default firewall rules.

### 5.2 Non-Production Network: `vpc-nonprod-shared`

* **Host Project:** `vpc-host-nonprod-pf819-wa214`
* **Architecture:** Mirrors the production network to ensure environment parity.
* **Configuration:**
    * **`subnet-non-prod-1`**:
        * **Region:** `southamerica-west1` (Santiago)
        * **IP Range:** `10.2.1.0/24`
        * **Linked Service Project:** `nonprod1-svc-5q4z`
    * **`subnet-non-prod-2`**:
        * **Region:** `us-east4` (N. Virginia)
        * **IP Range:** `10.2.2.0/24`
        * **Linked Service Project:** `nonprod2-svc-5q4z`
    * **Common Settings:** For both subnets, **VPC Flow Logs** and **Private Google Access** are **On**, while **Cloud NAT** is **Off**. The network includes 3 default firewall rules.

---

## 6.0 Security & Compliance Configuration

A multi-layered security strategy has been implemented across the organization.

### 6.1 Centralized Security Monitoring

* **Security Command Center (SCC) Standard Tier** has been enabled at the organization level. This provides a centralized dashboard for asset inventory, discovery, and reporting on vulnerabilities and misconfigurations across all projects.

### 6.2 Organization Policies

* A comprehensive set of recommended **Organization Policies** were applied at the root of the organization. These policies act as preventative guardrails, enforcing security best practices such as disabling the creation of default networks, preventing public access to storage buckets, and restricting the use of external IP addresses on virtual machines.
* **Service Account Key Restriction:** Organization policy `constraints/iam.disableServiceAccountKeyCreation` is enforced to prevent the creation of service account keys, enhancing security by encouraging the use of more secure authentication methods like Application Default Credentials (ADC) and Workload Identity.

### 6.3 Data Encryption Strategy

* **Customer-Managed Encryption Keys (CMEK):** A policy of using CMEK has been adopted to provide a higher level of control over data encryption, a key requirement for financial services.
* **Mandatory CMEK Policy:** Organization policy `constraints/gcp.restrictNonCmekServices` enforces CMEK usage across all services, ensuring no data is stored without customer-managed encryption.
* **Cloud KMS with Autokey:** This feature was enabled to automate and simplify the management of CMEK. It automatically creates and manages keyrings, keys, and IAM roles on a per-environment basis, enforcing a policy that requires new resources to be protected with these keys.
* **Development Environment CMEK Implementation:**
    * **Project:** `ccm-dev-pool` 
    * **KMS Keyring:** `ccm-dev-keyring` (location: `southamerica-west1`)
    * **Firestore Key:** `firestore-key` with minimal IAM permissions granted to Google's managed Firestore service account
    * **Database:** `ccm-development` Firestore database with CMEK encryption for persistent development data
* **Post-Deployment Considerations for Autokey:**
    * If new environment folders are added in the future, KMS projects and policies for those folders must be configured manually.
    * When deploying resources via Terraform or APIs, a "key handle" must be created manually, a step that is automated when using the Cloud Console.

### 6.4 Centralized Logging & Monitoring

* **Logging:** All organization-level audit logs are routed to a central log bucket named `palace-logging` within the `central-logging-monitoring` project. The default log retention period is set to **30 days**.
* **Monitoring:** A central metrics scope has been configured in the `central-logging-monitoring` project. This scope collects and displays metrics from all projects created by the foundation setup, providing a single pane of glass for system health and performance.

---

## 7.0 Development Environment Setup

### 7.1 Client Dashboard Development Environment

**Active Development Project:** `ccm-dev-pool` (Project Number: `1075260378031`)  
**Location:** Development folder (ID: `802429588971`)  
**Purpose:** Primary development environment for the CCM2.0 Client Dashboard application

**Database Configuration:**
* **Firestore Database:** `ccm-development`
* **Type:** Native Firestore with CMEK encryption
* **Location:** `southamerica-west1` (Santiago, Chile)
* **Encryption Key:** `projects/ccm-dev-pool/locations/southamerica-west1/keyRings/ccm-dev-keyring/cryptoKeys/firestore-key`
* **Connection Details:**
  ```typescript
  const projectId = "ccm-dev-pool";
  const databaseId = "ccm-development";
  ```

**Security Implementation:**
* CMEK encryption enforced by organization policy
* Minimal IAM permissions following Google Cloud security best practices
* Firestore service account (`service-1075260378031@gcp-sa-firestore.iam.gserviceaccount.com`) granted `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the encryption key

**Development Benefits:**
* Persistent data storage (no data loss on development environment restarts)
* Production-like security configuration for realistic testing
* Compliance with organizational CMEK requirements during development

---

## 8.0 Gmail API Integration for Email Automation

### 8.1 Overview

The CCM2.0 application integrates with Gmail API to automatically monitor and process trade confirmation emails sent to a dedicated mailbox (`confirmaciones_dev@servicios.palace.cl`). This integration enables near real-time processing of email confirmations without manual intervention.

### 8.2 Service Account Configuration

**Service Account:** `gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com`  
**Purpose:** Automated access to Gmail inbox for email processing and sending  
**Authentication Method:** Service account key with domain-wide delegation

#### 8.2.1 Domain-Wide Delegation Setup

To enable the service account to access the Gmail mailbox:

1. **Service Account Configuration:**
   - Created in project `ccm-dev-pool`
   - Domain-wide delegation enabled
   - OAuth scopes: `https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send`

2. **Google Workspace Admin Configuration:**
   - Client ID (Unique ID) authorized in admin.google.com
   - Scopes: `https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send`
   - Allows reading and sending emails as `confirmaciones_dev@servicios.palace.cl`

#### 8.2.2 Organization Policy Exception

Due to the organization policy `constraints/iam.disableServiceAccountKeyCreation` that prevents service account key creation:

1. **Temporary Exception Process:**
   ```bash
   # Temporarily disable the restriction
   gcloud resource-manager org-policies set-policy policy-exception.yaml --organization=165254678508
   
   # Create the service account key
   gcloud iam service-accounts keys create gmail-service-account.json \
     --iam-account=gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com
   
   # Re-enable the restriction
   gcloud resource-manager org-policies set-policy policy-reenable.yaml --organization=165254678508
   ```

2. **Key Storage:**
   - Key file: `backend/gmail-service-account.json`
   - Not committed to version control (in .gitignore)
   - Required for Gmail API authentication only

### 8.3 Authentication Architecture

The application uses a dual authentication approach:

1. **Firestore Access:** Uses Application Default Credentials (ADC)
   - Leverages user's Google Cloud credentials
   - No service account keys required
   - Access to CMEK-encrypted `ccm-development` database

2. **Gmail API Access:** Uses service account key with domain-wide delegation
   - Required due to Gmail's specific authentication requirements
   - Enables programmatic access to monitored mailbox
   - Processes emails without user intervention

### 8.4 Email Processing Workflow

1. **Email Detection:**
   - Service monitors `confirmaciones_dev@servicios.palace.cl` inbox
   - Uses Gmail History API for efficient new message detection
   - Processes emails where monitoring address is in To/CC fields

2. **Processing Pipeline:**
   - Extract email metadata (sender, subject, date, body)
   - Download PDF attachments
   - Process PDFs through existing EmailParserService
   - Send to LLM (Claude) for trade data extraction
   - Store processed data in Firestore
   - Trigger automatic matching with existing trades

3. **API Endpoints:**
   - `POST /api/v1/gmail/check-now` - Manual email check
   - `POST /api/v1/gmail/start-monitoring` - Start background monitoring
   - `POST /api/v1/gmail/stop-monitoring` - Stop monitoring
   - `GET /api/v1/gmail/status` - Check service status
   - `POST /api/v1/gmail/initialize` - Initialize service

### 8.5 Automated Email Sending Capability

**Added:** August 2025 - Support for sending confirmation and dispute emails

1. **Sending Functionality:**
   - Service can send emails from `confirmaciones_dev@servicios.palace.cl`
   - Supports plain text and multipart messages with proper headers
   - Includes reply-to configuration and CC support
   - Full error handling and logging for sent emails

2. **Use Cases:**
   - Automated confirmation emails for matched trades
   - Automated dispute notifications with field-specific discrepancies
   - System-generated notifications based on client configuration

3. **Implementation Details:**
   - Uses same service account authentication as monitoring
   - Gmail API `users().messages().send()` method
   - Base64-encoded MIME message format
   - Integrated with existing `gmail_service.py` module

### 8.6 Security Considerations

1. **Principle of Least Privilege:**
   - Service account has read and send access to Gmail (minimal required scopes)
   - Limited to specific mailbox via domain-wide delegation
   - Cannot modify or delete existing emails
   - Can only send emails from the designated service address

2. **Key Management:**
   - Service account key stored locally only
   - Not in version control
   - Organization policy prevents unauthorized key creation

3. **Audit Trail:**
   - All API access logged in Cloud Audit Logs
   - Email processing tracked in application logs
   - Failed processing attempts recorded for investigation

### 8.6 Production Deployment Considerations

For production deployment:

1. **Dedicated Service Account:** Create production-specific service account in production project
2. **Production Mailbox:** Use `confirmaciones@servicios.palace.cl` instead of development mailbox
3. **Key Rotation:** Implement regular key rotation schedule
4. **Monitoring:** Set up alerts for processing failures and API quota usage

### 8.7 Recent Improvements (August 2025)

**Enhanced Email Processing Pipeline:**

1. **Improved Trade Matching Integration:**
   - Automated emails now triggered directly from trade matching results
   - Support for both "Confirmation OK" and "Difference" status handling
   - Automatic email queuing using Cloud Tasks for reliable delivery

2. **Field Discrepancy Reporting:**
   - Detailed reporting of specific field differences in dispute emails
   - Multi-language support (Spanish, Portuguese, English) for email content
   - Structured discrepancy data showing both email and client values

3. **Email Address Validation:**
   - Robust validation to ensure only valid email addresses are used for automated sending
   - Graceful handling of MSG files that contain only display names
   - Error logging for invalid email addresses with appropriate fallback behavior

4. **System Reliability Improvements:**
   - Removed overly aggressive email address guessing logic
   - Clean error handling for cases where sender email cannot be determined
   - Streamlined debugging and logging for production environments

---

## 9.0 Google Cloud Tasks Integration

### 9.1 Overview

**Added:** August 2025 - Asynchronous task processing for automated email operations

Google Cloud Tasks provides a reliable, scalable queue service that enables the CCM2.0 application to handle automated email processing asynchronously. This integration ensures that automated email operations don't block the main application flow and can be retried on failure.

### 9.2 Service Configuration

**Service Account:** Uses existing application default credentials (ADC) with minimal required permissions
**Location:** `us-east4` (Northern Virginia) - Cloud Tasks doesn't support `southamerica-west1`
**Authentication:** No additional service account keys required - leverages existing ADC setup

### 9.3 Task Queue Architecture

The application implements multiple task queues for different types of operations:

1. **General Queue** (`general-queue`):
   - Default queue for general background tasks
   - Standard processing rate and retry policies

2. **Email Queue** (`email-queue`):
   - Dedicated queue for automated email processing
   - Optimized for email delivery operations

3. **Priority Queue** (`priority-queue`):
   - High-priority queue for time-sensitive operations
   - Faster processing with higher resource allocation

### 9.4 Email Automation Integration

**Automated Email Types Supported:**
- **Confirmation Emails:** Sent when trades are successfully matched
- **Dispute Emails:** Sent when discrepancies are found between email trades and client records

**Task Processing Flow:**
1. Main application processes email confirmations and matches trades
2. Based on match results, creates appropriate Cloud Tasks for email automation
3. Tasks are queued with delay (configurable, default: immediate processing)
4. Worker processes execute tasks asynchronously
5. Failed tasks are automatically retried according to queue configuration

### 9.5 Implementation Details

**Task Creation:**
- Tasks are created with unique identifiers to prevent duplication
- Payload includes all necessary data for email generation (trade data, client info, match results)
- Task routing based on operation type (confirmation vs. dispute)

**Error Handling:**
- Comprehensive error logging for failed tasks
- Automatic retry with exponential backoff
- Dead letter queue handling for permanently failed tasks
- Detailed error messages for debugging

**Performance Benefits:**
- Non-blocking email processing
- Improved application responsiveness
- Scalable processing of high email volumes
- Resilient handling of temporary Gmail API failures

### 9.6 Required GCP APIs

The following Google Cloud APIs must be enabled for Cloud Tasks integration:

```bash
# Enable Cloud Tasks API
gcloud services enable cloudtasks.googleapis.com --project=ccm-dev-pool

# Verify API is enabled
gcloud services list --enabled --project=ccm-dev-pool | grep cloudtasks
```

### 9.7 IAM Permissions

The application service account requires the following Cloud Tasks permissions:

- `roles/cloudtasks.enqueuer` - Create and submit tasks to queues
- `roles/cloudtasks.viewer` - View queue status and task details (for monitoring)

### 9.8 Monitoring and Observability

**Queue Monitoring:**
- Cloud Tasks provides built-in metrics for queue depth, processing rates, and error rates
- Integration with existing central logging and monitoring infrastructure
- Custom application logs for task execution tracking

**Alert Configuration:**
- Recommended alerts for queue depth exceeding thresholds
- Error rate monitoring for failed task detection
- Integration with existing SCC monitoring setup

### 9.9 Production Deployment Considerations

For production deployment:

1. **Queue Configuration:** Review and adjust queue processing rates based on expected email volume
2. **Regional Deployment:** Use `us-east4` region for queues (Cloud Tasks limitation - doesn't support `southamerica-west1`)
3. **Monitoring Setup:** Configure production alerts and monitoring dashboards
4. **Error Handling:** Implement dead letter queue processing for manual intervention on critical failures

---

## 10.0 Production Architecture Alignment (October 2025)

### 10.1 Load Balancer and Cloud Armor Configuration

**Required for Production:** IP whitelisting for enterprise clients requires Global Load Balancer

#### 10.1.1 Global Load Balancer Setup

**Configuration:**
```yaml
Load Balancer:
  Name: ccm-api-lb
  Type: HTTPS Load Balancer (Global)
  Project: prod1-svc-5q4z
  Frontend:
    IP: Static reserved IP
    Port: 443
    Certificate: Google-managed SSL for api.servicios.palace.cl
  Backend:
    Service: Cloud Run (ccm-backend-prod)
    Region: southamerica-west1
  Cost: $25/month + $3/month for static IP
```

**Cloud Armor Policy:**
```yaml
Policy Name: ccm-ip-whitelist
Default Rule: Deny all (403 Forbidden)
Client Rules:
  - Priority 100-199: Client office IP ranges
  - Priority 999: Palace office IPs for admin access
Attached to: Load Balancer backend service
```

#### 10.1.2 Domain Configuration

**Production URLs:**
- Frontend: `app.servicios.palace.cl` → Firebase Hosting
- Backend API: `api.servicios.palace.cl` → Load Balancer → Cloud Run

**Development URLs:**
- Frontend: `dev.servicios.palace.cl` → Firebase Hosting (dev)
- Backend API: Direct Cloud Run URL (no Load Balancer needed)

### 10.2 Multi-Environment Deployment Strategy

#### 10.2.1 Environment Mapping

| Environment | GCP Project | Purpose | Load Balancer |
|------------|------------|---------|---------------|
| Local | ccm-dev-pool (remote DB) | Development with emulators | No |
| Development | ccm-dev-pool | Integration testing | No |
| Staging | nonprod1-svc-5q4z | Pre-production testing | Optional |
| Production | prod1-svc-5q4z | Live environment | Yes (Required) |

#### 10.2.2 Cloud Run Configuration per Environment

**Development (ccm-dev-pool):**
```yaml
Service: ccm-backend-dev
Region: southamerica-west1
Configuration:
  CPU: 1
  Memory: 2Gi
  Min Instances: 0 (scale to zero)
  Max Instances: 5
  Timeout: 60s
VPC Connector: Not required (public access for development)
```

**Staging (nonprod1-svc-5q4z):**
```yaml
Service: ccm-backend-staging
Region: southamerica-west1
Configuration:
  CPU: 1
  Memory: 2Gi
  Min Instances: 0
  Max Instances: 10
  Timeout: 60s
VPC Connector: vpc-connector-nonprod (optional)
```

**Production (prod1-svc-5q4z):**
```yaml
Service: ccm-backend-prod
Region: southamerica-west1
Configuration:
  CPU: 1
  Memory: 2Gi
  Min Instances: 0 (with Cloud Scheduler warm-up)
  Max Instances: 10
  Timeout: 60s
VPC Connector: vpc-connector-prod
Cloud Scheduler: Warm-up every 10 min during business hours
```

#### 10.2.3 Firestore Databases per Environment

| Environment | Project | Database Name | CMEK Key |
|------------|---------|---------------|----------|
| Local | N/A | Emulator | N/A |
| Development | ccm-dev-pool | ccm-development | kms-proj-nqs0vivc9gcm/firestore-key |
| Staging | nonprod1-svc-5q4z | ccm-staging | kms-proj-3zwv12e1sndn/firestore-key |
| Production | prod1-svc-5q4z | ccm-production | kms-proj-g5c6fwjtocz9/firestore-key |

### 10.3 Local Development Setup

#### 10.3.1 Firebase Emulators Configuration

**firebase.json:**
```json
{
  "emulators": {
    "firestore": {
      "port": 8080,
      "host": "localhost"
    },
    "auth": {
      "port": 9099,
      "host": "localhost"
    },
    "pubsub": {
      "port": 8085,
      "host": "localhost"
    }
  }
}
```

#### 10.3.2 Local Development Workflow

```bash
# Terminal 1: Start Firebase emulators
firebase emulators:start

# Terminal 2: Start backend (FastAPI)
cd backend
export FIRESTORE_EMULATOR_HOST=localhost:8080
export PUBSUB_EMULATOR_HOST=localhost:8085
uvicorn src.main:app --reload --port 8000

# Terminal 3: Start frontend (React)
cd frontend
npm start  # Runs on port 3000
```

**Environment Variables (.env.local):**
```bash
# Backend
FIRESTORE_EMULATOR_HOST=localhost:8080
PUBSUB_EMULATOR_HOST=localhost:8085
PROJECT_ID=ccm-dev-pool
ENVIRONMENT=local

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_USE_EMULATOR=true
```

### 10.4 Pub/Sub Configuration for Gmail Push Notifications

**Replaces 30-second polling with instant push notifications**

#### 10.4.1 Topic and Subscription Setup

**Per Environment:**
```yaml
Development:
  Topic: projects/ccm-dev-pool/topics/gmail-notifications-dev
  Subscription: gmail-processor-dev
  Push Endpoint: https://ccm-backend-dev-*.run.app/api/v1/gmail/webhook

Staging:
  Topic: projects/nonprod1-svc-5q4z/topics/gmail-notifications-staging
  Subscription: gmail-processor-staging
  Push Endpoint: https://ccm-backend-staging-*.run.app/api/v1/gmail/webhook

Production:
  Topic: projects/prod1-svc-5q4z/topics/gmail-notifications-prod
  Subscription: gmail-processor-prod
  Push Endpoint: https://api.servicios.palace.cl/api/v1/gmail/webhook
```

### 10.5 Vertex AI Configuration

**LLM Processing (Not available in southamerica-west1):**

```yaml
Platform: Google Vertex AI
Region: us-east4 (required)
Project: Use same as environment (e.g., prod1-svc-5q4z for production)
Models:
  Primary: Claude Sonnet 4.5 (via Model Garden)
  Fallback: Gemini 2.5 Pro
Authentication: Service Account (no API keys needed)
```

### 10.6 Automatic Trade File Synchronization

**New Feature:** Client file source integration

```yaml
Supported Sources:
  - Google Cloud Storage (preferred - Workload Identity)
  - AWS S3 (IAM role or access keys)
  - Azure Blob Storage (SAS tokens)
  - SFTP (legacy support)

Sync Configuration:
  Frequency: Every 10 minutes (configurable)
  Trigger: Cloud Scheduler → Cloud Run
  Storage: Credentials in Secret Manager
  Processing: Cloud Tasks queue
```

### 10.7 Cost Optimization Strategy

#### 10.7.1 Per Environment Costs

| Environment | Monthly Cost | Key Components |
|------------|-------------|----------------|
| Local | $0 | All emulated |
| Development | ~$30 | Cloud Run, Firestore, minimal usage |
| Staging | ~$50 | Similar to dev, more testing |
| Production | ~$115 | Includes Load Balancer, higher usage |

#### 10.7.2 Cost Saving Measures

1. **Scale to Zero:** All environments use min instances = 0
2. **Cloud Scheduler:** Warm-up only during business hours
3. **Regional Resources:** Use southamerica-west1 where possible
4. **Shared VPC:** Leverage existing network infrastructure
5. **CMEK Reuse:** Use existing KMS infrastructure

## 11.0 Deployment & Ongoing Management

### 11.1 Terraform Deployment

* The entire foundation described in this document was deployed from a single, unified Terraform configuration that was generated and downloaded from the Google Cloud Foundation Setup guide.

### 11.2 Terraform State Management

* During the download process, a Google Cloud Storage (GCS) bucket was created in the `southamerica-west1` region. This bucket is configured as the remote backend for the Terraform project, providing a secure and reliable location to store the Terraform state file.

### 11.3 Future Management Strategy

* All future changes to the foundational infrastructure should be managed through the Terraform code. The standard workflow is as follows:
    1.  **Edit Code:** Modify the `.tf` files to reflect the desired change.
    2.  **Version Control:** Commit the changes to the Git repository.
    3.  **Plan:** Run `terraform plan` to review the exact changes that will be made.
    4.  **Apply:** Run `terraform apply` to implement the changes.
* This IaC-first approach prevents configuration drift, provides a full audit trail of changes, and ensures that the infrastructure remains consistent and well-documented over time. Manual changes via the GCP Console should be avoided for foundational resources.

### 11.4 Development Environment Management

* **Development Database:** The `ccm-development` Firestore database was created manually following Google Cloud security best practices for CMEK implementation.
* **Gmail Integration:** Service account and authentication configured manually due to organization policy restrictions.
* **Future Development Projects:** Additional development projects should follow the same CMEK-enabled pattern using existing KMS infrastructure.
* **Production Deployment:** When deploying to production, the same security configuration pattern should be replicated in the Production folder projects (`prod1-service`, `prod2-service`) using their respective KMS keys.