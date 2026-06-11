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


# Fetch the changed code from the pull request to review
code_to_review = get_pr_diff("jaredsturisky", "Code-Review-Agent", 2)

# Stop here if the fetch failed, so we don't send the literal text "None" to Gemini
if code_to_review is None:
    print("Could not fetch the PR diff, so there is nothing to review. Exiting.")
    raise SystemExit(1)

# The instruction we give Gemini, with the code attached
prompt = f"""You are a code reviewer. Review the following code for bugs,
security issues, and code quality. Summarize each problem in one sentence. Final output should be no longer than 1 sentence.

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
post_pr_comment("jaredsturisky", "Code-Review-Agent", 2, review_text)