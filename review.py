import os
from dotenv import load_dotenv
from google import genai

# Load the variables from .env into the environment
load_dotenv()

# Read the API key that .env just loaded
api_key = os.getenv("GEMINI_API_KEY")

# Create a client - this is your connection to Gemini
client = genai.Client(api_key=api_key)

# The code we want reviewed (hardcoded for now - this is fake input)
code_to_review = '''
def login(username, password):
    if password == "123456":
        return True
    return False
'''

# The instruction we give Gemini, with the code attached
prompt = f"""You are a code reviewer. Review the following code for bugs,
security issues, and code quality. Summarize each problem into one brief sentence.

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