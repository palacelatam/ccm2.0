# Gmail API Setup - Using Application Default Credentials (ADC)

This guide sets up Gmail API using ADC (same as Firebase in this app). **No key files needed!**

## Step 1: Enable Gmail API ✅ (Probably Done)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project: `ccm-dev-pool`
3. APIs & Services → Library
4. Search "Gmail API" → Enable

## Step 2: Create Service Account

**You're at Step 2.4 - Here's what to do:**

1. **Skip the "Grant this service account access" page** - Don't add any roles, just click "Continue"
2. **Skip the "Grant users access" page** - Click "Done"
3. **Important**: Note down the service account email (like `gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com`)

**DO NOT download any JSON key** - We're using ADC instead!

## Step 3: Enable Domain-Wide Delegation

1. Go to APIs & Services → Credentials
2. Click on your new service account email
3. In the service account details page:
   - **Copy the "Unique ID"** (a long number) - you need this for Step 4
   - Scroll down and check ✅ **"Enable Google Workspace Domain-wide Delegation"**
   - Click "Save"

## Step 4: Configure in Google Workspace Admin

1. Go to [admin.google.com](https://admin.google.com)
2. Security → Access and data control → API controls
3. Under "Domain-wide delegation", click "Manage Domain Wide Delegation"
4. Click "Add new"
5. Enter:
   - **Client ID**: The Unique ID from Step 3
   - **OAuth scopes**: `https://www.googleapis.com/auth/gmail.readonly`
6. Click "Authorize"

**Security Note**: The app code hardcodes `confirmaciones_dev@servicios.palace.cl`, so it can only access that one inbox.

## Step 5: Give Yourself Permission to Impersonate

Run this command to allow your user account to impersonate the service account:

```bash
gcloud iam service-accounts add-iam-policy-binding \
  gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com \
  --member="user:YOUR_EMAIL@palace.cl" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project=ccm-dev-pool
```

Replace:
- `gmail-email-processor` with your actual service account name
- `YOUR_EMAIL@palace.cl` with your Google account email

## Step 6: Set Up Local Development

1. Make sure gcloud is installed
2. Login to your Google account:
   ```bash
   gcloud auth login
   ```

3. Set your project:
   ```bash
   gcloud config set project ccm-dev-pool
   ```

4. Configure ADC to impersonate the service account:
   ```bash
   gcloud auth application-default login \
     --impersonate-service-account=gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com
   ```

This creates local credentials that will be used automatically by the app.

## Step 7: Test It

```bash
cd backend
python test_gmail_service.py
```

The app will automatically use ADC - no configuration needed!

## How It Works

```
Your Computer → Your Google Account → Impersonates Service Account → Accesses Gmail
                    (gcloud auth)           (ADC magic)              (as confirmaciones_dev)
```

In production (Cloud Run):
```
Cloud Run → Service Account → Accesses Gmail
         (attached to service)  (as confirmaciones_dev)
```

## Common Issues & Fixes

### "Unable to impersonate service account"
You missed Step 5. Run the `gcloud iam` command to grant yourself permission.

### "Delegation denied for confirmaciones_dev@servicios.palace.cl"
- Check Step 3: Domain-wide delegation must be enabled
- Check Step 4: Client ID must be added in admin.google.com

### "Application Default Credentials not found"
Run Step 6.4 again - the `gcloud auth application-default login` command.

### Gmail account doesn't exist
Make sure `confirmaciones_dev@servicios.palace.cl` is a real Gmail/Google Workspace account.

## Why This is Better Than Key Files

✅ **No key file to steal** - Uses your Google identity locally  
✅ **Automatic in Cloud Run** - Just attach the service account  
✅ **Respects org policy** - No need to disable security rules  
✅ **Same as Firebase** - Consistent auth throughout your app  

## For Production

When deploying to Cloud Run:
1. In Cloud Run settings, set Service Account to `gmail-email-processor@ccm-dev-pool.iam.gserviceaccount.com`
2. The code automatically uses it - no changes needed
3. For production email, change `confirmaciones_dev@servicios.palace.cl` to `confirmaciones@servicios.palace.cl` in the code