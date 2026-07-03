import json
import os
import requests
from dotenv import load_dotenv
from google import genai

# Load the variables from .env into the environment
load_dotenv()

# Read the API key that .env just loaded
api_key = os.getenv("GEMINI_API_KEY")

# Create a client
client = genai.Client(api_key=api_key)

# Maximum number of lines a single file may contain before it is flagged.
# Kept as a simple constant so it is easy to change later.
MAX_FILE_LINES = 500


def get_pr_context():
    """Determine which PR to review and which repo it lives in.

    When running inside a GitHub Action, GitHub writes the event payload to a
    JSON file whose path is in the GITHUB_EVENT_PATH environment variable. For a
    pull_request event that payload contains the PR number at `number`, the repo
    owner at `repository.owner.login`, and the repo name at `repository.name`.

    Returns a (owner, repo, pr_number) tuple. If GITHUB_EVENT_PATH is not set
    (i.e. running locally rather than in an Action), falls back to hardcoded
    values so the script can still be tested manually.
    """
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        # Running locally: use the hardcoded test values.
        return "jaredsturisky", "Code-Review-Agent", 2

    with open(event_path, encoding="utf-8") as event_file:
        event = json.load(event_file)

    owner = event["repository"]["owner"]["login"]
    repo = event["repository"]["name"]
    pr_number = event["number"]

    return owner, repo, pr_number


def get_pr_diff(owner, repo, pr_number):
    """Fetch the changed code from a GitHub pull request.

    Calls the GitHub REST API to list the files changed in the given PR and
    returns the combined diff text, joining each file's `patch` and labeling
    every section with its filename.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set in the environment.")
        return None

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        status = error.response.status_code
        print(f"GitHub API request failed with HTTP {status}: {error.response.reason}")
        return None
    except requests.exceptions.RequestException as error:
        print(f"Could not reach the GitHub API: {error}")
        return None

    files = response.json()

    sections = []
    for changed_file in files:
        filename = changed_file.get("filename", "unknown file")
        patch = changed_file.get("patch")
        if patch is None:
            # Binary files and some renames have no patch text.
            sections.append(f"### {filename}\n(no diff available)")
        else:
            sections.append(f"### {filename}\n{patch}")

    return "\n\n".join(sections)


def post_pr_comment(owner, repo, pr_number, comment_body):
    """Post a general comment on a GitHub pull request.

    Uses the GitHub REST API issues endpoint (PRs are issues for the purpose of
    general comments) to add `comment_body` as a comment on the given PR. On
    success it prints a confirmation and the URL of the new comment.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set in the environment.")
        return None

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"body": comment_body}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        status = error.response.status_code
        print(f"Failed to post PR comment (HTTP {status}): {error.response.reason}")
        return None
    except requests.exceptions.RequestException as error:
        print(f"Could not reach the GitHub API to post the comment: {error}")
        return None

    comment = response.json()
    comment_url = comment.get("html_url")
    if comment_url:
        print(f"Posted review comment to PR #{pr_number}: {comment_url}")
    else:
        print(f"Posted review comment to PR #{pr_number}.")

    return comment


