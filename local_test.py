"""Run the Gemini review prompt against a local file, no PR or branch needed.

Usage:
    python local_test.py path/to/bad_code.ts [more_files.ts ...]

Reads the given file(s), feeds their contents into the same prompt used by
review.py, and prints Gemini's response to the terminal. Useful for quickly
iterating on the prompt in review.py without opening a PR.
"""

import sys

from review import build_prompt, call_gemini


def main():
    if len(sys.argv) < 2:
        print("Usage: python local_test.py <file> [file ...]")
        raise SystemExit(1)

    paths = sys.argv[1:]
    sections = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            contents = f.read()
        sections.append(f"### {path}\n{contents}")

    code_to_review = "\n\n".join(sections)

    prompt = build_prompt(code_to_review)
    review_text = call_gemini(prompt)
    print(review_text)


if __name__ == "__main__":
    main()
