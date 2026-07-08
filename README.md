# Dominican Film Dashboard

Executive dashboard for the Dominican Republic film industry built with Python and Streamlit.

## Tech Stack

- Language: Python 3.13
- Dashboard: Streamlit 1.59.0
- Charts: streamlit-echarts, plotly
- Navigation: streamlit-option-menu
- Data: pandas, numpy
- OS: macOS

## Project Structure

```text
dominican-film-dashboard/
├── app.py
├── views/
├── components/
├── utils/
├── charts/
├── data/
├── notebooks/
├── .streamlit/
└── .github/
```

## Setup

1. Create and activate your Python environment.
2. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: install notebook and analysis tooling:

```bash
pip install -r requirements-dev.txt
```

4. Run the dashboard:

```bash
streamlit run app.py
```

## Dependency Profiles

- requirements.txt: runtime dependencies for the Streamlit dashboard.
- requirements-dev.txt: development and notebook dependencies (includes runtime).

## Branch Strategy (GitHub Flow)

- main: production, always stable, protected.
- develop: integration branch.
- feature/\*: new features.
- fix/\*: bug fixes.
- refactor/\*: code reorganization.

## Commit Convention (Conventional Commits)

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting, no logic changes
- refactor: code reorganization
- data: dataset changes
- chore: maintenance tasks

## Pull Request Rules

- feature/\* to develop (never directly to main).
- develop to main (only for releases).
- Always fill the PR template in .github/PULL_REQUEST_TEMPLATE.md.
- Delete feature/fix/refactor branch after merge.
