import json
import os
import requests
from dotenv import load_dotenv
from google import genai

# Load the variables from .env into the environment
load_dotenv()

# Read the API key that .env just loaded
api_key = os.getenv("GEMINI_API_KEY")

# Create a client - this is your connection to Gemini
client = genai.Client(api_key=api_key)


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

    with open(event_path) as event_file:
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
        response = requests.get(url, headers=headers)
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
        response = requests.post(url, headers=headers, json=payload)
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


# Figure out which PR/repo to review (from the GitHub event, or local fallback)
owner, repo, pr_number = get_pr_context()

# Fetch the changed code from the pull request to review
code_to_review = get_pr_diff(owner, repo, pr_number)

# Stop here if the fetch failed, so we don't send the literal text "None" to Gemini
if code_to_review is None:
    print("Could not fetch the PR diff, so there is nothing to review. Exiting.")
    raise SystemExit(1)

# The instruction we give Gemini, with the code attached
prompt = f"""You are a senior code reviewer for a Node.js/TypeScript backend and React frontend codebase. Review the following pull request diff against the team's standards below. Only comment on issues actually present in the diff — do not invent problems or review code that isn't shown.
Evaluate the code against these standards:
General: readability, maintainability, production readiness, simplicity, and consistency. Flag overengineering, unnecessary abstractions, duplicate logic, tight coupling, and dead code.
Clean Architecture (backend): business logic belongs only in domain/use cases. Flag any database logic, HTTP calls, ORM/TypeORM decorators, or Express imports inside the domain layer. Controllers should only validate requests, call use cases, and return responses — flag business logic, database calls, or external API calls in controllers. In repositories, flag raw SQL string concatenation, missing query optimization, missing pagination, indexing problems, and N+1 queries.
TypeScript: require strict typing, proper interfaces, and DTO typing. Flag use of any, implicit types, and unsafe casting.
Security (highest priority): flag hardcoded credentials, sensitive data in logs, SQL or NoSQL injection, unsafe dynamic queries, and missing authorization checks.
Error handling: require try/catch and centralized error middleware. Flag empty catch blocks, raw stack trace exposure, and unhandled errors.
React: require XSS protection, secure token handling, and input sanitization. Flag unsafe dangerouslySetInnerHTML, exposed secrets, and insecure token storage (e.g. sensitive tokens in localStorage).
AI-generated code: verify imported libraries and APIs actually exist. Flag hallucinated packages, fake APIs, and meaningless boilerplate.
Secrets: flag any secrets in source code or frontend, and committed .env values. Expect environment-variable usage.
For each issue you find, provide: the file and approximate location, a severity level (Critical, High, Medium, or Low), a brief explanation, and actionable remediation guidance with a short corrected code example where helpful. If the diff has no issues, say so clearly rather than inventing concerns. Be concise and specific.
Pull request diff:

{code_to_review}

Code:
{code_to_review}
"""

# Send the prompt to Gemini and get a response
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Print Gemini's review to the terminal
review_text = response.text
print(review_text)

# Post the review back to the pull request as a comment
post_pr_comment(owner, repo, pr_number, review_text)