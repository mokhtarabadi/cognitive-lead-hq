# Gitlab

> Source: https://opencode.ai/docs/gitlab/

# GitLab

Use OpenCode in GitLab issues and merge requests.

OpenCode integrates with your GitLab workflow through your GitLab CI/CD pipeline or with GitLab Duo.

In both cases, OpenCode will run on your GitLab runners.

---

## GitLab CI

OpenCode works in a regular GitLab pipeline. You can build it into a pipeline as a CI component

Here we are using a community-created CI/CD component for OpenCode — nagyv/gitlab-opencode.

---

### Features

- **Use custom configuration per job**: Configure OpenCode with a custom configuration directory, for example ./config/#custom-directory to enable or disable functionality per OpenCode invocation.
- **Minimal setup**: The CI component sets up OpenCode in the background, you only need to create the OpenCode configuration and the initial prompt.
- **Flexible**: The CI component supports several inputs for customizing its behavior

---

### Setup

Store your OpenCode authentication JSON as a File type CI environment variables under **Settings** > **CI/CD** > **Variables**. Make sure to mark them as “Masked and hidden”.

Add the following to your .gitlab-ci.yml file.

```
include:  - component: $CI_SERVER_FQDN/nagyv/gitlab-opencode/opencode@2    inputs:      config_dir: ${CI_PROJECT_DIR}/opencode-config      auth_json: $OPENCODE_AUTH_JSON # The variable name for your OpenCode authentication JSON      command: optional-custom-command      message: "Your prompt here"
```

- .gitlab-ci.yml

For more inputs and use cases check out the docs for this component.

---

## GitLab Duo

OpenCode integrates with your GitLab workflow.
Mention @opencode in a comment, and OpenCode will execute tasks within your GitLab CI pipeline.

---

### Features

- **Triage issues**: Ask OpenCode to look into an issue and explain it to you.
- **Fix and implement**: Ask OpenCode to fix an issue or implement a feature.
  It will create a new branch and raise a merge request with the changes.
- **Secure**: OpenCode runs on your GitLab runners.

---

### Setup

OpenCode runs in your GitLab CI/CD pipeline, here’s what you’ll need to set it up:

Tip

Check out the **GitLab docs** for up to date instructions.

Configure your GitLab environment

Set up CI/CD

Get an AI model provider API key

Create a service account

Configure CI/CD variables

Create a flow config file, here’s an example:

```
image: node:22-slimcommands:  - echo "Installing opencode"  - npm install --global opencode-ai  - echo "Installing glab"  - export GITLAB_TOKEN=$GITLAB_TOKEN_OPENCODE  - apt-get update --quiet && apt-get install --yes curl wget gpg git && rm --recursive --force /var/lib/apt/lists/*  - curl --silent --show-error --location "https://raw.githubusercontent.com/upciti/wakemeops/main/assets/install_repository" | bash  - apt-get install --yes glab  - echo "Configuring glab"  - echo $GITLAB_HOST  - echo "Creating OpenCode auth configuration"  - mkdir --parents ~/.local/share/opencode  - |    cat > ~/.local/share/opencode/auth.json << EOF    {      "anthropic": {        "type": "api",        "key": "$ANTHROPIC_API_KEY"      }    }    EOF  - echo "Configuring git"  - git config --global user.email "opencode@gitlab.com"  - git config --global user.name "OpenCode"  - echo "Testing glab"  - glab issue list  - echo "Running OpenCode"  - |    opencode run "    You are an AI assistant helping with GitLab operations.
    Context: $AI_FLOW_CONTEXT    Task: $AI_FLOW_INPUT    Event: $AI_FLOW_EVENT
    Please execute the requested task using the available GitLab tools.    Be thorough in your analysis and provide clear explanations.
    <important>    Please use the glab CLI to access data from GitLab. The glab CLI has already been authenticated. You can run the corresponding commands.
    If you are asked to summarize an MR or issue or asked to provide more information then please post back a note to the MR/Issue so that the user can see it.    You don't need to commit or push up changes, those will be done automatically based on the file changes you make.    </important>    "  - git checkout --branch $CI_WORKLOAD_REF origin/$CI_WORKLOAD_REF  - echo "Checking for git changes and pushing if any exist"  - |    if ! git diff --quiet || ! git diff --cached --quiet || [ --not --zero "$(git ls-files --others --exclude-standard)" ]; then      echo "Git changes detected, adding and pushing..."      git add .      if git diff --cached --quiet; then        echo "No staged changes to commit"      else        echo "Committing changes to branch: $CI_WORKLOAD_REF"        git commit --message "Codex changes"        echo "Pushing changes up to $CI_WORKLOAD_REF"        git push https://gitlab-ci-token:$GITLAB_TOKEN@$GITLAB_HOST/gl-demo-ultimate-dev-ai-epic-17570/test-java-project.git $CI_WORKLOAD_REF        echo "Changes successfully pushed"      fi    else      echo "No git changes detected, skipping push"    fivariables:  - ANTHROPIC_API_KEY  - GITLAB_TOKEN_OPENCODE  - GITLAB_HOST
```

- Flow configuration

You can refer to the GitLab CLI agents docs for detailed instructions.

---

### Examples

Here are some examples of how you can use OpenCode in GitLab.

Tip

You can configure to use a different trigger phrase than @opencode.

**Explain an issue**

Add this comment in a GitLab issue.

```
@opencode explain this issue
```

OpenCode will read the issue and reply with a clear explanation.

**Fix an issue**

In a GitLab issue, say:

```
@opencode fix this
```

OpenCode will create a new branch, implement the changes, and open a merge request with the changes.

**Review merge requests**

Leave the following comment on a GitLab merge request.

```
@opencode review this merge request
```

OpenCode will review the merge request and provide feedback.

Edit pageFound a bug? Open an issueJoin our Discord communitySelect languageEnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文© Anomaly

Last updated: Jul 14, 2026
