"""Regenerate the security guidelines explorer's rule data from rules.json.

`rules.json` is the single source of truth shared by the review agent and the
human-facing explorer. This script rewrites only the `const RULES = [...]` array
inside `security_guidelines_explorer.html` so the explorer can never drift from
what `review.py` enforces. The HTML shell (styling and behavior) is untouched.

The explorer's fields map onto the rulebook like so:
    desc <- detect, bad <- insecure_example, good <- secure_example

Usage:
    python build_explorer.py          # rewrite the explorer in place
    python build_explorer.py --check  # exit 1 if the explorer is out of sync
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(HERE, "rules.json")
EXPLORER_PATH = os.path.join(HERE, "security_guidelines_explorer.html")

# The RULES array is the only region we rewrite. `];` never appears inside the
# rule strings (verified against the data), so a non-greedy match is safe.
RULES_RE = re.compile(r"const RULES = \[.*?\];", re.DOTALL)


def js(value):
    """Serialize a Python string as a valid JS string literal (double-quoted)."""
    return json.dumps(value, ensure_ascii=False)


def build_array(rules):
    """Render the rulebook as the explorer's `const RULES = [...]` array text."""
    lines = ["const RULES = ["]
    for rule in rules:
        lines.append(
            "  {"
            f"id:{js(rule['id'])},layer:{js(rule['layer'])},"
            f"severity:{js(rule['severity'])},title:{js(rule['title'])},"
            f"owasp:{js(rule['owasp'])},desc:{js(rule['detect'])},"
            f"bad:{js(rule['insecure_example'])},good:{js(rule['secure_example'])}"
            "},"
        )
    lines.append("];")
    return "\n".join(lines)


def main():
    check_only = "--check" in sys.argv[1:]

    with open(RULES_PATH, encoding="utf-8") as rules_file:
        rules = json.load(rules_file)
    with open(EXPLORER_PATH, encoding="utf-8") as html_file:
        html = html_file.read()

    if not RULES_RE.search(html):
        print("Could not find the 'const RULES = [...]' array in the explorer.")
        raise SystemExit(1)

    # Pass a function as the replacement so backslashes in the rule data are not
    # interpreted as regex backreferences.
    new_html = RULES_RE.sub(lambda _match: build_array(rules), html, count=1)

    if check_only:
        if new_html != html:
            print(
                "Explorer is OUT OF SYNC with rules.json. "
                "Run: python build_explorer.py"
            )
            raise SystemExit(1)
        print("Explorer is in sync with rules.json.")
        return

    if new_html == html:
        print("Explorer already in sync with rules.json; no changes written.")
        return

    with open(EXPLORER_PATH, "w", encoding="utf-8") as html_file:
        html_file.write(new_html)
    print(
        f"Regenerated {os.path.basename(EXPLORER_PATH)} from rules.json "
        f"({len(rules)} rules)."
    )


if __name__ == "__main__":
    main()
