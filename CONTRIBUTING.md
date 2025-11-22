# Contributing to CodeQuest 🤝

Thank you for your interest in contributing to CodeQuest! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/your-username/codequest.git
   cd codequest
   ```
3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/bnm-sys/codequest.git
   ```
4. **Run the setup script**
   ```bash
   ./startup.sh
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Keep changes focused and atomic
- Write meaningful commit messages

### 3. Code Quality Standards

#### Formatting

We use **Black** and **isort** for code formatting:

```bash
# Format code
black .
isort .
```

#### Linting

We use **Flake8** for linting (line length limit ignored):

```bash
# Check linting
flake8 .
```

All code must pass linting before submission.

#### Type Hints

While not required, type hints are encouraged for new code:

```python
def calculate_xp(points: int, streak: int) -> int:
    return points * (1 + streak // 10)
```

### 4. Testing

All new features must include tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest accounts/tests.py

# Run with coverage
pytest --cov=. --cov-report=html
```

**Testing Requirements:**
- Minimum 80% code coverage for new code
- All tests must pass before PR submission
- Include both positive and negative test cases
- Test edge cases and error handling

**Test Structure:**
```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestYourFeature:
    def test_feature_success(self, client):
        """Test successful scenario."""
        # Arrange
        data = {...}
        
        # Act
        response = client.post(url, data)
        
        # Assert
        assert response.status_code == 200
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add user profile avatar upload feature

- Add ImageField to CustomUser model
- Create upload view and template
- Add validation for image size and format
- Include tests for avatar upload"
```

**Commit Message Format:**
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description with bullet points
- Reference issue numbers if applicable

### 6. Keep Your Branch Updated

Regularly sync with upstream:

```bash
git fetch upstream
git rebase upstream/main
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest`)
- [ ] Linting passes (`flake8 .`)
- [ ] Code is formatted (`black . && isort .`)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains the changes

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Changes Made
- Change 1
- Change 2

## Testing
- Test scenario 1
- Test scenario 2

## Screenshots (if applicable)
```

## Reporting Bugs 🐛

### Before Reporting

- Check if the bug has already been reported
- Verify the bug exists in the latest version
- Check if it's actually a bug or expected behavior

### Bug Report Template

```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12]
- Django version: [e.g., 5.0]

**Additional Context:**
Logs, screenshots, etc.
```

## Feature Requests 💡

We welcome feature requests! Please:

1. Check if the feature has been requested before
2. Clearly describe the feature and its benefits
3. Provide use cases and examples
4. Be open to discussion and alternatives

## Code Style Guide

### Python

- Follow PEP 8 (enforced by Flake8)
- Use meaningful variable names
- Keep functions small and focused
- Add docstrings to functions and classes
- Prefer explicit over implicit

### Django

- Use class-based views where appropriate
- Keep business logic in models
- Use Django's built-in features
- Follow Django naming conventions
- Optimize database queries (avoid N+1)

### Example

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    """A learning course with modules and challenges."""
    
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.title

    @property
    def total_enrolled(self):
        """Return the total number of enrolled students."""
        return self.enrollments.count()
```

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update API documentation if applicable
- Include inline comments for complex logic

## Performance Considerations

- Use `select_related()` and `prefetch_related()`
- Avoid N+1 query problems
- Use database indexes appropriately
- Cache expensive operations
- Profile code for bottlenecks

## Security Guidelines

- Never commit secrets or credentials
- Validate all user inputs
- Use Django's built-in security features
- Follow OWASP guidelines
- Report security issues privately

## Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainers review the code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged
5. **Cleanup**: Delete your feature branch

## Questions?

- Open an issue for questions
- Join discussions in existing issues
- Contact maintainers directly

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to CodeQuest! 🎉
