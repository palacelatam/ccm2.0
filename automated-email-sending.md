# Automated Email Sending Implementation Plan

## Overview

This document outlines the implementation approach for automated email sending functionality in the Client Confirmation Manager 2.0 application. The system will automatically send confirmation or dispute emails from the central application email (`confirmaciones_dev@servicios.palace.cl`) to banks based on admin-configured settings and time delays.

## Business Requirements (from business-specs.md)

### Auto-Confirmation Settings (Admin Configurable)
1. **Matched Trades**:
   - Toggle: Turn On/Off autoconfirm on matched trades
   - Delay: Configurable time to wait before sending confirmation email (e.g., 30 seconds)
   - Action: Send confirmation email to bank indicating trade is confirmed

2. **Disputed Trades**:
   - Toggle: Turn On/Off autoconfirm on disputed trades  
   - Delay: Configurable time to wait before sending dispute email (e.g., 60 seconds)
   - Action: Send dispute email to bank highlighting specific field discrepancies

### Email Content
- **Confirmation Email**: Uses existing mailback functionality when no discrepancies found
- **Dispute Email**: Uses existing mailback functionality with specific differing fields highlighted
- **From Address**: `confirmaciones_dev@servicios.palace.cl` (central application email)
- **To Address**: Bank's confirmation email address (extracted from original email sender)
- **Language**: Uses client's configured language (Spanish/English/Portuguese) with i18next templates

## Current System Infrastructure

### Already Available
1. **Gmail Service** (`backend/src/services/gmail_service.py`):
   - ✅ Gmail API authentication with service account
   - ✅ Email receiving and processing capabilities
   - ✅ Central email address configured: `confirmaciones_dev@servicios.palace.cl`

2. **Mailback Content Generation**:
   - ✅ Existing mailback function in ConfirmationsGrid.tsx
   - ✅ i18next templates for multilingual emails
   - ✅ Discrepancy detection using differingFields from matched trades

3. **Admin Configuration System** (FULLY IMPLEMENTED):
   - ✅ AdminDashboard.tsx with complete auto-email configuration UI
   - ✅ Toggle switches for autoConfirmMatched and autoConfirmDisputed
   - ✅ Delay input fields (in minutes) for both matched and disputed trades
   - ✅ Backend API integration via clientService.getClientSettings() and updateClientSettings()
   - ✅ Configuration storage in Firestore at `/clients/{client_id}/settings/configuration`
   - ✅ AutomationSettings interface with proper TypeScript types
   - ✅ Unsaved changes tracking and save/reset functionality

### Needs Extension
1. **Gmail Service**: Add sending capability (currently read-only)
2. **Task Queue System**: For delayed email processing

## Technical Implementation Approach

### 1. Gmail API Enhancement

**Send Permissions Added** ✅:
- ✅ Extended Gmail API scopes to include `https://www.googleapis.com/auth/gmail.send`
- ✅ Added `send_email()` method to existing `GmailService` class
- ✅ Updated domain-wide delegation in Google Workspace Admin Console
- ✅ Uses same service account authentication with enhanced permissions

**New Method**:
```python
class GmailService:
    async def send_confirmation_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        cc_email: str = None
    ) -> bool:
        # Implementation to send email via Gmail API
```

### 2. Task Queue System - Google Cloud Tasks

**Why Cloud Tasks**:
- ✅ Persistent across server restarts
- ✅ Scales with multiple Cloud Run instances  
- ✅ Built-in retry logic for failed sends
- ✅ Fully managed by Google (zero maintenance)
- ✅ Cost-effective for expected volume
- ✅ Perfect for delayed task execution

**Architecture**:
```python
class AutoEmailService:
    async def schedule_confirmation_email(
        self,
        client_id: str,
        email_data: dict, 
        delay_seconds: int
    ):
        # Create Cloud Task scheduled for future execution
        # Task will call internal API endpoint after delay
```

