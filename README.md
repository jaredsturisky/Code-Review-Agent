# Code-Review-Agent

An AI agent that automatically reviews GitHub pull requests using Google's Gemini model. When a PR is opened, reopened, or updated, a GitHub Action fetches the PR diff, asks Gemini to review it for bugs, security issues, and code quality, and posts the review back as a comment on the PR.

## How it works

1. A `pull_request` event triggers the **AI Code Review** GitHub Action (`.github/workflows/ai-review.yml`).
2. `review.py` reads the PR context (owner, repo, number) from the GitHub event payload.
3. It fetches the changed files' diff via the GitHub REST API.
4. When the diff touches `package.json`, the workflow runs `npm audit` and passes the results to the review as ground truth for dependency (PKG-*) findings.
5. It builds the prompt from the security rulebook (`rules.json`) plus the diff, and sends it to Gemini (`gemini-2.5-flash`).
6. It posts Gemini's review back to the PR as a comment. Only **critical** findings fail the check (blocking merge when the check is required); warnings are advisory.

## Security rulebook (single source of truth)

`rules.json` is the canonical list of security rules the agent enforces. Each rule has a stable ID (e.g. `NODE-001`), a severity (`critical`/`warning`), an OWASP tag, and secure/insecure examples. Every finding cites its rule ID.

The human-facing `security_guidelines_explorer.html` is **generated** from `rules.json` — never edit its rule data by hand. After changing `rules.json`, regenerate it:

```bash
python build_explorer.py          # rewrite the explorer from rules.json
python build_explorer.py --check  # verify they are in sync (used in CI)
```

The workflow runs `--check` on every PR, so an edit to `rules.json` that forgets to regenerate the explorer will fail the build.

## Setup

Add this secret to your repository (**Settings → Secrets and variables → Actions**):

- `GEMINI_API_KEY` — your Google Gemini API key.

You don't need to add `GITHUB_TOKEN`: GitHub Actions provides it automatically, and the workflow grants it `pull-requests: write`.

That's it — the workflow runs on every PR automatically.

## Running locally

```bash
pip install -r requirements.txt
```

Create a `.env` file with:

```ini
GEMINI_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_token
```

Then run:

```bash
python review.py
```

When run outside a GitHub Action, the script falls back to reviewing a hardcoded PR (see `get_pr_context()` in `review.py`) for manual testing.

## Project structure

| File | Purpose |
| --- | --- |
| `review.py` | Fetches the PR diff, runs the Gemini review, and posts the comment. |
| `rules.json` | The security rulebook — single source of truth for the rules the agent enforces. |
| `build_explorer.py` | Regenerates `security_guidelines_explorer.html` from `rules.json`; `--check` verifies sync. |
| `security_guidelines_explorer.html` | Human-facing, generated view of the rulebook. Do not edit its rule data by hand. |
| `.github/workflows/ai-review.yml` | GitHub Action that runs the review on pull request events. |
| `requirements.txt` | Python dependencies. |
