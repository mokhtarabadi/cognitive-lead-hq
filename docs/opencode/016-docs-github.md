---
title: GitHub
url: https://opencode.ai/docs/github/
source: crawler
fetched_at: 2026-02-14T12:04:44.041492-03:00
rendered_js: false
word_count: 769
summary: This document provides comprehensive instructions for installing, configuring, and using OpenCode to automate GitHub tasks like issue triaging and code reviews via GitHub Actions.
tags:
    - github-actions
    - ai-agent
    - workflow-automation
    - opencode
    - continuous-integration
    - github-app
category: guide
---

Use OpenCode in GitHub issues and pull-requests.

OpenCode integrates with your GitHub workflow. Mention `/opencode` or `/oc` in your comment, and OpenCode will execute tasks within your GitHub Actions runner.

* * *

## [Features](#features)

- **Triage issues**: Ask OpenCode to look into an issue and explain it to you.
- **Fix and implement**: Ask OpenCode to fix an issue or implement a feature. And it will work in a new branch and submits a PR with all the changes.
- **Secure**: OpenCode runs inside your GitHub’s runners.

* * *

## [Installation](#installation)

Run the following command in a project that is in a GitHub repo:

This will walk you through installing the GitHub app, creating the workflow, and setting up secrets.

* * *

### [Manual Setup](#manual-setup)

Or you can set it up manually.

