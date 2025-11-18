# CodeQuest - Interactive Learning Platform

A gamified learning platform for Linux and Git with adaptive learning powered by Item Response Theory (IRT).

## Features

### 🎯 Core Features
- User authentication with role-based permissions (Student/Instructor/Admin)
- Course management with modules and challenges
- Interactive terminal sandbox using Docker containers
- Adaptive learning engine using IRT (Item Response Theory)
- Gamification system with XP, achievements, and leaderboards

### 🛠️ Technology Stack
- **Backend**: Django 4.2 with Django REST Framework
- **Frontend**: Tailwind CSS with Xterm.js for terminal interface
- **Database**: PostgreSQL (SQLite for development)
- **Sandbox**: Docker containers for isolated execution
- **AI/ML**: NumPy, SciPy, Scikit-learn for IRT implementation

## Quick Start

### Prerequisites
- Python 3.9+
- Docker (for sandbox functionality)
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd codequest
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DOCKER_BASE_URL=unix://var/run/docker.sock
DOCKER_IMAGE=ubuntu:22.04
DOCKER_CONTAINER_TIMEOUT=300
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Project Structure

```
codequest/
├── accounts/              # User authentication & profiles
│   ├── models.py         # CustomUser, Profile models
│   ├── views.py          # Registration, login, dashboard
│   └── urls.py
├── courses/              # Course management
│   ├── models.py         # Course, Module, Challenge, Enrollment
│   ├── views.py          # Course views with IRT integration
│   └── urls.py
├── sandbox/              # Docker sandbox integration
│   ├── models.py         # SandboxSession model
│   ├── docker_service.py # Docker container management
│   ├── evaluator.py      # Output evaluation
│   ├── views.py          # REST API endpoints
│   └── urls.py
├── gamification/         # Gamification & IRT
│   ├── models.py         # Achievement, SkillMastery models
│   ├── irt_engine.py     # IRT implementation
│   ├── signals.py        # Automatic achievement awarding
│   ├── views.py          # Leaderboard, achievements
│   └── urls.py
└── templates/            # HTML templates with Tailwind CSS
```

## API Endpoints

### Sandbox API
- `POST /sandbox/api/sessions/` - Create new sandbox session
- `POST /sandbox/api/sessions/{id}/execute/` - Execute command in container
- `POST /sandbox/api/sessions/{id}/evaluate/` - Evaluate output against challenge
- `POST /sandbox/api/sessions/{id}/stop/` - Stop and cleanup session

### Gamification
- `/gamification/leaderboard/` - View leaderboards
- `/gamification/achievements/` - View achievements
- `/gamification/skill-mastery/` - View skill mastery levels

## IRT Engine

The Item Response Theory engine tracks user skill levels (theta values) for each skill tag and recommends challenges based on:
- User's current ability (theta)
- Challenge difficulty (b parameter)
- Discrimination (a parameter)
- Information function maximization

## Docker Sandbox

The sandbox creates isolated Docker containers for each user session:
- Automatic container creation and cleanup
- Resource limits (512MB RAM, 50% CPU)
- Command execution with timeout (30s per command)
- Session timeout (5 minutes default)

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests (if available)
4. Submit a pull request

## License

[Your License Here]

