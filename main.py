import json
import os
import random
import re
import sys
import urllib.error
import urllib.request

DEFAULT_COMMANDS = ["/pr-or-gtfo", "/prorgtfo"]

# Keep all possible responses here. A random one is posted whenever a trigger matches.
SAYINGS = [
    "please kindly develop a PR to address this proposal or GTFO out of here",
    "proposal acknowledged; please open a PR to move this forward or kindly step aside",
    "great idea, now turn it into a PR or respectfully GTFO",
    "this suggestion needs code: submit a PR or make room for someone who will",
    "request received, but execution wins: bring a PR or bounce",
]


def parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    return default


def parse_commands(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in re.split(r"[\n,]+", raw) if item.strip()]


def set_output(name: str, value: str) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as output_file:
        output_file.write(f"{name}={value}\n")


def extract_context(payload: dict, event_name: str) -> dict | None:
    if event_name == "issue_comment":
        return {
            "body": payload.get("comment", {}).get("body"),
            "issue_number": payload.get("issue", {}).get("number"),
            "sender_type": payload.get("sender", {}).get("type"),
        }

    if event_name == "pull_request_review_comment":
        return {
            "body": payload.get("comment", {}).get("body"),
            "issue_number": payload.get("pull_request", {}).get("number"),
            "sender_type": payload.get("sender", {}).get("type"),
        }

    if event_name == "pull_request_review":
        return {
            "body": payload.get("review", {}).get("body"),
            "issue_number": payload.get("pull_request", {}).get("number"),
            "sender_type": payload.get("sender", {}).get("type"),
        }

    return {
        "body": payload.get("comment", {}).get("body")
        or payload.get("review", {}).get("body")
        or payload.get("body"),
        "issue_number": payload.get("issue", {}).get("number")
        or payload.get("pull_request", {}).get("number"),
        "sender_type": payload.get("sender", {}).get("type"),
    }


def contains_command(body: str, commands: list[str]) -> bool:
    normalized_body = body.lower()
    return any(command.lower() in normalized_body for command in commands)


def post_issue_comment(
    token: str, owner: str, repo: str, issue_number: int, comment_body: str
) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    payload = json.dumps({"body": comment_body}).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(request):
            return
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed with {exc.code}: {response_body}"
        ) from exc


def main() -> int:
    set_output("triggered", "false")
    set_output("selected-saying", "")

    token = os.getenv("INPUT_TOKEN")
    if not token:
        raise RuntimeError("Missing required input: token")

    repository = os.getenv("GITHUB_REPOSITORY", "")
    if "/" not in repository:
        raise RuntimeError("Missing or invalid GITHUB_REPOSITORY environment variable")

    owner, repo = repository.split("/", 1)

    event_path = os.getenv("GITHUB_EVENT_PATH")
    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    if not event_path or not os.path.exists(event_path):
        raise RuntimeError("Missing or invalid GITHUB_EVENT_PATH")

    with open(event_path, "r", encoding="utf-8") as event_file:
        payload = json.load(event_file)

    context = extract_context(payload, event_name)
    if not context:
        print("No comment context found in payload. Nothing to do.")
        return 0

    body = context.get("body")
    issue_number = context.get("issue_number")
    sender_type = str(context.get("sender_type") or "")

    if not body or not issue_number:
        print("No comment or issue/PR number found in payload. Nothing to do.")
        return 0

    ignore_bots = parse_bool(os.getenv("INPUT_IGNORE_BOTS"), True)
    if ignore_bots and sender_type.lower() == "bot":
        print("Comment came from a bot user. Ignoring.")
        return 0

    commands = parse_commands(os.getenv("INPUT_COMMANDS"))
    active_commands = commands or DEFAULT_COMMANDS

    if not contains_command(body, active_commands):
        print("No trigger command found in the comment body.")
        return 0

    saying_pool = SAYINGS or [
        "please kindly develop a PR to address this proposal or GTFO out of here"
    ]
    selected_saying = random.choice(saying_pool)

    post_issue_comment(token, owner, repo, int(issue_number), selected_saying)

    set_output("triggered", "true")
    set_output("selected-saying", selected_saying)

    print(f"Posted response to #{issue_number} after matching command in {event_name}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
