# Firebase Emulator Scripts

## 🎯 **Purpose**

These scripts help manage Firebase emulator data persistence for the Client Confirmation Manager development environment.

## 📜 **Available Scripts**

### **`start-emulators.bat`** - Primary Development Script
Starts Firebase emulators with persistent data storage.

**Features:**
- Automatically loads existing demo data
- Shows connection URLs and demo user credentials
- Saves data automatically when emulators stop
- Displays helpful status information

**Important**: Must be run from **Windows Command Prompt** (not Git Bash)

**Usage:**
```cmd
# From project root in Windows Command Prompt
scripts\start-emulators.bat

# Or run the command directly:
firebase emulators:start --import=./demo-data --export-on-exit=./demo-data
```

**Demo Users (Password: demo123):**
- `admin@xyz.cl` - Client Admin
- `usuario@xyz.cl` - Client User  
- `admin@bancoabc.cl` - Bank Admin

### **`export-demo-data.bat`** - Manual Export
Exports current emulator data while emulators are running.

**Usage:**
```bash
# With emulators running
scripts\export-demo-data.bat
```

### **`backup-demo-data.bat`** - Create Backups
Creates timestamped backups of current demo data.

**Usage:**
```bash
scripts\backup-demo-data.bat
```

**Output:** `backups\demo-data-YYYY-MM-DD_HH-MM-SS\`

### **`reset-demo-data.bat`** - Reset to Fresh State
Deletes current demo data after creating a backup.

**Usage:**
```bash
scripts\reset-demo-data.bat
```

**Warning:** This will delete all current demo users and Firestore data.

## 📁 **Data Storage Structure**

```
demo-data/
├── auth_export/
│   ├── accounts.json          # Demo users with credentials
│   └── config.json           # Auth emulator configuration
├── firestore_export/         # Firestore documents and collections
└── firebase-export-metadata.json  # Export metadata
```

## 🔄 **Development Workflow**

### **Daily Development:**
1. **Open Windows Command Prompt** (not Git Bash)
2. **Navigate to project**: `cd C:\Users\bencl\Proyectos\ccm2.0`
3. **Run**: `firebase emulators:start --import=./demo-data --export-on-exit=./demo-data`
4. Develop and test with consistent demo data
5. Stop emulators (Ctrl+C) - data auto-saves

### **After Adding New Demo Data:**
1. Create new users/data in emulator UI
2. Stop emulators - data auto-saves
3. Optionally run `scripts\backup-demo-data.bat` for safety

### **Sharing with Team:**
1. Commit `demo-data/` directory to Git
2. Team members get same demo environment
3. Use `scripts\backup-demo-data.bat` before major changes

### **Clean Start:**
1. Run `scripts\reset-demo-data.bat`
2. Creates backup before reset
3. Next emulator start will be fresh

## 🚀 **Production Migration**

When migrating to production Firestore:

1. **Reference demo data structure:**
   ```json
   // demo-data/auth_export/accounts.json
   {
     "users": [
       {
         "email": "admin@xyz.cl",
         "displayName": "XYZ Admin",
         // ... other properties
       }
     ]
   }
   ```

2. **Create production users** with real passwords
3. **Recreate Firestore documents** based on emulator data
4. **Maintain role assignments** from demo environment

## 🔐 **Security Notes**

- **Demo passwords are `demo123`** - change for production
- **Emulator data is local only** - not connected to production
- **Backup files contain user data** - handle appropriately
- **Consider .gitignore** for sensitive demo scenarios

## 🧪 **Testing Scenarios**

**Saved Demo Users:**
- **Bank Admin Flow**: Login as `admin@bancoabc.cl`
- **Client Admin Flow**: Login as `admin@xyz.cl` 
- **Client User Flow**: Login as `usuario@xyz.cl`

**Adding Test Data:**
1. Use Firestore Emulator UI: http://127.0.0.1:4000/firestore
2. Create collections matching `data-structure.md`
3. Data persists automatically

## 🔍 **Troubleshooting**

**Scripts won't run:**
- **Use Windows Command Prompt** (not Git Bash or PowerShell)
- Ensure you're in project root directory
- Check that Firebase CLI is installed and in PATH
- Verify Java is installed and accessible from Command Prompt

**Demo data not loading:**
- Verify `demo-data/auth_export/accounts.json` exists
- Check file permissions
- Try `scripts\reset-demo-data.bat` and start fresh

**Emulators won't start:**
- Check ports 4000, 8080, 9099 are available
- Ensure Java 11+ is installed
- Close any running emulator instances

**Data not saving:**
- Use `scripts\export-demo-data.bat` for manual export
- Check disk space availability
- Verify write permissions in project directory