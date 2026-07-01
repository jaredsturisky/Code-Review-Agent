# Code-Review-Agent

An AI agent that automatically reviews GitHub pull requests using Google's Gemini model. When a PR is opened, reopened, or updated, a GitHub Action fetches the PR diff, asks Gemini to review it for bugs, security issues, and code quality, and posts the review back as a comment on the PR.

## How it works

1. A `pull_request` event triggers the **AI Code Review** GitHub Action (`.github/workflows/ai-review.yml`).
2. `review.py` reads the PR context (owner, repo, number) from the GitHub event payload.
3. It fetches the changed files' diff via the GitHub REST API.
4. It sends the diff to Gemini (`gemini-2.5-flash`) with a code-review prompt.
5. It posts Gemini's review back to the PR as a comment.

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

```
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
| `.github/workflows/ai-review.yml` | GitHub Action that runs the review on pull request events. |
| `requirements.txt` | Python dependencies. |
