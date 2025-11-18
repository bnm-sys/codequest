# CodeQuest Testing Guide

## 🚀 Server Status
✅ **Server is running on**: http://localhost:8000  
✅ **Docker is running**  
✅ **Sample data created**: 2 courses, 3 modules, 3 challenges, 2 achievements

## 🔐 Test Credentials

### Admin User
- **Username**: `admin`
- **Password**: (set during superuser creation)
- **Access**: Admin panel at http://localhost:8000/admin/

### Test Student User
- **Username**: `testuser`
- **Password**: `testpass123`
- **Email**: testuser@example.com
- **Role**: Student

## 📋 Complete Testing Flow

### 1. Homepage Testing
1. Open http://localhost:8000 in your browser
2. Verify you see:
   - ✅ Welcome message
   - ✅ List of available courses (Linux Basics, Git Fundamentals)
   - ✅ Navigation menu with Login/Register

### 2. User Registration
1. Click **Register**
2. Fill in the form:
   - Username: `testuser2`
   - Email: `testuser2@example.com` (or phone: +977XXXXXXXXX)
   - Password: (set a password)
3. Submit and verify:
   - ✅ Redirected to dashboard
   - ✅ Success message displayed
   - ✅ Profile automatically created

### 3. User Login
1. If logged out, click **Login**
2. Enter credentials:
   - Username: `testuser`
   - Password: `testpass123`
3. Verify:
   - ✅ Redirected to dashboard
   - ✅ Navigation shows Dashboard, Leaderboard, Achievements

### 4. Dashboard Testing
1. Navigate to Dashboard (or auto-redirected after login)
2. Verify you see:
   - ✅ "Your Courses" section (empty initially)
   - ✅ "Browse Courses" button if no enrollments
   - ✅ Quick stats section (XP: 0, Challenges: 0, Streak: 0)

### 5. Course Enrollment
1. Click **Browse Courses** or go to homepage
2. Click on **"Linux Basics"** course
3. Verify course detail page shows:
   - ✅ Course description
   - ✅ List of modules (File System Navigation, Git Basics)
   - ✅ "Enroll Now" button
4. Click **Enroll Now**
5. Verify:
   - ✅ Success message
   - ✅ Redirected to Learning Center
   - ✅ Course appears in Dashboard

### 6. Learning Center & Terminal Sandbox Testing ⭐
1. In Learning Center, verify you see:
   - ✅ Course progress (0% initially)
   - ✅ XP and Streak counters
   - ✅ Current module and challenge
   - ✅ Challenge prompt
   - ✅ "Start Terminal" button
   - ✅ Terminal container (empty initially)

2. **Start Terminal Sandbox:**
   - Click **"Start Terminal"** button
   - Wait for terminal to initialize (may take a few seconds)
   - Verify:
     - ✅ Terminal displays: "✓ Sandbox session started!"
     - ✅ Terminal status shows "Connected"
     - ✅ Prompt appears: `$`
     - ✅ "Start Terminal" button hidden, "Submit Answer" button appears

3. **Test Command Execution:**
   - Type: `ls -la`
   - Press Enter
   - Verify:
     - ✅ Command executes in Docker container
     - ✅ Output appears in terminal
     - ✅ Prompt returns for next command

4. **Test Challenge Completion:**
   - For "List Directory Contents" challenge:
     - Run: `ls -la`
     - Copy relevant output
   - Click **"Submit Answer"** button
   - Verify:
     - ✅ Feedback appears (Correct/Incorrect)
     - ✅ XP increases if correct
     - ✅ Streak increases
     - ✅ Redirected or message shown

### 7. Challenge Flow Testing
1. Complete a challenge correctly
2. Verify:
   - ✅ Progress percentage increases
   - ✅ XP added to enrollment and profile
   - ✅ Next challenge appears (or course completion message)
   - ✅ Skill mastery updated (if skill tags exist)

3. Try an incorrect answer
4. Verify:
   - ✅ Error message shown
   - ✅ Streak resets to 0
   - ✅ Can retry challenge

### 8. IRT & Adaptive Learning Testing
1. Complete multiple challenges in the same module
2. Verify:
   - ✅ Next challenge recommended based on skill level
   - ✅ Challenge difficulty adapts to user ability
   - ✅ Skill mastery (theta) values updated in database

### 9. Achievements Testing
1. Navigate to **Achievements** page
2. Verify:
   - ✅ Shows earned achievements (if any)
   - ✅ Shows locked achievements
   - ✅ Progress bar for achievement completion

3. Complete challenges to trigger achievements:
   - Complete 1 challenge → "First Steps" achievement
   - Complete 10 challenges → "Challenge Master 10" achievement
   - Earn XP milestones → XP achievements

4. Verify achievements auto-award via signals

