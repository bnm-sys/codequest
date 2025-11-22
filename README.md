# CodeQuest 🎓

An interactive learning platform for coding challenges with gamification features including XP, streaks, and progress tracking.

## Features ✨

- **User Authentication**: Secure registration and login with email/phone validation
- **Course Management**: Browse and enroll in programming courses
- **Challenge System**: Interactive coding challenges with instant feedback
- **Gamification**: Track XP, streaks, and progress
- **Email Notifications**: Welcome emails via Mailhog integration
- **PostgreSQL Backend**: Robust database with optimized queries
- **Comprehensive Testing**: Full test coverage with pytest

## Tech Stack 🛠️

- **Backend**: Django 5.0
- **Database**: PostgreSQL 13
- **Email**: Mailhog (Development)
- **Testing**: pytest, pytest-django
- **Code Quality**: Black, isort, Flake8
- **CI/CD**: GitHub Actions

## Quick Start 🚀

### Prerequisites

- Python 3.12+
- Docker (for PostgreSQL and Mailhog)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bnm-sys/codequest.git
   cd codequest
   ```

2. **Start Docker services**
   ```bash
   docker-compose up -d
   ```

3. **Run automated setup**
   ```bash
   ./startup.sh
   ```

4. **Start the development server**
   ```bash
   ./env/bin/python manage.py runserver 0.0.0.0:8001
   ```

5. **Access the application**
   - Application: http://localhost:8001
   - Admin Panel: http://localhost:8001/admin
   - Mailhog UI: http://localhost:8025

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver 0.0.0.0:8001
```

## Configuration ⚙️

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=codequest
DB_USER=postgres
DB_PASSWORD=********
DB_HOST=localhost
DB_PORT=15432

# Email
EMAIL_HOST=localhost
EMAIL_PORT=1025
```

## Default Credentials 🔑

- **Admin User**: `admin` / `********`
- **Database**: `postgres` / `*********`

## Testing 🧪

Run the complete test suite:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run specific test file:

```bash
pytest accounts/tests.py
```

## Code Quality 📊

Format code:

```bash
black .
isort .
```

Run linting:

```bash
flake8 .
```

## Project Structure 📁

```
codequest/
├── accounts/           # User authentication & profiles
├── courses/            # Course management & challenges
├── templates/          # HTML templates
├── codequest/          # Project settings
├── .github/            # CI/CD workflows
├── docker-compose.yml  # Docker services
├── startup.sh          # Automated setup script
└── requirements.txt    # Python dependencies
```

## API Endpoints 🔗

- `/` - Home page
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/dashboard/` - User dashboard
- `/courses/` - Course listing
- `/admin/` - Admin panel

## Development Workflow 💻

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `flake8 .`
5. Format code: `black . && isort .`
6. Commit and push
7. Create a pull request

## CI/CD Pipeline 🔄

The project uses GitHub Actions for continuous integration:

- **Code Quality**: Black, isort, Flake8 checks
- **Testing**: Automated test suite with PostgreSQL
- **Triggers**: Push/PR to main or develop branches

## Contributing 🤝

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💬

For questions or issues, please open an issue on GitHub.

## Roadmap 🗺️

- [ ] Code execution sandbox
- [ ] Real-time leaderboards
- [ ] Course creator interface
- [ ] Social features (comments, discussions)
- [ ] Achievement badges
- [ ] API documentation

## Acknowledgments 🙏

- Django community
- Contributors and testers
- Open source libraries used in this project