**Task Execution Flow**:
1. Trade processed → Status determined (matched/disputed)
2. Check client's auto-email settings
3. If enabled → Create Cloud Task with configured delay
4. After delay → Cloud Tasks calls internal endpoint
5. Internal endpoint → Sends email via Gmail API

### 3. Database Configuration Structure (ALREADY EXISTS)

**Location**: `/clients/{client_id}/settings/configuration`

**Existing Schema** (from AdminDashboard.tsx):
```typescript
interface AutomationSettings {
  dataSharing: boolean;
  autoConfirmMatched: {
    enabled: boolean;
    delayMinutes: number;  // Admin configures in minutes
  };
  autoConfirmDisputed: {
    enabled: boolean;
    delayMinutes: number;  // Admin configures in minutes  
  };
  autoCartaInstruccion: boolean;
}
```

**Usage in Implementation**:
- Read existing `automationSettings` from client configuration
- Convert `delayMinutes` to seconds for Cloud Tasks: `delayMinutes * 60`

### 4. Integration Points

**When Trade is Processed**:
- In existing trade matching/processing logic
- After status determination (matched/disputed/unrecognized)
- Check client auto-email settings
- Schedule appropriate email if configured

**Email Content Generation**:
- Reuse existing mailback generation logic
- Same i18next templates and language detection
- Same discrepancy field highlighting for dispute emails

**Admin Configuration (ALREADY COMPLETE)**:
- ✅ AdminDashboard.tsx already has all required toggles and delay input fields
- ✅ Configuration already saved to Firestore via existing clientService API
- ✅ No changes needed to admin interface

## Implementation Steps

### Phase 1: Gmail API Extension ✅ COMPLETED
1. ✅ Updated Gmail service scopes to include send permissions
2. ✅ Added `send_email()` method to GmailService  
3. ✅ Updated domain-wide delegation in Google Workspace Admin Console
4. ✅ Successfully tested email sending capability

### Phase 2: Cloud Tasks Setup  
1. Set up Cloud Tasks queue in GCP project
2. Create AutoEmailService class
3. Add internal API endpoint for task execution
4. Test delayed task scheduling and execution

### Phase 3: Integration
1. Integrate auto-email scheduling into trade processing workflow
2. Connect email content generation with Cloud Tasks execution  
3. Read existing client configuration using clientService.getClientSettings()
4. Convert delayMinutes to seconds for Cloud Tasks scheduling
5. Add logging and monitoring for sent emails

### Phase 4: Testing & Validation
1. Test end-to-end workflow with different client configurations
2. Validate email delivery and content accuracy
3. Test failure scenarios and retry logic
4. Performance testing with multiple concurrent clients

## Scalability Considerations

**For Hundreds-Thousands of Clients**:
- ✅ Cloud Tasks handles distributed task execution
- ✅ Multiple Cloud Run instances process tasks independently  
- ✅ Firestore scales automatically for configuration storage
- ✅ Gmail API has sufficient rate limits for expected volume
- ✅ Pay-per-task pricing model is cost-effective

**Expected Volume**:
- Not massive email volume (trades are discrete events)
- Multiple users but reasonable email frequency
- Cloud Tasks perfect for this "medium-scale, reliable delivery" use case

## Risk Mitigation

**Email Delivery Failures**:
- Cloud Tasks built-in retry logic
- Failed task monitoring and alerts
- Audit log of all email attempts

**Configuration Changes**:
- Admin can disable auto-emails instantly
- Pending tasks for disabled features still execute (configurable)
- Clear admin UI feedback on current settings

**System Reliability**:
- Persistent task storage (survives server restarts)
- No memory-based timers (eliminates single points of failure)
- Monitoring and alerting for task queue health

## Future Enhancements

**Phase 2 Features** (not in initial scope):
- Email templates customization per client
- Advanced scheduling rules (business hours only, etc.)
- Email delivery status tracking and reporting
- Integration with SMS notifications (mentioned in business-specs.md)
- Bulk email operations for multiple trades

---

This approach leverages existing infrastructure while adding robust, scalable email automation that aligns with the business requirements and technical architecture of the CCM 2.0 platform.