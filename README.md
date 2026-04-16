# PR or GTFO

A GitHub Action that listens for trigger phrases in issue or pull request comments and posts a randomized follow-up response.

If a comment includes `/pr-or-gtfo` or `/prorgtfo` (customizable), the action can reply with:

> please kindly develop a PR to address this proposal or GTFO out of here

The sayings list is stored directly in `main.py`, and one saying is chosen at random each time.

## What It Does

- Detects configured trigger commands in comment text.
- Supports issue comments and pull request comments/reviews.
- Selects a random saying from the in-file sayings list.
- Posts the selected saying as a follow-up issue/PR comment.

## Quick Start

Create a workflow in your repository, for example `.github/workflows/pr-or-gtfo.yml`:

```yaml
name: PR or GTFO responder

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  pull_request_review:
    types: [submitted]

permissions:
  issues: write
  pull-requests: write

jobs:
  respond:
    runs-on: ubuntu-latest
    steps:
      - name: PR or GTFO
        uses: NeuroShepherd/pr-or-gtfo@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commands: |
            /pr-or-gtfo
            /prorgtfo
```

## Customize Sayings

Edit the `SAYINGS` list in `main.py`.

```python
SAYINGS = [
    "please kindly develop a PR to address this proposal or GTFO out of here",
    "proposal acknowledged; please open a PR to move this forward or kindly step aside",
    "great idea, now turn it into a PR or respectfully GTFO",
]
```

Each trigger comment picks one entry at random.

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `token` | Yes | n/a | GitHub token with permission to create issue comments. Usually `${{ secrets.GITHUB_TOKEN }}`. |
| `commands` | No | `/pr-or-gtfo,/prorgtfo` | Comma or newline-separated trigger commands. |
| `ignore-bots` | No | `true` | Ignore comments from bot users. |

## Outputs

| Name | Description |
| --- | --- |
| `triggered` | `true` when a command match was found and a response was posted. |
| `selected-saying` | The saying that was selected and posted. |

## Notes

- This action does not run by itself; it runs inside your workflow.
- It posts through the Issues API, which works for both issues and pull requests.
- For pull requests from forks, ensure your workflow/event setup matches your repository security model.

## Marketplace Prep Checklist

- Add a license file.
- Tag a release like `v1`.
- Keep `README.md` and `action.yml` up to date.
- Optionally configure repository topics and branding.
