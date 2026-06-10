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


# Fetch the changed code from the pull request to review
code_to_review = get_pr_diff("jaredsturisky", "Code-Review-Agent", 1)

# Stop here if the fetch failed, so we don't send the literal text "None" to Gemini
if code_to_review is None:
    print("Could not fetch the PR diff, so there is nothing to review. Exiting.")
    raise SystemExit(1)

# The instruction we give Gemini, with the code attached
prompt = f"""You are a code reviewer. Review the following code for bugs,
security issues, and code quality. Be specific and concise.

Code:
{code_to_review}
"""

# Send the prompt to Gemini and get a response
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

# Print Gemini's review to the terminal
print(response.text)