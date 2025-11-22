# Feature Plan (Django-First)

Track work in small steps. Each feature lists executable tasks and subtasks you can do sequentially.

## 1) Project Setup & Quality Gates
- [x] Confirm Python/Django versions in `README.md` and `pyproject.toml`
- [x] Add `pre-commit` hooks (black, isort, flake8, bandit)
- [x] Configure CI (GitHub Actions) for lint + tests + migrations check
- [x] Create `.env.example` and document settings loading
- [ ] Add healthcheck endpoint and basic ops runbook

## 2) Auth & Profiles
- [x] Enable email/password signup + login; enforce strong passwords
- [x] Add profile model for locale preference (English/Nepali) and display name
- [x] Wire Django messages + templates to honor locale selection
- [ ] Add password reset and email verification flows
- [x] Create seed command for demo users (learner, coach)

## 3) Localization (English/Nepali)
- [x] Turn on Django i18n with `LANGUAGES = ['en', 'ne']`
- [x] Add translation strings to templates and views (`gettext_lazy`)
- [x] Create translation files and initial `.po` entries for both languages
- [ ] Verify fonts render Nepali; set fallback font stack in base template
- [x] Add language switcher UI and persist choice in session/profile

## 4) Course & Module Model
- [ ] Define models: Track, Module, Lesson, Lab, QuizQuestion, QuizOption, TaskOutcome
- [x] Add admin for all course objects with search/filter
- [ ] Seed fixtures: starter Git track (init, clone, commit, branch, merge)
- [ ] Add slugged URLs for modules/lessons; friendly breadcrumb in templates
- [ ] Add permissions: only coaches can publish modules

## 5) Adaptive Engine (Rule-Based MVP)
- [ ] Model learner skill levels per tag (e.g., git_basics, branching, ci_cd)
- [ ] Add attempt logging: lesson_id, task_id, score, duration, hints_used
- [ ] Implement simple rule engine: promote/demote skill level based on recent attempts
- [ ] Endpoint/service to suggest next lesson given current skill profile
- [ ] Store “why this next” reason and surface it in UI

## 6) Lesson Delivery (Web)
- [x] Base templates: dashboard, module detail, lesson page
- [ ] Render bilingual content blocks (Markdown) with toggle
- [ ] Embed code snippets and terminal transcripts with copy buttons
- [ ] Add hint/request-help buttons that log usage
- [ ] Track completion state and time-on-task per lesson

## 7) Practical Git Labs (Local + Remote Repo)
- [ ] Create lab template repo (with intentional issues) for each module
- [ ] Add lab assignment model linking to repo URL and expected checks
- [ ] Build lab runner service: clone repo, run check script, post results
- [ ] Provide downloadable lab bundle and instructions for local execution
- [ ] Store graded results and surface pass/fail with diffs in UI

## 8) Quizzes & Checks
- [ ] Multiple-choice and short-answer quiz models with correct answers
- [ ] Server-side scoring; prevent resubmit spam via throttling
- [ ] Adaptive difficulty: pick next question level from skill profile
- [ ] Show explanations (en/ne) after submission
- [ ] Export/import quizzes as YAML for content authors

## 9) Coaching & Feedback
- [ ] Add feedback form per lesson/lab with rating + free text
- [ ] Coach dashboard: view attempts, common errors, and stuck learners
- [ ] Trigger “review request” workflow when learner fails twice
- [ ] Email/notification hooks for coach interventions

## 10) Progress & Reporting
- [ ] Progress model per learner per track; completion percentage and streaks
- [ ] Generate progress dashboards (per user, per cohort)
- [ ] Export CSV/PDF summaries; include bilingual headings
- [ ] Add weekly digest email with recommended next steps

## 11) Content Authoring Workflow
- [ ] Markdown/MDX storage for lessons with front-matter (`title_en`, `title_ne`, `body_en`, `body_ne`)
- [ ] Admin/editor preview of lessons before publish
- [ ] Versioning: keep content in Git; show changelog on lesson page
- [ ] Media handling: image upload with alt text in both languages
- [ ] Content lint: check for missing translations or broken links

## 12) System & DevOps Tasks (Platform Engineering Focus)
- [ ] Add labs for git ops in real workflows (hooks, CI, release tagging)
- [ ] Add labs for Linux basics (package install, service mgmt, logging)
- [ ] Add monitoring/tuning labs (collectd/Prometheus basics, log analysis)
- [ ] Provide containerized sandbox for labs (Docker Compose template)
- [ ] Write ops runbooks for each lab with expected outcomes

## 13) Security & Privacy
- [ ] Enforce HTTPS and secure cookies; configure CSP
- [ ] Rate-limit auth and submission endpoints
- [ ] Audit logging for admin/content changes
- [ ] Data retention policy and user data export/delete flow
- [ ] Secrets management documentation and `.env` guidance

## 14) Observability & Support
- [ ] Request/response logging with correlation IDs
- [ ] Basic metrics (Prometheus or StatsD) for key flows
- [ ] Error reporting (Sentry or similar) with PII scrubbing
- [ ] Status page endpoint and DB readiness check
- [ ] Support page with FAQ and contact info (en/ne)

## 15) Deployment & Environments
- [ ] Dockerfile + docker-compose for local; document hot-reload
- [ ] Staging/prod settings split; environment-specific configs
- [ ] DB migrations workflow and backup/restore guide
- [ ] CDN/static files pipeline; collectstatic checks in CI
- [ ] Minimal infra-as-code sample (optional) for future cloud deploys

## 16) Optional LLM Integration (Later)
- [ ] Plug-in layer for hosted/local LLM to generate hints/explanations
- [ ] Safety filters and guardrails before showing responses
- [ ] Cache/track prompts to reduce cost and improve reuse
- [ ] Fallback to rule-based hints when model unavailable
- [ ] Content authors can pre-approve/override AI hints
