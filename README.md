# PR or GTFO

Are you an open-source project maintainer who receives lots of requests for *super important* new features and proposals for definitely fully-baked ideas, but simply don't have the time to address them yourself? Say no more! With this GitHub Action, you can now simply comment `/pr-or-gtfo` or `/prorgtfo` (customizable) on an issue or pull request, and a follow-up comment such as:

> please kindly develop a PR to address this proposal or GTFO out of here

will *kindly* inform the requestor that they should help out on this special idea!

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

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `token` | Yes | n/a | GitHub token with permission to create issue comments. Usually `${{ secrets.GITHUB_TOKEN }}`. |
| `commands` | No | `/pr-or-gtfo,/prorgtfo` | Comma or newline-separated trigger commands. |
| `ignore-bots` | No | `true` | Ignore comments from bot users. |

## Disclaimer

*This action **does** actually work as described, but was made as a tongue-in-cheek project mostly to learn a bit more about how to build and release actions to the Actions Marketplace.*

I take no responsibility for angry developers who get hit with a `/pr-or-gtfo`.

