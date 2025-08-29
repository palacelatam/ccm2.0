# Ngrok Setup and Configuration for CCM2.0 Development

**Document Version:** 1.0  
**Date:** August 29, 2025  
**Author:** Claude Code

## 1.0 Overview

Ngrok provides secure tunneling to localhost, enabling external access to your development environment for client demonstrations and webhook testing. This is essential for showcasing the CCM2.0 application to potential clients without deploying to production infrastructure.

## 2.0 Installation and Setup

### 2.1 Download and Install Ngrok

1. **Download:** Visit [https://ngrok.com/download](https://ngrok.com/download)
2. **Install:** Extract the executable to a convenient location (e.g., `C:\tools\ngrok\`)
3. **Add to PATH:** Add the ngrok directory to your Windows PATH environment variable
4. **Verify Installation:**
   ```cmd
   ngrok --version
   ```

### 2.2 Account Setup

1. **Create Account:** Sign up at [https://ngrok.com](https://ngrok.com)
2. **Get Auth Token:** From your ngrok dashboard, copy your authtoken
3. **Configure Auth Token:**
   ```cmd
   ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
   ```

## 3.0 Development Configuration

### 3.1 Backend API Tunnel

For exposing your FastAPI backend running on localhost:

```cmd
# Start tunnel for backend API (default port 8000)
ngrok http 8000 --log=stdout --log-level=info
```

**Configuration Options:**
- `--log=stdout` - Display logs in console
- `--log-level=info` - Set appropriate log level
- `--region=us` - Use US region for better performance (optional)

### 3.2 Frontend Development Tunnel

For exposing your React frontend during development:

```cmd
# Start tunnel for frontend (typical React dev server port 3000)
ngrok http 3000
```

### 3.3 Multiple Service Tunneling

If you need to expose both frontend and backend simultaneously:

```cmd
# Terminal 1 - Backend tunnel
ngrok http 8000 --log=stdout

# Terminal 2 - Frontend tunnel  
ngrok http 3000 --log=stdout
```

## 4.0 Client Demo Configuration

### 4.1 Recommended Setup for Client Presentations

1. **Start Backend Services:**
   - Ensure Firestore is running (emulator or production)
   - Start FastAPI backend server
   - Verify Gmail API integration is working

2. **Start Frontend:**
   - Run React development server
   - Ensure it connects to backend API

3. **Start Ngrok Tunnels:**
   - Backend tunnel on port 8000
   - Frontend tunnel on port 3000

4. **Update Configuration:**
   - Update frontend API base URL to use ngrok backend tunnel
   - Test all functionality before client demo

### 4.2 Demo Environment Checklist

- [ ] Backend server running on localhost:8000
- [ ] Frontend server running on localhost:3000
- [ ] Ngrok tunnel for backend active
- [ ] Ngrok tunnel for frontend active
- [ ] Gmail API credentials configured
- [ ] Firestore database accessible
- [ ] Test data loaded and accessible
- [ ] All major features tested through tunnels

## 5.0 Configuration Management

### 5.1 Environment Variables

Create environment variables for easy tunnel URL management:

```cmd
# Set in your development environment
set NGROK_BACKEND_URL=https://abc123.ngrok.io
set NGROK_FRONTEND_URL=https://def456.ngrok.io
```

### 5.2 Frontend API Configuration

Update your frontend configuration to use ngrok URLs during demos:

```javascript
// In your React app configuration
const API_BASE_URL = process.env.NODE_ENV === 'demo' 
  ? process.env.REACT_APP_NGROK_BACKEND_URL 
  : 'http://localhost:8000';
```

## 6.0 Security Considerations

### 6.1 Demo Security

- **Temporary Use Only:** Ngrok tunnels are for development and demos only
- **Auth Token Security:** Keep your ngrok auth token secure and private
- **Data Protection:** Use test data only during client demonstrations
- **Session Management:** Close tunnels immediately after demonstrations

### 6.2 Firewall and Network

- **Local Firewall:** Ensure Windows Firewall allows ngrok connections
- **Corporate Networks:** May require additional configuration or approval
- **HTTPS Tunnels:** Ngrok provides HTTPS by default for secure demonstrations

## 7.0 Common Commands and Usage

### 7.1 Essential Ngrok Commands

```cmd
# Basic HTTP tunnel
ngrok http 8000

# HTTP tunnel with custom subdomain (paid plans)
ngrok http 8000 --subdomain=ccm-demo

# HTTP tunnel with authentication
ngrok http 8000 --basic-auth="demo:password"

# Check active tunnels
ngrok status

# Stop all tunnels
ngrok kill

# View tunnel information
ngrok api tunnels list
```

### 7.2 Inspection and Debugging

Ngrok provides a web interface for inspecting requests:

- **Local Interface:** http://localhost:4040
- **View Requests:** See all HTTP requests/responses
- **Replay Requests:** Useful for debugging
- **Request History:** Track client interactions during demos

## 8.0 Troubleshooting

### 8.1 Common Issues

**Connection Refused:**
- Verify backend/frontend servers are running
- Check correct port numbers
- Ensure no firewall blocking

**Auth Token Issues:**
- Re-run `ngrok config add-authtoken`
- Verify token is correct from dashboard
- Check ngrok account status

**Slow Performance:**
- Try different ngrok regions
- Check network connectivity
- Consider paid plan for better performance

### 8.2 Startup Validation

The startup script will check for:
- Ngrok installation and availability
- Active backend service on expected port
- Active frontend service on expected port
- Prompt user to start ngrok tunnels if needed

## 9.0 Integration with Development Workflow

### 9.1 Automated Startup Process

The enhanced startup script will:
1. Check if ngrok is installed
2. Verify backend and frontend services are running
3. Check if tunnels are already active
4. Provide clear instructions for starting tunnels
5. Display tunnel URLs for easy access

### 9.2 Demo Preparation Workflow

1. **Pre-Demo Setup (5 minutes):**
   - Run enhanced startup script
   - Follow ngrok tunnel prompts
   - Verify all services accessible via tunnels

2. **During Demo:**
   - Use ngrok HTTPS URLs for client access
   - Monitor requests via ngrok web interface (localhost:4040)
   - Keep tunnel terminal windows visible for monitoring

3. **Post-Demo Cleanup:**
   - Close ngrok tunnels
   - Stop development servers
   - Clear any demo-specific test data

## 10.0 Production Considerations

### 10.1 Not for Production Use

- **Development Only:** Ngrok is strictly for development and demos
- **Production Deployment:** Use proper GCP Cloud Run or App Engine deployment
- **Security:** Never use ngrok for production traffic or sensitive data

### 10.2 Transition to Production

When ready for production deployment:
- Use GCP Cloud Run for containerized deployment
- Configure proper DNS and SSL certificates
- Implement production monitoring and logging
- Remove all ngrok dependencies from production code

---

## Appendix: Quick Reference

### Essential URLs During Development
- **Ngrok Web Interface:** http://localhost:4040
- **Backend API (local):** http://localhost:8000
- **Frontend (local):** http://localhost:3000
- **Ngrok Backend Tunnel:** https://[random].ngrok.io (backend)
- **Ngrok Frontend Tunnel:** https://[random].ngrok.io (frontend)

### Key Commands for Client Demos
```cmd
# 1. Start backend tunnel
ngrok http 8000

# 2. Start frontend tunnel (new terminal)
ngrok http 3000

# 3. Check tunnel status
curl -s http://localhost:4040/api/tunnels

# 4. Stop all tunnels
ngrok kill
```