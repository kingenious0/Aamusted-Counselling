# AAMUSTED Counselling System - Quick Reference Card

## 🖥️ Accessing the System

**Open Browser** → Type: `http://localhost:5000`

**Login** with your credentials

## 🔄 Daily Check

**Is the system working?**
1. Open browser → `http://localhost:5000`
2. If login page appears → ✅ System is working
3. If no page loads → Follow emergency steps below

## 🚨 Emergency: System Not Working

### Step 1: Check Status
**Double-click desktop icon** "Check Service Status"

**OR** open Command Prompt and type:
```
cd C:\AAMUSTED_Counselling
python check_service.py
```

### Step 2: If Service is Stopped
**In Command Prompt (as Administrator):**
```
net start AAMUSTEDCounsellingService
```

### Step 3: If Still Not Working
**Contact IT Support**: [Your Contact Info]

**Emergency Restart** (if urgent):
```cmd
net stop AAMUSTEDCounsellingService
wait 10 seconds
net start AAMUSTEDCounsellingService
```

## 📞 Who to Call

**Technical Issues**: [Your Phone Number]  
**Service Down**: [Your Emergency Number]  
**After Hours**: [Your After Hours Contact]

## 💡 Tips

✅ **Service starts automatically** when computer starts  
✅ **No need to manually start** the application  
✅ **Check logs** if problems persist  
✅ **Keep this card handy** for quick reference  

## 🔍 How to Check Logs

**For detailed status:**
```cmd
cd C:\AAMUSTED_Counselling
python service_manager.py
# Select option 6 to view logs
```

---
**Keep this card at your desk for quick reference!**