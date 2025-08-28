# Google Cloud Platform: `palace.cl` Organization Architecture & Security Summary

**Document Version:** 1.2  
**Date:** August 14, 2025  
**Author:** Gemini AI Assistant (Updated by Claude Code)

## 1.0 Introduction & Strategic Objectives

This document provides a detailed and comprehensive summary of the foundational setup for the Google Cloud Platform (GCP) Organization `palace.cl`. The primary objective of this foundation is to provide a secure, scalable, and compliant platform for the development and operation of enterprise-level Software-as-a-Service (SaaS) applications, with a specific focus on meeting the stringent requirements of the banking and financial services industry.

The entire foundation was configured using the Google Cloud Foundation Setup guide and was ultimately downloaded as a complete Infrastructure as Code (IaC) project using Terraform. This ensures that the environment is repeatable, version-controllable, and managed according to modern best practices.

The key strategic pillars underpinning this architecture are:
* **Security by Default:** Implementing a strong security posture from the outset, using Google Cloud's recommended best practices for identity, network security, and data encryption.
* **Scalability & Flexibility:** Building a resource hierarchy and network architecture that can support both shared (pooled) and dedicated (siloed) tenancy models to cater to a diverse range of banking clients.
* **Operational Excellence:** Leveraging Infrastructure as Code (IaC) for all foundational components to ensure reliability, prevent configuration drift, and enable automated, auditable changes.
* **Compliance Readiness:** Establishing a framework with centralized logging, organization-wide security policies, and customer-managed encryption keys to simplify the process of meeting financial industry compliance standards.

---

## 2.0 SaaS Tenancy Model Strategy

A core strategic decision made during the planning phase was the approach to client tenancy, a critical consideration for any SaaS business targeting the banking sector. The foundation has been architected to support a flexible, tiered offering that can accommodate the needs of different types of financial institutions.

### 2.1 The Pool Model (Standard Tier)

This is the primary, more scalable offering.
* **Architecture:** A single, robust multi-tenant application is hosted within the production Shared VPC. This application serves many different clients from a shared infrastructure base.
* **Data Isolation:** Data segregation is enforced at the application and database layers. This is achieved through strict code logic and database design (e.g., ensuring every database query is scoped to the authenticated client's `tenant_id`, or using separate schemas per client within a shared database).
* **Target Clients:** This model is suitable for smaller banks, credit unions, and FinTechs who require a secure, enterprise-grade solution but may not have the budget or requirement for fully dedicated infrastructure.
* **Prerequisites for Sale:** To successfully offer this model to financial clients, it is understood that rigorous proof of security is required. This includes obtaining third-party security certifications and audits, such as **SOC 2 Type 2** and **ISO 27001**, which validate the effectiveness of the application-level isolation controls.

### 2.2 The Silo Model (Enterprise Tier)

This is the premium offering, designed for large, risk-averse financial institutions.
* **Architecture:** For each client in this tier, a completely separate and dedicated instance of the application and its underlying infrastructure is deployed. This includes a dedicated VPC, separate service projects, and a dedicated database instance.
* **Data Isolation:** This model provides the maximum possible level of isolation at the network level. A client's data never resides on the same network or database server as another client's.
* **Target Clients:** This model is designed for large, established banks that have stringent regulatory requirements and corporate policies demanding complete infrastructure isolation.
* **Deployment Strategy:** The use of Terraform is critical for this model's viability. The foundational code allows for the automated, repeatable, and error-free deployment of a new, dedicated "silo" for each enterprise client, making this a manageable and scalable premium offering.

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
    * **Host Projects:** `vpc-host-prod` and `vpc-host-nonprod`, located in the `Common` folder.
    * **Service Projects:** `prod1-service`, `prod2-service`, `nonprod1-service`, `nonprod2-service`, located in the `Production` and `Non-Production` folders respectively.
    * **Development Service Project:** `ccm-dev-pool` (CCM2 - Dev Pool), located in the `Development` folder, used for client dashboard development with persistent CMEK-enabled Firestore.
    * **Central Services Project:** `central-logging-monitoring`, located in the `Common` folder.
    * **KMS Autokey Projects:** A dedicated project for managing encryption keys was created in each of the `Production`, `Non-Production`, and `Development` folders.

---

## 5.0 Networking (VPC Configuration)

The network architecture is built on the **Shared VPC** model and is designed for high availability and security.

### 5.1 Production Network: `vpc-prod-shared`

* **Host Project:** `vpc-host-prod`
* **Architecture:** Multi-regional for high availability.
* **Configuration:**
    * **`subnet-prod-1`**:
        * **Region:** `southamerica-west1` (Santiago)
        * **IP Range:** `10.1.1.0/24`
        * **Linked Service Project:** `prod1-service`
    * **`subnet-prod-2`**:
        * **Region:** `us-east4` (N. Virginia)
        * **IP Range:** `10.1.2.0/24`
        * **Linked Service Project:** `prod2-service`
    * **Common Settings:** For both subnets, **VPC Flow Logs** and **Private Google Access** are **On**, while **Cloud NAT** is **Off**. The network includes 3 default firewall rules.

### 5.2 Non-Production Network: `vpc-nonprod-shared`

* **Host Project:** `vpc-host-nonprod`
* **Architecture:** Mirrors the production network to ensure environment parity.
* **Configuration:**
    * **`subnet-non-prod-1`**:
        * **Region:** `southamerica-west1` (Santiago)
        * **IP Range:** `10.2.1.0/24`
        * **Linked Service Project:** `nonprod1-service`
    * **`subnet-non-prod-2`**:
        * **Region:** `us-east4` (N. Virginia)
        * **IP Range:** `10.2.2.0/24`
        * **Linked Service Project:** `nonprod2-service`
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

---

## 9.0 Deployment & Ongoing Management

### 9.1 Terraform Deployment

* The entire foundation described in this document was deployed from a single, unified Terraform configuration that was generated and downloaded from the Google Cloud Foundation Setup guide.

### 9.2 Terraform State Management

* During the download process, a Google Cloud Storage (GCS) bucket was created in the `southamerica-west1` region. This bucket is configured as the remote backend for the Terraform project, providing a secure and reliable location to store the Terraform state file.

### 9.3 Future Management Strategy

* All future changes to the foundational infrastructure should be managed through the Terraform code. The standard workflow is as follows:
    1.  **Edit Code:** Modify the `.tf` files to reflect the desired change.
    2.  **Version Control:** Commit the changes to the Git repository.
    3.  **Plan:** Run `terraform plan` to review the exact changes that will be made.
    4.  **Apply:** Run `terraform apply` to implement the changes.
* This IaC-first approach prevents configuration drift, provides a full audit trail of changes, and ensures that the infrastructure remains consistent and well-documented over time. Manual changes via the GCP Console should be avoided for foundational resources.

### 9.4 Development Environment Management

* **Development Database:** The `ccm-development` Firestore database was created manually following Google Cloud security best practices for CMEK implementation.
* **Gmail Integration:** Service account and authentication configured manually due to organization policy restrictions.
* **Future Development Projects:** Additional development projects should follow the same CMEK-enabled pattern using existing KMS infrastructure.
* **Production Deployment:** When deploying to production, the same security configuration pattern should be replicated in the Production folder projects (`prod1-service`, `prod2-service`) using their respective KMS keys.