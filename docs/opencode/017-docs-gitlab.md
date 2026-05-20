---
title: GitLab
url: https://opencode.ai/docs/gitlab/
source: crawler
fetched_at: 2026-02-14T12:04:45.407873-03:00
rendered_js: false
word_count: 374
summary: This document explains how to integrate OpenCode into GitLab workflows using CI/CD pipelines and GitLab Duo to automate tasks like issue triage and merge request reviews.
tags:
    - gitlab-ci
    - opencode
    - cicd-pipeline
    - gitlab-duo
    - workflow-automation
    - ai-integration
category: guide
---

OpenCode integrates with your GitLab workflow through your GitLab CI/CD pipeline or with GitLab Duo.

In both cases, OpenCode will run on your GitLab runners.

* * *

## [GitLab CI](#gitlab-ci)

OpenCode works in a regular GitLab pipeline. You can build it into a pipeline as a [CI component](https://docs.gitlab.com/ee/ci/components/)

Here we are using a community-created CI/CD component for OpenCode — [nagyv/gitlab-opencode](https://gitlab.com/nagyv/gitlab-opencode).

* * *

### [Features](#features)

- **Use custom configuration per job**: Configure OpenCode with a custom configuration directory, for example `./config/#custom-directory` to enable or disable functionality per OpenCode invocation.
- **Minimal setup**: The CI component sets up OpenCode in the background, you only need to create the OpenCode configuration and the initial prompt.
- **Flexible**: The CI component supports several inputs for customizing its behavior

* * *

### [Setup](#setup)

1. Store your OpenCode authentication JSON as a File type CI environment variables under **Settings** &gt; **CI/CD** &gt; **Variables**. Make sure to mark them as “Masked and hidden”.
2. Add the following to your `.gitlab-ci.yml` file.
   
   ```
   
   include:
   - component: $CI_SERVER_FQDN/nagyv/gitlab-opencode/opencode@2
   inputs:
   config_dir: ${CI_PROJECT_DIR}/opencode-config
   auth_json: $OPENCODE_AUTH_JSON# The variable name for your OpenCode authentication JSON
   command: optional-custom-command
   message: "Your prompt here"
   ```

For more inputs and use cases [check out the docs](https://gitlab.com/explore/catalog/nagyv/gitlab-opencode) for this component.

* * *

## [GitLab Duo](#gitlab-duo)

OpenCode integrates with your GitLab workflow. Mention `@opencode` in a comment, and OpenCode will execute tasks within your GitLab CI pipeline.

* * *

### [Features](#features-1)

- **Triage issues**: Ask OpenCode to look into an issue and explain it to you.
- **Fix and implement**: Ask OpenCode to fix an issue or implement a feature. It will create a new branch and raise a merge request with the changes.
- **Secure**: OpenCode runs on your GitLab runners.

* * *

### [Setup](#setup-1)

OpenCode runs in your GitLab CI/CD pipeline, here’s what you’ll need to set it up:

1. Configure your GitLab environment
2. Set up CI/CD
3. Get an AI model provider API key
4. Create a service account
5. Configure CI/CD variables
6. Create a flow config file, here’s an example:
   
   Flow configuration
   
   ```
   
   image: node:22-slim
   commands:
   - echo "Installing opencode"
   - npm install --global opencode-ai
   - echo "Installing glab"
   - export GITLAB_TOKEN=$GITLAB_TOKEN_OPENCODE
   - apt-get update --quiet && apt-get install --yes curl wget gpg git && rm --recursive --force /var/lib/apt/lists/*
   - curl --silent --show-error --location "https://raw.githubusercontent.com/upciti/wakemeops/main/assets/install_repository" | bash
   - apt-get install --yes glab
   - echo "Configuring glab"
   - echo $GITLAB_HOST
   - echo "Creating OpenCode auth configuration"
   - mkdir --parents ~/.local/share/opencode
   - |
   cat > ~/.local/share/opencode/auth.json << EOF
   {
   "anthropic": {
   "type": "api",
   "key": "$ANTHROPIC_API_KEY"
   }
   }
   EOF
   - echo "Configuring git"
   - git config --global user.email "opencode@gitlab.com"
   - git config --global user.name "OpenCode"
   - echo "Testing glab"
   - glab issue list
   - echo "Running OpenCode"
   - |
   opencode run "
   You are an AI assistant helping with GitLab operations.
   Context: $AI_FLOW_CONTEXT
   Task: $AI_FLOW_INPUT
   Event: $AI_FLOW_EVENT
   Please execute the requested task using the available GitLab tools.
   Be thorough in your analysis and provide clear explanations.
   <important>
   Please use the glab CLI to access data from GitLab. The glab CLI has already been authenticated. You can run the corresponding commands.
   If you are asked to summarize an MR or issue or asked to provide more information then please post back a note to the MR/Issue so that the user can see it.
   You don't need to commit or push up changes, those will be done automatically based on the file changes you make.
   </important>
   "
   - git checkout --branch $CI_WORKLOAD_REF origin/$CI_WORKLOAD_REF
   - echo "Checking for git changes and pushing if any exist"
   - |
   if ! git diff --quiet || ! git diff --cached --quiet || [ --not --zero "$(git ls-files --others --exclude-standard)" ]; then
   echo "Git changes detected, adding and pushing..."
   git add .
   if git diff --cached --quiet; then
   echo "No staged changes to commit"
   else
   echo "Committing changes to branch: $CI_WORKLOAD_REF"
   git commit --message "Codex changes"
   echo "Pushing changes up to $CI_WORKLOAD_REF"
   git push https://gitlab-ci-token:$GITLAB_TOKEN@$GITLAB_HOST/gl-demo-ultimate-dev-ai-epic-17570/test-java-project.git $CI_WORKLOAD_REF
   echo "Changes successfully pushed"
   fi
   else
   echo "No git changes detected, skipping push"
   fi
   variables:
   - ANTHROPIC_API_KEY
   - GITLAB_TOKEN_OPENCODE
   - GITLAB_HOST
   ```

You can refer to the [GitLab CLI agents docs](https://docs.gitlab.com/user/duo_agent_platform/agent_assistant/) for detailed instructions.

* * *

### [Examples](#examples)

Here are some examples of how you can use OpenCode in GitLab.

- **Explain an issue**
  
  Add this comment in a GitLab issue.
  
  ```
  
  @opencode explain this issue
  ```
  
  OpenCode will read the issue and reply with a clear explanation.
- **Fix an issue**
  
  In a GitLab issue, say:
  
  OpenCode will create a new branch, implement the changes, and open a merge request with the changes.
- **Review merge requests**
  
  Leave the following comment on a GitLab merge request.
  
  ```
  
  @opencode review this merge request
  ```
  
  OpenCode will review the merge request and provide feedback.