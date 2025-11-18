# Quick Testing Guide

## ✅ Setup Complete!
- **Server**: http://localhost:8000 (running)
- **Docker**: Running
- **Test User**: `testuser` / `testpass123`
- **Admin**: `admin` (password set during creation)

## 🚀 Quick Test Steps

### 1. Open the Application
```
http://localhost:8000
```

### 2. Login as Test User
- Click **Login**
- Username: `testuser`
- Password: `testpass123`

### 3. Browse Courses
- Click on **"Linux Basics"** course
- Click **"Enroll Now"**

### 4. Test Terminal Sandbox (Main Feature)
1. In Learning Center, click **"Start Terminal"**
2. Wait for terminal to connect (may take 10-20 seconds on first run)
3. Type a command: `ls -la` and press Enter
4. Verify output appears in terminal
5. Try completing the challenge:
   - Read the challenge prompt
   - Execute the required command
   - Click **"Submit Answer"**

### 5. Check Dashboard
- Navigate to **Dashboard**
- Verify XP, Progress, and Streak updated
- Check enrolled course appears

### 6. Check Leaderboard
- Click **Leaderboard** in nav
- Verify your rank and XP appear

### 7. Check Achievements
- Click **Achievements**
- Verify achievements earned (after completing challenges)

## 🐛 Troubleshooting

### If terminal doesn't start:
```bash
# Check Docker
docker ps

# Pull Ubuntu image if needed
docker pull ubuntu:22.04

# Check server logs
tail -f /tmp/django_server.log
```

### If server stops:
```bash
cd /Users/bnmd3x/cursor_codequest/codequest
python manage.py runserver 8000
```

### Check admin panel:
```
http://localhost:8000/admin/
Username: admin
Password: (your admin password)
```

## 📝 What to Test

1. ✅ **Registration/Login** - Create new account or login
2. ✅ **Course Enrollment** - Enroll in "Linux Basics" course
3. ✅ **Terminal Sandbox** - Start terminal and execute commands
4. ✅ **Challenge Completion** - Complete a challenge and see XP/streak update
5. ✅ **Achievements** - Earn achievements after milestones
6. ✅ **Leaderboard** - See rankings by XP
7. ✅ **IRT Recommendations** - Notice next challenge adapts to your skill

## 🎯 Expected Results

After completing first challenge:
- ✅ XP increases (100 XP for first module)
- ✅ Streak = 1 🔥
- ✅ Progress % increases
- ✅ Next challenge appears
- ✅ Achievement may be awarded

## 💡 Tips

- The terminal may take 10-30 seconds to start on first use (Docker image pull)
- Commands execute in isolated Docker containers
- Each session times out after 5 minutes
- Check admin panel to see sandbox sessions: `/admin/sandbox/sandboxsession/`

Happy Testing! 🚀