### 10. Leaderboard Testing
1. Navigate to **Leaderboard** page
2. Verify:
   - ✅ Shows top users by total XP
   - ✅ Shows user's current rank
   - ✅ Shows user's XP
   - ✅ Shows skill-specific leaderboards (if any)

3. Complete more challenges to increase XP
4. Refresh leaderboard
5. Verify:
   - ✅ Rank updates
   - ✅ XP increases

### 11. Admin Panel Testing
1. Log in as admin (http://localhost:8000/admin/)
2. Explore admin interfaces:
   - ✅ **Accounts → Custom Users**: View/edit users
   - ✅ **Courses**: Manage courses, modules, challenges
   - ✅ **Gamification → Achievements**: Manage achievements
   - ✅ **Gamification → Skill Mastery**: View skill levels
   - ✅ **Sandbox → Sandbox Sessions**: Monitor active sessions
   - ✅ **Courses → Enrollments**: View enrollments

3. Create a new challenge:
   - Go to Courses → Challenges
   - Add Challenge
   - Fill in details:
     - Title: "Test Challenge"
     - Module: (select a module)
     - Prompt: "Run the command: echo 'Hello World'"
     - Expected Output: "Hello World"
     - Difficulty: Easy
   - Save
4. Verify challenge appears in learning center

### 12. Docker Sandbox API Testing (Optional)
You can test the REST API directly using curl:

```bash
# Get CSRF token first (login required)
curl -c cookies.txt -b cookies.txt http://localhost:8000/accounts/login/

# Create sandbox session
curl -X POST http://localhost:8000/sandbox/api/sessions/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -b cookies.txt \
  -d '{"challenge_id": 1}'

# Execute command (replace SESSION_ID)
curl -X POST http://localhost:8000/sandbox/api/sessions/SESSION_ID/execute/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -b cookies.txt \
  -d '{"command": "ls -la"}'
```

## 🐛 Common Issues & Solutions

### Issue: Terminal doesn't start
**Solution**: 
- Check Docker is running: `docker ps`
- Check server logs: `tail -f /tmp/django_server.log`
- Verify Docker image exists: `docker images | grep ubuntu`

### Issue: Command execution fails
**Solution**:
- Check sandbox session is active in admin panel
- Verify container is running: `docker ps`
- Check container logs: `docker logs CONTAINER_ID`

### Issue: Challenge evaluation fails
**Solution**:
- Verify expected_output format matches evaluation logic
- Check output evaluator is comparing correctly
- Test with simpler expected outputs

### Issue: Achievements not awarding
**Solution**:
- Check signals are loaded: Verify `gamification/apps.py` has `ready()` method
- Check achievement criteria in admin panel
- Verify UserChallengeAttempt records are created

## ✅ Test Checklist

- [ ] Homepage loads and displays courses
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard displays correctly
- [ ] Course enrollment works
- [ ] Learning center loads
- [ ] Terminal sandbox starts
- [ ] Commands execute in terminal
- [ ] Challenge submission works
- [ ] XP and streak update correctly
- [ ] Progress percentage calculates correctly
- [ ] Next challenge recommendation works (IRT)
- [ ] Achievements display correctly
- [ ] Leaderboard shows rankings
- [ ] Admin panel accessible
- [ ] Can create/edit courses via admin
- [ ] Skill mastery tracking works
- [ ] Docker containers clean up after timeout

## 🎯 Expected Behavior

### After completing "List Directory Contents" challenge:
- XP increases by 100 (module points)
- Streak increases by 1
- Progress increases
- Next challenge appears
- Skill mastery (ls) theta updates

### After completing module:
- Module marked complete
- Next module unlocks
- Progress percentage increases

### After completing course:
- Course progress = 100%
- Achievement awarded (if configured)
- Course completion message shown

## 📊 Monitoring

### Check Active Sandbox Sessions:
```bash
python manage.py shell
>>> from sandbox.models import SandboxSession
>>> SandboxSession.objects.filter(is_active=True)
```

### Check User Progress:
```bash
>>> from courses.models import Enrollment
>>> Enrollment.objects.all().values('user__username', 'xp', 'progress', 'streak')
```

### Check Skill Mastery:
```bash
>>> from gamification.models import SkillMastery
>>> SkillMastery.objects.all().values('user__username', 'skill_tag', 'theta')
```

## 🔄 Restart Server (if needed)
```bash
# Stop server
kill $(cat /tmp/django_server.pid) 2>/dev/null

# Start server
python manage.py runserver 8000
```

## 🎉 Success Criteria
✅ All pages load without errors  
✅ Terminal sandbox creates and executes commands  
✅ Challenges can be completed and evaluated  
✅ XP, streaks, and progress update correctly  
✅ Achievements auto-award on milestones  
✅ Leaderboard displays rankings  
✅ IRT recommendations work  
✅ Docker containers clean up properly  

Happy Testing! 🚀