def build_prompt(code_to_review):
    """Build the Gemini review prompt for the given code/diff text."""
    return f"""
You are a senior code reviewer for a Node.js and React codebase backed by a PostgreSQL database.

Review only the provided pull request diff.
Only comment on issues actually present in the diff.
Do not invent issues.
Do not review code that is not shown.

Be concise.
Do not write paragraphs.
Use brief sentences only.

Review against these standards:

General:
Flag readability, maintainability, production readiness, simplicity, consistency, overengineering, duplicate logic, tight coupling, and dead code issues.

File constraints:
Flag any file that is empty or has no meaningful code.
Flag any file longer than {MAX_FILE_LINES} lines; a file must not exceed this limit.

Clean Architecture:
Flag database logic, HTTP calls, ORM or TypeORM decorators, and Express imports inside the domain layer.
Flag controllers that contain business logic, database calls, or external API calls.
Flag repositories with raw or string-concatenated PostgreSQL queries, missing parameterization, missing pagination, inefficient queries, indexing concerns, or N plus 1 query risks.

TypeScript (applies only to .ts and .tsx files; never flag a .js or .jsx file for not being TypeScript and never suggest converting it):
Flag use of any, implicit types, unsafe casting, missing interfaces, and weak DTO typing.

Security:
This is your highest priority. Scrutinize every diff for security problems first, and never overlook a potential vulnerability even when other issues are present; keep considering the other standards too, but security comes first.
Flag hardcoded credentials, secrets in source code, sensitive data in logs, SQL injection, unparameterized or string-built PostgreSQL queries, NoSQL injection, unsafe dynamic queries, and missing authorization checks.

Package security:
Flag dependencies with known vulnerabilities or CVEs, outdated or unmaintained packages, and suspicious, malicious, or typosquatted package names.
Flag dependencies pulled from untrusted sources, loose or wildcard version ranges that allow unexpected upgrades, and unnecessary new dependencies that duplicate existing functionality.

Error handling:
Flag missing try catch where needed, empty catch blocks, unhandled errors, raw stack trace exposure, and missing centralized error handling.

React:
Flag unsafe dangerouslySetInnerHTML, XSS risks, missing input sanitization, exposed frontend secrets, and sensitive tokens stored in localStorage.

AI generated code:
Flag fake packages, fake APIs, invalid imports, hallucinated libraries, and meaningless boilerplate.

Secrets:
Flag committed .env values, frontend secrets, and hardcoded secrets.
Expect environment variables for secret values.

Output format for each issue:

Location:
Severity:
Problem:
Suggested Edit:
```<language>
// Replace:
<exact problematic lines from the diff>

// With:
<corrected replacement code>
```

Rules:
Keep Location, Severity, and Problem to one brief sentence each.
Always include Suggested Edit. For code issues use a Replace/With code block targeting the exact lines from the diff; for file-level issues (an empty file or a file over the line limit) give a one-sentence instruction instead.
Use the correct language identifier in the code fence (ts, js, tsx, etc.).
Copy the exact problematic lines from the diff into Replace.
Write only the corrected replacement in With.
Do not add prose after the code block.
Do not include long explanations.
Do not include paragraphs.
Do not repeat the same issue multiple times.

If there are no issues, say exactly:
No issues found in the provided diff.

Pull request diff:
{code_to_review}
"""


def call_gemini(prompt, model="gemini-2.5-flash"):
    """Send a prompt to Gemini and return the response text.

    Returns None if the request fails so callers can handle the error instead
    of crashing with a raw traceback.
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    except Exception as error:
        print(f"Gemini request failed: {error}")
        return None

    return response.text


def main():
    # Figure out which PR/repo to review (from the GitHub event, or local fallback)
    owner, repo, pr_number = get_pr_context()

    # Fetch the changed code from the pull request to review
    code_to_review = get_pr_diff(owner, repo, pr_number)

    # Stop here if the fetch failed, so we don't send the literal text "None" to Gemini
    if code_to_review is None:
        print("Could not fetch the PR diff, so there is nothing to review. Exiting.")
        raise SystemExit(1)

    prompt = build_prompt(code_to_review)

    # Print Gemini's review to the terminal
    review_text = call_gemini(prompt)

    # Stop here if the Gemini call failed, so we don't post "None" as the review
    if review_text is None:
        print("Gemini did not return a review, so there is nothing to post. Exiting.")
        raise SystemExit(1)

    print(review_text)

    # Decide the verdict from Gemini's own conclusion.
    issues_found = "No issues found in the provided diff." not in review_text
    if issues_found:
        header = (
            "Gemini review: issues found below. This check is failing on purpose "
            "to block the merge until they are resolved."
        )
    else:
        header = "Gemini review: no issues found."

    comment_body = f"{header}\n\n{review_text}"

    # Post Gemini's feedback as a comment first, so the reviewer sees it whether
    # or not the check ends up failing.
    post_pr_comment(owner, repo, pr_number, comment_body)

    # Block the merge when issues are found by failing the required check. The
    # red check is intentional here (it is the merge gate, not a crash); a clean
    # review leaves the check green so the PR can be merged.
    if issues_found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()