1. **Install the GitHub app**
   
   Head over to [**github.com/apps/opencode-agent**](https://github.com/apps/opencode-agent). Make sure it’s installed on the target repository.
2. **Add the workflow**
   
   Add the following workflow file to `.github/workflows/opencode.yml` in your repo. Make sure to set the appropriate `model` and required API keys in `env`.
   
   ```
   
   name: opencode
   on:
   issue_comment:
   types: [created]
   pull_request_review_comment:
   types: [created]
   jobs:
   opencode:
   if: |
   contains(github.event.comment.body, '/oc') ||
   contains(github.event.comment.body, '/opencode')
   runs-on: ubuntu-latest
   permissions:
   id-token: write
   steps:
   - name: Checkout repository
   uses: actions/checkout@v6
   with:
   fetch-depth: 1
   persist-credentials: false
   - name: Run OpenCode
   uses: anomalyco/opencode/github@latest
   env:
   ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
   with:
   model: anthropic/claude-sonnet-4-20250514
   # share: true
   # github_token: xxxx
   ```
3. **Store the API keys in secrets**
   
   In your organization or project **settings**, expand **Secrets and variables** on the left and select **Actions**. And add the required API keys.

* * *

## [Configuration](#configuration)

- `model`: The model to use with OpenCode. Takes the format of `provider/model`. This is **required**.
- `agent`: The agent to use. Must be a primary agent. Falls back to `default_agent` from config or `"build"` if not found.
- `share`: Whether to share the OpenCode session. Defaults to **true** for public repositories.
- `prompt`: Optional custom prompt to override the default behavior. Use this to customize how OpenCode processes requests.
- `token`: Optional GitHub access token for performing operations such as creating comments, committing changes, and opening pull requests. By default, OpenCode uses the installation access token from the OpenCode GitHub App, so commits, comments, and pull requests appear as coming from the app.
  
  Alternatively, you can use the GitHub Action runner’s [built-in `GITHUB_TOKEN`](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token) without installing the OpenCode GitHub App. Just make sure to grant the required permissions in your workflow:
  
  ```
  
  permissions:
  id-token: write
  contents: write
  pull-requests: write
  issues: write
  ```
  
  You can also use a [personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)(PAT) if preferred.

* * *

## [Supported Events](#supported-events)

OpenCode can be triggered by the following GitHub events:

Event TypeTriggered ByDetails`issue_comment`Comment on an issue or PRMention `/opencode` or `/oc` in your comment. OpenCode reads context and can create branches, open PRs, or reply.`pull_request_review_comment`Comment on specific code lines in a PRMention `/opencode` or `/oc` while reviewing code. OpenCode receives file path, line numbers, and diff context.`issues`Issue opened or editedAutomatically trigger OpenCode when issues are created or modified. Requires `prompt` input.`pull_request`PR opened or updatedAutomatically trigger OpenCode when PRs are opened, synchronized, or reopened. Useful for automated reviews.`schedule`Cron-based scheduleRun OpenCode on a schedule. Requires `prompt` input. Output goes to logs and PRs (no issue to comment on).`workflow_dispatch`Manual trigger from GitHub UITrigger OpenCode on demand via Actions tab. Requires `prompt` input. Output goes to logs and PRs.

### [Schedule Example](#schedule-example)

Run OpenCode on a schedule to perform automated tasks:

```

name: Scheduled OpenCode Task
on:
schedule:
- cron: "0 9 * * 1"# Every Monday at 9am UTC
jobs:
opencode:
runs-on: ubuntu-latest
permissions:
id-token: write
contents: write
pull-requests: write
issues: write
steps:
- name: Checkout repository
uses: actions/checkout@v6
with:
persist-credentials: false
- name: Run OpenCode
uses: anomalyco/opencode/github@latest
env:
ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
with:
model: anthropic/claude-sonnet-4-20250514
prompt: |
Review the codebase for any TODO comments and create a summary.
If you find issues worth addressing, open an issue to track them.
```

For scheduled events, the `prompt` input is **required** since there’s no comment to extract instructions from. Scheduled workflows run without a user context to permission-check, so the workflow must grant `contents: write` and `pull-requests: write` if you expect OpenCode to create branches or PRs.

* * *

### [Pull Request Example](#pull-request-example)

Automatically review PRs when they are opened or updated:

```

name: opencode-review
on:
pull_request:
types: [opened, synchronize, reopened, ready_for_review]
jobs:
review:
runs-on: ubuntu-latest
permissions:
id-token: write
contents: read
pull-requests: read
issues: read
steps:
- uses: actions/checkout@v6
with:
persist-credentials: false
- uses: anomalyco/opencode/github@latest
env:
ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
with:
model: anthropic/claude-sonnet-4-20250514
use_github_token: true
prompt: |
Review this pull request:
- Check for code quality issues
- Look for potential bugs
- Suggest improvements
```

For `pull_request` events, if no `prompt` is provided, OpenCode defaults to reviewing the pull request.

* * *

### [Issues Triage Example](#issues-triage-example)

Automatically triage new issues. This example filters to accounts older than 30 days to reduce spam:

```

name: Issue Triage
on:
issues:
types: [opened]
jobs:
triage:
runs-on: ubuntu-latest
permissions:
id-token: write
contents: write
pull-requests: write
issues: write
steps:
- name: Check account age
id: check
uses: actions/github-script@v7
with:
script: |
const user = await github.rest.users.getByUsername({
username: context.payload.issue.user.login
});
const created = new Date(user.data.created_at);
const days = (Date.now() - created) / (1000 * 60 * 60 * 24);
return days >= 30;
result-encoding: string
- uses: actions/checkout@v6
if: steps.check.outputs.result == 'true'
with:
persist-credentials: false
- uses: anomalyco/opencode/github@latest
if: steps.check.outputs.result == 'true'
env:
ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
with:
model: anthropic/claude-sonnet-4-20250514
prompt: |
Review this issue. If there's a clear fix or relevant docs:
- Provide documentation links
- Add error handling guidance for code examples
Otherwise, do not comment.
```

For `issues` events, the `prompt` input is **required** since there’s no comment to extract instructions from.

* * *

## [Custom prompts](#custom-prompts)

Override the default prompt to customize OpenCode’s behavior for your workflow.

```

- uses: anomalyco/opencode/github@latest
with:
model: anthropic/claude-sonnet-4-5
prompt: |
Review this pull request:
- Check for code quality issues
- Look for potential bugs
- Suggest improvements
```

This is useful for enforcing specific review criteria, coding standards, or focus areas relevant to your project.

* * *

## [Examples](#examples)

Here are some examples of how you can use OpenCode in GitHub.

- **Explain an issue**
  
  Add this comment in a GitHub issue.
  
  ```
  
  /opencode explain this issue
  ```
  
  OpenCode will read the entire thread, including all comments, and reply with a clear explanation.
- **Fix an issue**
  
  In a GitHub issue, say:
  
  And OpenCode will create a new branch, implement the changes, and open a PR with the changes.
- **Review PRs and make changes**
  
  Leave the following comment on a GitHub PR.
  
  ```
  
  Delete the attachment from S3 when the note is removed /oc
  ```
  
  OpenCode will implement the requested change and commit it to the same PR.
- **Review specific code lines**
  
  Leave a comment directly on code lines in the PR’s “Files” tab. OpenCode automatically detects the file, line numbers, and diff context to provide precise responses.
  
  ```
  
  [Comment on specific lines in Files tab]
  /oc add error handling here
  ```
  
  When commenting on specific lines, OpenCode receives:
  
  - The exact file being reviewed
  - The specific lines of code
  - The surrounding diff context
  - Line number information
  
  This allows for more targeted requests without needing to specify file paths or line numbers manually.