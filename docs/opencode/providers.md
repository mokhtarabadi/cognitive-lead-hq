# Providers

> Source: https://opencode.ai/docs/providers/

# Providers

Using any LLM provider in OpenCode.

OpenCode uses the AI SDK and Models.dev to support **75+ LLM providers** and it supports running local models.

To add a provider you need to:

- Add the API keys for the provider using the /connect command.
- Configure the provider in your OpenCode config.

---

### Credentials

When you add a provider’s API keys with the /connect command, they are stored
in ~/.local/share/opencode/auth.json.

---

### Config

You can customize the providers through the provider section in your OpenCode
config.

---

#### Base URL

You can customize the base URL for any provider by setting the baseURL option. This is useful when using proxy services or custom endpoints.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "anthropic": {      "options": {        "baseURL": "https://api.anthropic.com/v1"      }    }  }}
```

---

#### Hiding models

You can hide specific models from the /models picker for a provider using the blacklist option. This is useful when a provider exposes models you don’t want to use or select.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "anthropic": {      "blacklist": ["claude-opus-4-20250514"]    }  }}
```

The inverse whitelist option hides every model except the ones listed.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "anthropic": {      "whitelist": ["claude-sonnet-4-20250514"]    }  }}
```

Both options take an array of model IDs — the same IDs shown in the /models picker.

- blacklist removes the listed models from the picker.
- whitelist keeps only the listed models and hides the rest.
- You can combine them: whitelist narrows the set, then blacklist removes entries from it.

---

## OpenCode Zen

OpenCode Zen is a list of models provided by the OpenCode team that have been
tested and verified to work well with OpenCode. Learn more.

Tip

If you are new, we recommend starting with OpenCode Zen.

Run the /connect command in the TUI, select OpenCode Zen, and head to opencode.ai/auth.

```
/connect
```

Sign in, add your billing details, and copy your API key.

Paste your API key.

```
┌ API key││└ enter
```

Run /models in the TUI to see the list of models we recommend.

```
/models
```

It works like any other provider in OpenCode and is completely optional to use.

---

## OpenCode Go

OpenCode Go is a low cost subscription plan that provides reliable access to popular open coding models provided by the OpenCode team that have been
tested and verified to work well with OpenCode.

Run the /connect command in the TUI, select OpenCode Go, and head to opencode.ai/auth.

```
/connect
```

Sign in, add your billing details, and copy your API key.

Paste your API key.

```
┌ API key││└ enter
```

Run /models in the TUI to see the list of models we recommend.

```
/models
```

It works like any other provider in OpenCode and is completely optional to use.

---

## Directory

Let’s look at some of the providers in detail. If you’d like to add a provider to the
list, feel free to open a PR.

Note

Don’t see a provider here? Submit a PR.

---

### 302.AI

Head over to the 302.AI console, create an account, and generate an API key.

Run the /connect command and search for **302.AI**.

```
/connect
```

Enter your 302.AI API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

---

### Amazon Bedrock

To use Amazon Bedrock with OpenCode:

Head over to the **Model catalog** in the Amazon Bedrock console and request
access to the models you want.

Tip

You need to have access to the model you want in Amazon Bedrock.

**Configure authentication** using one of the following methods:

---

#### Environment Variables (Quick Start)

Set one of these environment variables while running opencode:

```
# Option 1: Using AWS access keysAWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=YYY opencode
# Option 2: Using named AWS profileAWS_PROFILE=my-profile opencode
# Option 3: Using Bedrock bearer tokenAWS_BEARER_TOKEN_BEDROCK=XXX opencode
```

Terminal windowOr add them to your bash profile:

```
export AWS_PROFILE=my-dev-profileexport AWS_REGION=us-east-1
```

~/.bash_profile
---

#### Configuration File (Recommended)

For project-specific or persistent configuration, use opencode.json:

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "amazon-bedrock": {      "options": {        "region": "us-east-1",        "profile": "my-aws-profile"      }    }  }}
```

opencode.json**Available options:**

- region - AWS region (e.g., us-east-1, eu-west-1)
- profile - AWS named profile from ~/.aws/credentials
- endpoint - Custom endpoint URL for VPC endpoints (alias for generic baseURL option)

Tip

Configuration file options take precedence over environment variables.

---

#### Advanced: VPC Endpoints

If you’re using VPC endpoints for Bedrock:

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "amazon-bedrock": {      "options": {        "region": "us-east-1",        "profile": "production",        "endpoint": "https://bedrock-runtime.us-east-1.vpce-xxxxx.amazonaws.com"      }    }  }}
```

Note

The endpoint option is an alias for the generic baseURL option, using AWS-specific terminology. If both endpoint and baseURL are specified, endpoint takes precedence.

---

#### Authentication Methods

- **AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY**: Create an IAM user and generate access keys in the AWS Console
- **AWS_PROFILE**: Use named profiles from ~/.aws/credentials. First configure with aws configure --profile my-profile or aws sso login
- **AWS_BEARER_TOKEN_BEDROCK**: Generate long-term API keys from the Amazon Bedrock console
- **AWS_WEB_IDENTITY_TOKEN_FILE / AWS_ROLE_ARN**: For EKS IRSA (IAM Roles for Service Accounts) or other Kubernetes environments with OIDC federation. These environment variables are automatically injected by Kubernetes when using service account annotations.

---

#### Authentication Precedence

Amazon Bedrock uses the following authentication priority:

- **Bearer Token** - AWS_BEARER_TOKEN_BEDROCK environment variable or token from /connect command
- **AWS Credential Chain** - Profile, access keys, shared credentials, IAM roles, Web Identity Tokens (EKS IRSA), instance metadata

Note

When a bearer token is set (via /connect or AWS_BEARER_TOKEN_BEDROCK), it takes precedence over all AWS credential methods including configured profiles.

Run the /models command to select the model you want.

```
/models
```

Note

For custom inference profiles, use the model and provider name in the key and set the id property to the arn. This ensures correct caching.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "amazon-bedrock": {      // ...      "models": {        "anthropic-claude-sonnet-4.5": {          "id": "arn:aws:bedrock:us-east-1:xxx:application-inference-profile/yyy"        }      }    }  }}
```

---

### Anthropic

Once you’ve signed up, run the /connect command and select Anthropic.

```
/connect
```

Here you can select the **Claude Pro/Max** option and it’ll open your browser
and ask you to authenticate.

```
┌ Select auth method││ Manually enter API Key└
```

Now all the Anthropic models should be available when you use the /models command.

```
/models
```

There are plugins that allow you to use your Claude Pro/Max models with
OpenCode. Anthropic explicitly prohibits this.

Previous versions of OpenCode came bundled with these plugins but that is no
longer the case as of 1.3.0

Other companies support freedom of choice with developer tooling - you can use
the following subscriptions in OpenCode with zero setup:

- ChatGPT Plus
- Github Copilot
- Gitlab Duo

---

### Atomic Chat

You can configure opencode to use local models through Atomic Chat, a desktop application that runs local LLMs behind an OpenAI-compatible API server (default endpoint http://127.0.0.1:1337/v1).

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "atomic-chat": {      "npm": "@ai-sdk/openai-compatible",      "name": "Atomic Chat (local)",      "options": {        "baseURL": "http://127.0.0.1:1337/v1"      },      "models": {        "<your-model-id>": {          "name": "<your-model-name>"        }      }    }  }}
```

In this example:

- atomic-chat is the custom provider ID. This can be any string you want.
- npm specifies the package to use for this provider. Here, @ai-sdk/openai-compatible is used for any OpenAI-compatible API.
- name is the display name for the provider in the UI.
- options.baseURL is the endpoint for the local server. Change the host and port to match your Atomic Chat setup.
- models is a map of model IDs to their display names. Each ID must match the id returned by GET /v1/models — run curl http://127.0.0.1:1337/v1/models to list the ids currently loaded in Atomic Chat.

Tip

If tool calls aren’t working well, pick a loaded model with strong tool-calling support (for example, a Qwen-Coder or DeepSeek-Coder variant).

---

### Azure OpenAI

Note

If you encounter “I’m sorry, but I cannot assist with that request” errors, try changing the content filter from **DefaultV2** to **Default** in your Azure resource.

Head over to the Azure portal and create an **Azure OpenAI** resource. You’ll need:

- **Resource name**: This becomes part of your API endpoint (https://RESOURCE_NAME.openai.azure.com/)
- **API key**: Either KEY 1 or KEY 2 from your resource

Go to Azure AI Foundry and deploy a model.

Note

The deployment name must match the model name for opencode to work properly.

Run the /connect command and search for **Azure**.

```
/connect
```

Enter your API key.

```
┌ API key││└ enter
```

Set your resource name as an environment variable:

```
AZURE_RESOURCE_NAME=XXX opencode
```

Terminal windowOr add it to your bash profile:

```
export AZURE_RESOURCE_NAME=XXX
```

- ~/.bash_profile

Run the /models command to select your deployed model.

```
/models
```

---

### Azure Cognitive Services

Head over to the Azure portal and create an **Azure OpenAI** resource. You’ll need:

- **Resource name**: This becomes part of your API endpoint (https://AZURE_COGNITIVE_SERVICES_RESOURCE_NAME.cognitiveservices.azure.com/)
- **API key**: Either KEY 1 or KEY 2 from your resource

Go to Azure AI Foundry and deploy a model.

Note

The deployment name must match the model name for opencode to work properly.

Run the /connect command and search for **Azure Cognitive Services**.

```
/connect
```

Enter your API key.

```
┌ API key││└ enter
```

Set your resource name as an environment variable:

```
AZURE_COGNITIVE_SERVICES_RESOURCE_NAME=XXX opencode
```

Terminal windowOr add it to your bash profile:

```
export AZURE_COGNITIVE_SERVICES_RESOURCE_NAME=XXX
```

- ~/.bash_profile

Run the /models command to select your deployed model.

```
/models
```

---

### Baseten

Head over to the Baseten, create an account, and generate an API key.

Run the /connect command and search for **Baseten**.

```
/connect
```

Enter your Baseten API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

---

### Cerebras

Head over to the Cerebras console, create an account, and generate an API key.

Run the /connect command and search for **Cerebras**.

```
/connect
```

Enter your Cerebras API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Qwen 3 Coder 480B_.

```
/models
```

---

### Cloudflare AI Gateway

Cloudflare AI Gateway lets you access models from OpenAI, Anthropic, Workers AI, and more through a unified endpoint. With Unified Billing you don’t need separate API keys for each provider.

Head over to the Cloudflare dashboard, navigate to **AI** > **AI Gateway**, and create a new gateway. Note your **Account ID** and **Gateway ID**.

Run the /connect command and search for **Cloudflare AI Gateway**.

```
/connect
```

Enter your **Account ID** when prompted.

```
┌ Enter your Cloudflare Account ID││└ enter
```

Enter your **Gateway ID** when prompted.

```
┌ Enter your Cloudflare AI Gateway ID││└ enter
```

Enter your **Cloudflare API token**.

```
┌ Gateway API token││└ enter
```

Run the /models command to select a model.

```
/models
```

You can also add models through your opencode config.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "cloudflare-ai-gateway": {      "models": {        "openai/gpt-4o": {},        "anthropic/claude-sonnet-4": {}      }    }  }}
```

opencode.jsonAlternatively, you can set environment variables instead of using /connect.

```
export CLOUDFLARE_ACCOUNT_ID=your-32-character-account-idexport CLOUDFLARE_GATEWAY_ID=your-gateway-idexport CLOUDFLARE_API_TOKEN=your-api-token
```

- ~/.bash_profile

---

### Cloudflare Workers AI

Cloudflare Workers AI lets you run AI models on Cloudflare’s global network directly via REST API, with no separate provider accounts needed for supported models.

Head over to the Cloudflare dashboard, navigate to **Workers AI**, and select **Use REST API** to get your **Account ID** and create an API token.

Run the /connect command and search for **Cloudflare Workers AI**.

```
/connect
```

Enter your **Account ID** when prompted.

```
┌ Enter your Cloudflare Account ID││└ enter
```

Enter your **Cloudflare API key**.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

Alternatively, you can set environment variables instead of using /connect.

```
export CLOUDFLARE_ACCOUNT_ID=your-32-character-account-idexport CLOUDFLARE_API_KEY=your-api-token
```

- ~/.bash_profile

---

### Cortecs

Head over to the Cortecs console, create an account, and generate an API key.

Run the /connect command and search for **Cortecs**.

```
/connect
```

Enter your Cortecs API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Kimi K2 Instruct_.

```
/models
```

---

### DeepSeek

Head over to the DeepSeek console, create an account, and click **Create new API key**.

Run the /connect command and search for **DeepSeek**.

```
/connect
```

Enter your DeepSeek API key.

```
┌ API key││└ enter
```

Run the /models command to select a DeepSeek model like _DeepSeek V4 Pro_.

```
/models
```

---

### Deep Infra

Head over to the Deep Infra dashboard, create an account, and generate an API key.

Run the /connect command and search for **Deep Infra**.

```
/connect
```

Enter your Deep Infra API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

---

### DigitalOcean

DigitalOcean’s Inference Engine provides access to open models like GPT-OSS, Llama, Qwen, and DeepSeek, plus custom Inference Routers that route each request to the cheapest, fastest, or best-fit model for a task.

OpenCode supports two authentication methods:

- **OAuth (Recommended)** — Sign in to your DigitalOcean account; OpenCode uses your DigitalOcean API token directly for inference and discovers your Inference Routers.
- **Model Access Key** — Paste an existing key from the DigitalOcean console.

#### OAuth (Recommended)

Run the /connect command and search for **DigitalOcean**.

```
/connect
```

Select **Login with DigitalOcean**.

```
┌ Select auth method││ Login with DigitalOcean│ Paste Model Access Key└
```

Your browser opens to authorize OpenCode. Sign in and approve.

Note

OpenCode requests genai:read and inference:query OAuth scopes. Your DigitalOcean API token is used directly for inference — no separate Model Access Key is created.

Note

Inference Routers only appear in the model picker after OAuth. Pasting a Model Access Key manually does not discover routers.

Run the /models command. Your Inference Routers appear as the format router: in the model selection.

```
/models
```

To pick up newly created Inference Routers, re-run /connect and select **DigitalOcean** again.

#### Using a Model Access Key

If you’d rather paste a key directly:

Head over to the **Manage** page in the Inference section of the DigitalOcean console and create a new key.

Run the /connect command and select **DigitalOcean**, then **Paste Model Access Key**.

```
┌ Enter your DigitalOcean Model Access Key││└ enter
```

Note

Inference Routers are not auto-discovered with this method. To surface them in the model picker, sign in via OAuth instead.

Run the /models command to select a model.

```
/models
```

#### Environment Variable

Alternatively, set your Model Access Key as an environment variable.

```
export DIGITALOCEAN_ACCESS_TOKEN=your-model-access-key
```

#### Inference Routers

Inference Routers let you define a routing policy across multiple models — picking the cheapest, fastest, or most appropriate model per request based on the task. After OAuth, OpenCode surfaces each router as router:<router-name> in the model picker.

Selecting a router model is a drop-in replacement for any other model — OpenCode forwards your request and DigitalOcean picks the underlying model based on your router’s policy. Learn more about Inference Routers

---

### FrogBot

Head over to the FrogBot dashboard, create an account, and generate an API key.

Run the /connect command and search for **FrogBot**.

```
/connect
```

Enter your FrogBot API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

---

### Fireworks AI

Head over to the Fireworks AI console, create an account, and click **Create API Key**.

Run the /connect command and search for **Fireworks AI**.

```
/connect
```

Enter your Fireworks AI API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Kimi K2 Instruct_.

```
/models
```

---

### GitLab Duo

Experimental

GitLab Duo support in OpenCode is experimental. Features, configuration, and
behavior may change in future releases.

OpenCode integrates with the GitLab Duo Agent Platform,
providing AI-powered agentic chat with native tool calling capabilities.

License requirements

GitLab Duo Agent Platform requires a **Premium** or **Ultimate** GitLab
subscription. It is available on GitLab.com and GitLab Self-Managed.
See GitLab Duo Agent Platform prerequisites
for full requirements.

Run the /connect command and select GitLab.

```
/connect
```

Choose your authentication method:

```
┌ Select auth method││ OAuth (Recommended)│ Personal Access Token└
```

#### Using OAuth (Recommended)

Select **OAuth** and your browser will open for authorization.

#### Using Personal Access Token

- Go to GitLab User Settings > Access Tokens
- Click **Add new token**
- Name: OpenCode, Scopes: api
- Copy the token (starts with glpat-)
- Enter it in the terminal

Run the /models command to see available models.

```
/models
```

Three Claude-based models are available:

- **duo-chat-haiku-4-5** (Default) - Fast responses for quick tasks
- **duo-chat-sonnet-4-5** - Balanced performance for most workflows
- **duo-chat-opus-4-5** - Most capable for complex analysis

Note

You can also specify ‘GITLAB_TOKEN’ environment variable if you don’t want
to store token in opencode auth storage.

Self-Hosted GitLabcompliance note

OpenCode uses a small model for some AI tasks like generating the session title.
It is configured to use gpt-5-nano by default, hosted by Zen. To lock OpenCode
to only use your own GitLab-hosted instance, add the following to your
opencode.json file. It is also recommended to disable session sharing.

```
{  "$schema": "https://opencode.ai/config.json",  "small_model": "gitlab/duo-chat-haiku-4-5",  "share": "disabled"}
```

For self-hosted GitLab instances:

```
export GITLAB_INSTANCE_URL=https://gitlab.company.comexport GITLAB_TOKEN=glpat-...
```

If your instance runs a custom AI Gateway:

```
GITLAB_AI_GATEWAY_URL=https://ai-gateway.company.com
```

Or add to your bash profile:

```
export GITLAB_INSTANCE_URL=https://gitlab.company.comexport GITLAB_AI_GATEWAY_URL=https://ai-gateway.company.comexport GITLAB_TOKEN=glpat-...
```

Note

Your GitLab administrator must:

- Turn on GitLab Duo
  for the user, group, or instance
- Turn on the Agent Platform
  (GitLab 18.8+) or enable beta and experimental features
  (GitLab 18.7 and earlier)
- For Self-Managed, configure your instance

OAuth for Self-Hosted instancesIn order to make Oauth working for your self-hosted instance, you need to create
a new application (Settings → Applications) with the
callback URL http://127.0.0.1:8080/callback and following scopes:

- api (Access the API on your behalf)
- read_user (Read your personal information)
- read_repository (Allows read-only access to the repository)

Then expose application ID as environment variable:

```
export GITLAB_OAUTH_CLIENT_ID=your_application_id_here
```

More documentation on opencode-gitlab-auth homepage.

ConfigurationCustomize through opencode.json:

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "gitlab": {      "options": {        "instanceUrl": "https://gitlab.com"      }    }  }}
```

GitLab Duo Agent Platform (DAP) Workflow ModelsDAP workflow models provide an alternative execution path that routes tool calls
through GitLab’s Duo Workflow Service (DWS) instead of the standard agentic chat.
When a duo-workflow-* model is selected, OpenCode will:

- Discover available models from your GitLab namespace
- Present a selection picker if multiple models are available
- Cache the selected model to disk for fast subsequent startups
- Route tool execution requests through OpenCode’s permission-gated tool system

Available DAP workflow models follow the duo-workflow-* naming convention and
are dynamically discovered from your GitLab instance.

GitLab API Tools (Optional, but highly recommended)To access GitLab tools (merge requests, issues, pipelines, CI/CD, etc.):

```
{  "$schema": "https://opencode.ai/config.json",  "plugin": ["opencode-gitlab-plugin"]}
```

This plugin provides comprehensive GitLab repository management capabilities including MR reviews, issue tracking, pipeline monitoring, and more.

---

### GitHub Copilot

To use your GitHub Copilot subscription with opencode:

Note

Some models might need a Pro+
subscription to use.

Run the /connect command and search for GitHub Copilot.

```
/connect
```

Navigate to github.com/login/device and enter the code.

```
┌ Login with GitHub Copilot││ https://github.com/login/device││ Enter code: 8F43-6FCF│└ Waiting for authorization...
```

Now run the /models command to select the model you want.

```
/models
```

---

### GMI Cloud

To use GMI Cloud with OpenCode:

Head over to the GMI Cloud console to create an API key. You can also review the API reference for the endpoint details.

Run the /connect command and search for **GMI Cloud**.

```
/connect
```

Enter your GMI Cloud API key.

```
┌ API key││└ enter
```

Run the /models command to select the model you want.

```
/models
```

---

### Google Vertex AI

To use Google Vertex AI with OpenCode:

Head over to the **Model Garden** in the Google Cloud Console and check the
models available in your region.

Note

You need to have a Google Cloud project with Vertex AI API enabled.

Set the required environment variables:

- GOOGLE_CLOUD_PROJECT: Your Google Cloud project ID
- VERTEX_LOCATION (optional): The region for Vertex AI (defaults to global)

- Authentication (choose one):
  GOOGLE_APPLICATION_CREDENTIALS: Path to your service account JSON key file
- Authenticate using gcloud CLI: gcloud auth application-default login

Set them while running opencode.

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json GOOGLE_CLOUD_PROJECT=your-project-id opencode
```

Or add them to your bash profile.

```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.jsonexport GOOGLE_CLOUD_PROJECT=your-project-idexport VERTEX_LOCATION=global
```

Tip

The global region improves availability and reduces errors at no extra cost. Use regional endpoints (e.g., us-central1) for data residency requirements. Learn more

Run the /models command to select the model you want.

```
/models
```

---

### Groq

Head over to the Groq console, click **Create API Key**, and copy the key.

Run the /connect command and search for Groq.

```
/connect
```

Enter the API key for the provider.

```
┌ API key││└ enter
```

Run the /models command to select the one you want.

```
/models
```

---

### Hugging Face

Hugging Face Inference Providers provides access to open models supported by 17+ providers.

Head over to Hugging Face settings to create a token with permission to make calls to Inference Providers.

Run the /connect command and search for **Hugging Face**.

```
/connect
```

Enter your Hugging Face token.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Kimi-K2-Instruct_ or _GLM-4.6_.

```
/models
```

---

### Helicone

Helicone is an LLM observability platform that provides logging, monitoring, and analytics for your AI applications. The Helicone AI Gateway routes your requests to the appropriate provider automatically based on the model.

Head over to Helicone, create an account, and generate an API key from your dashboard.

Run the /connect command and search for **Helicone**.

```
/connect
```

Enter your Helicone API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

For more providers and advanced features like caching and rate limiting, check the Helicone documentation.

#### Optional Configs

In the event you see a feature or model from Helicone that isn’t configured automatically through opencode, you can always configure it yourself.

Here’s Helicone’s Model Directory, you’ll need this to grab the IDs of the models you want to add.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "helicone": {      "npm": "@ai-sdk/openai-compatible",      "name": "Helicone",      "options": {        "baseURL": "https://ai-gateway.helicone.ai",      },      "models": {        "gpt-4o": {          // Model ID (from Helicone's model directory page)          "name": "GPT-4o", // Your own custom name for the model        },        "claude-sonnet-4-20250514": {          "name": "Claude Sonnet 4",        },      },    },  },}
```

#### Custom Headers

Helicone supports custom headers for features like caching, user tracking, and session management. Add them to your provider config using options.headers:

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "helicone": {      "npm": "@ai-sdk/openai-compatible",      "name": "Helicone",      "options": {        "baseURL": "https://ai-gateway.helicone.ai",        "headers": {          "Helicone-Cache-Enabled": "true",          "Helicone-User-Id": "opencode",        },      },    },  },}
```

Session trackingHelicone’s Sessions feature lets you group related LLM requests together. Use the opencode-helicone-session plugin to automatically log each OpenCode conversation as a session in Helicone.

```
npm install -g opencode-helicone-session
```

Add it to your config.

```
{  "plugin": ["opencode-helicone-session"]}
```

The plugin injects Helicone-Session-Id and Helicone-Session-Name headers into your requests. In Helicone’s Sessions page, you’ll see each OpenCode conversation listed as a separate session.

| Header | Description |
| ------ | ----------- |

| Helicone-Cache-Enabled | Enable response caching (true/false) |
| ---------------------- | ------------------------------------ |

| Helicone-User-Id | Track metrics by user |
| ---------------- | --------------------- |

| Helicone-Property-[Name] | Add custom properties (e.g., Helicone-Property-Environment) |
| ------------------------ | ----------------------------------------------------------- |

| Helicone-Prompt-Id | Associate requests with prompt versions |
| ------------------ | --------------------------------------- |

Common Helicone headersSee the Helicone Header Directory for all available headers.

---

### llama.cpp

You can configure opencode to use local models through llama.cpp’s llama-server utility

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "llama.cpp": {      "npm": "@ai-sdk/openai-compatible",      "name": "llama-server (local)",      "options": {        "baseURL": "http://127.0.0.1:8080/v1"      },      "models": {        "qwen3-coder:a3b": {          "name": "Qwen3-Coder: a3b-30b (local)",          "limit": {            "context": 128000,            "output": 65536          }        }      }    }  }}
```

In this example:

- llama.cpp is the custom provider ID. This can be any string you want.
- npm specifies the package to use for this provider. Here, @ai-sdk/openai-compatible is used for any OpenAI-compatible API.
- name is the display name for the provider in the UI.
- options.baseURL is the endpoint for the local server.
- models is a map of model IDs to their configurations. The model name will be displayed in the model selection list.

---

### IO.NET

IO.NET offers 17 models optimized for various use cases:

Head over to the IO.NET console, create an account, and generate an API key.

Run the /connect command and search for **IO.NET**.

```
/connect
```

Enter your IO.NET API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

---

### LM Studio

You can configure opencode to use local models through LM Studio.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "lmstudio": {      "npm": "@ai-sdk/openai-compatible",      "name": "LM Studio (local)",      "options": {        "baseURL": "http://127.0.0.1:1234/v1"      },      "models": {        "google/gemma-3n-e4b": {          "name": "Gemma 3n-e4b (local)"        }      }    }  }}
```

In this example:

- lmstudio is the custom provider ID. This can be any string you want.
- npm specifies the package to use for this provider. Here, @ai-sdk/openai-compatible is used for any OpenAI-compatible API.
- name is the display name for the provider in the UI.
- options.baseURL is the endpoint for the local server.
- models is a map of model IDs to their configurations. The model name will be displayed in the model selection list.

---

### Moonshot AI

To use Kimi K2 from Moonshot AI:

Head over to the Moonshot AI console, create an account, and click **Create API key**.

Run the /connect command and search for **Moonshot AI**.

```
/connect
```

Enter your Moonshot API key.

```
┌ API key││└ enter
```

Run the /models command to select _Kimi K2_.

```
/models
```

---

### MiniMax

Head over to the MiniMax API Console, create an account, and generate an API key.

Run the /connect command and search for **MiniMax**.

```
/connect
```

Enter your MiniMax API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _M2.1_.

```
/models
```

---

### NVIDIA

NVIDIA provides access to Nemotron models and many other open models through build.nvidia.com for free.

Head over to build.nvidia.com, create an account, and generate an API key.

Run the /connect command and search for **NVIDIA**.

```
/connect
```

Enter your NVIDIA API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like nemotron-3-super-120b-a12b.

```
/models
```

#### On-Prem / NIM

You can also use NVIDIA models locally via NVIDIA NIM by setting a custom base URL.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "nvidia": {      "options": {        "baseURL": "http://localhost:8000/v1"      }    }  }}
```

#### Environment Variable

Alternatively, set your API key as an environment variable.

```
export NVIDIA_API_KEY=nvapi-your-key-here
```

---

### Nebius Token Factory

Head over to the Nebius Token Factory console, create an account, and click **Add Key**.

Run the /connect command and search for **Nebius Token Factory**.

```
/connect
```

Enter your Nebius Token Factory API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Kimi K2 Instruct_.

```
/models
```

---

### Ollama

You can configure opencode to use local models through Ollama.

Tip

Ollama can automatically configure itself for OpenCode. See the Ollama integration docs for details.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "ollama": {      "npm": "@ai-sdk/openai-compatible",      "name": "Ollama (local)",      "options": {        "baseURL": "http://localhost:11434/v1"      },      "models": {        "llama2": {          "name": "Llama 2"        }      }    }  }}
```

In this example:

- ollama is the custom provider ID. This can be any string you want.
- npm specifies the package to use for this provider. Here, @ai-sdk/openai-compatible is used for any OpenAI-compatible API.
- name is the display name for the provider in the UI.
- options.baseURL is the endpoint for the local server.
- models is a map of model IDs to their configurations. The model name will be displayed in the model selection list.

Tip

If tool calls aren’t working, try increasing num_ctx in Ollama. Start around 16k - 32k.

---

### Ollama Cloud

To use Ollama Cloud with OpenCode:

Head over to https://ollama.com/ and sign in or create an account.

Navigate to **Settings** > **Keys** and click **Add API Key** to generate a new API key.

Copy the API key for use in OpenCode.

Run the /connect command and search for **Ollama Cloud**.

```
/connect
```

Enter your Ollama Cloud API key.

```
┌ API key││└ enter
```

**Important**: Before using cloud models in OpenCode, you must pull the model information locally:

```
ollama pull gpt-oss:20b-cloud
```

- Terminal window

Run the /models command to select your Ollama Cloud model.

```
/models
```

---

### OpenAI

We recommend signing up for ChatGPT Plus or Pro.

Once you’ve signed up, run the /connect command and select OpenAI.

```
/connect
```

Here you can select the **ChatGPT Plus/Pro** option and it’ll open your browser
and ask you to authenticate.

```
┌ Select auth method││ ChatGPT Plus/Pro│ Manually enter API Key└
```

Now all the OpenAI models should be available when you use the /models command.

```
/models
```

Using API keysIf you already have an API key, you can select **Manually enter API Key** and paste it in your terminal.

---

### OpenCode Zen

OpenCode Zen is a list of tested and verified models provided by the OpenCode team. Learn more.

Sign in to **OpenCode Zen** and click **Create API Key**.

Run the /connect command and search for **OpenCode Zen**.

```
/connect
```

Enter your OpenCode API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Qwen 3 Coder 480B_.

```
/models
```

---

### OpenRouter

Head over to the OpenRouter dashboard, click **Create API Key**, and copy the key.

Run the /connect command and search for OpenRouter.

```
/connect
```

Enter the API key for the provider.

```
┌ API key││└ enter
```

Many OpenRouter models are preloaded by default, run the /models command to select the one you want.

```
/models
```

You can also add additional models through your opencode config.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "openrouter": {      "models": {        "somecoolnewmodel": {}      }    }  }}
```

- opencode.json

You can also customize them through your opencode config. Here’s an example of specifying a provider

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "openrouter": {      "models": {        "moonshotai/kimi-k2": {          "options": {            "provider": {              "order": ["baseten"],              "allow_fallbacks": false            }          }        }      }    }  }}
```

- opencode.json

---

### LLM Gateway

Head over to the LLM Gateway dashboard, click **Create API Key**, and copy the key.

Run the /connect command and search for LLM Gateway.

```
/connect
```

Enter the API key for the provider.

```
┌ API key││└ enter
```

Many LLM Gateway models are preloaded by default, run the /models command to select the one you want.

```
/models
```

You can also add additional models through your opencode config.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "llmgateway": {      "models": {        "somecoolnewmodel": {}      }    }  }}
```

- opencode.json

You can also customize them through your opencode config. Here’s an example of specifying a provider

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "llmgateway": {      "models": {        "glm-4.7": {          "name": "GLM 4.7"        },        "gpt-5.2": {          "name": "GPT-5.2"        },        "gemini-2.5-pro": {          "name": "Gemini 2.5 Pro"        },        "claude-3-5-sonnet-20241022": {          "name": "Claude 3.5 Sonnet"        }      }    }  }}
```

- opencode.json

---

### SAP AI Core

SAP AI Core provides access to 40+ models from OpenAI, Anthropic, Google, Amazon, Meta, Mistral, and AI21 through a unified platform.

Go to your SAP BTP Cockpit, navigate to your SAP AI Core service instance, and create a service key.

Tip

The service key is a JSON object containing clientid, clientsecret, url, and serviceurls.AI_API_URL. You can find your AI Core instance under **Services** > **Instances and Subscriptions** in the BTP Cockpit.

Run the /connect command and search for **SAP AI Core**.

```
/connect
```

Enter your service key JSON.

```
┌ Service key││└ enter
```

Or set the AICORE_SERVICE_KEY environment variable:

```
AICORE_SERVICE_KEY='{"clientid":"...","clientsecret":"...","url":"...","serviceurls":{"AI_API_URL":"..."}}' opencode
```

Terminal windowOr add it to your bash profile:

```
export AICORE_SERVICE_KEY='{"clientid":"...","clientsecret":"...","url":"...","serviceurls":{"AI_API_URL":"..."}}'
```

- ~/.bash_profile

Optionally set deployment ID and resource group:

```
AICORE_DEPLOYMENT_ID=your-deployment-id AICORE_RESOURCE_GROUP=your-resource-group opencode
```

Terminal windowNote

These settings are optional and should be configured according to your SAP AI Core setup.

Run the /models command to select from 40+ available models.

```
/models
```

---

### STACKIT

STACKIT AI Model Serving provides fully managed sovereign hosting environment for AI models, focusing on LLMs like Llama, Mistral, and Qwen, with maximum data sovereignty on European infrastructure.

Head over to STACKIT Portal, navigate to **AI Model Serving**, and create an auth token for your project.

Tip

You need a STACKIT customer account, user account, and project before creating auth tokens.

Run the /connect command and search for **STACKIT**.

```
/connect
```

Enter your STACKIT AI Model Serving auth token.

```
┌ API key││└ enter
```

Run the /models command to select from available models like _Qwen3-VL 235B_ or _Llama 3.3 70B_.

```
/models
```

---

### OVHcloud AI Endpoints

Head over to the OVHcloud panel. Navigate to the Public Cloud section, AI & Machine Learning > AI Endpoints and in API Keys tab, click **Create a new API key**.

Run the /connect command and search for **OVHcloud AI Endpoints**.

```
/connect
```

Enter your OVHcloud AI Endpoints API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _gpt-oss-120b_.

```
/models
```

---

### Scaleway

To use Scaleway Generative APIs with Opencode:

Head over to the Scaleway Console IAM settings to generate a new API key.

Run the /connect command and search for **Scaleway**.

```
/connect
```

Enter your Scaleway API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _devstral-2-123b-instruct-2512_ or _gpt-oss-120b_.

```
/models
```

---

### Snowflake Cortex

Snowflake Cortex gives you access to frontier models (Claude, OpenAI GPT-5, and more) via an OpenAI-compatible API. All inference runs within the Snowflake perimeter and is billed in Snowflake credits. For per-model rates, see the Snowflake Service Consumption Table.

Don’t have a Snowflake account? Sign up for a free trial.

opencode’s core workflow for coding, editing files, and running commands relies on tool calling. Only the Claude and OpenAI families within Snowflake Cortex support this. The provider is limited to those families to support the core workflow.

OpenCode supports two authentication methods:

- **Browser OAuth (Recommended)** — sign in with your IdP/SSO; no secrets to manage, tokens refresh automatically.
- **Manual bearer token** — paste a PAT or JWT from the Snowflake console.

#### Browser OAuth (Recommended)

Run the /connect command and search for **Snowflake Cortex**.

```
/connect
```

Select **Login with Snowflake (External Browser)**.

```
┌ Select auth method││ Login with Snowflake (External Browser)│ Paste PAT or bearer token manually└
```

Enter your account identifier when prompted, for example myorg-myaccount or xy12345.us-east-1.

```
┌ Snowflake Account Identifier││└ enter
```

Optionally enter a Snowflake role to scope the session (e.g. SYSADMIN). Leave blank to use your default role.

Complete sign-in in the browser that opens. OpenCode captures the OAuth callback automatically and stores the token — no copy/paste needed.

Run the /models command to select a model.

```
/models
```

Note

Browser OAuth uses Snowflake’s built-in SNOWFLAKE$LOCAL_APPLICATION security integration (docs), which is rolling out to all accounts. To check availability in your account:

```
SHOW SECURITY INTEGRATIONS LIKE 'SNOWFLAKE$LOCAL_APPLICATION';
```

If the result is empty, use the **Manual bearer token** method below while the integration rolls out to your account.

#### Manual bearer token

If you prefer to paste a token directly, or if SNOWFLAKE$LOCAL_APPLICATION is not yet available in your account:

Generate a Programmatic Access Token (PAT) in your Snowflake account.

Run the /connect command, search for **Snowflake Cortex**, and select **Paste PAT or bearer token manually**.

Enter your account identifier when prompted.

Paste your PAT.

Run the /models command to select a model.

```
/models
```

#### Environment variable

For CI or headless environments, set a PAT or JWT before starting opencode:

```
export SNOWFLAKE_ACCOUNT=myorg-myaccountexport SNOWFLAKE_CORTEX_TOKEN=your-pat-or-jwt
```

Note

SNOWFLAKE_CORTEX_TOKEN accepts a PAT or JWT only — the browser OAuth flow is available via /connect only and cannot be configured through an environment variable. SNOWFLAKE_CORTEX_PAT is still supported for backward compatibility.

The model catalog is provided automatically. A minimal opencode.json is all that’s needed:

```
{  "$schema": "https://opencode.ai/config.json",  "model": "snowflake-cortex/claude-sonnet-4-6",  "small_model": "snowflake-cortex/claude-haiku-4-5"}
```

---

### Together AI

Head over to the Together AI console, create an account, and click **Add Key**.

Run the /connect command and search for **Together AI**.

```
/connect
```

Enter your Together AI API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Kimi K2 Instruct_.

```
/models
```

---

### Venice AI

Head over to the Venice AI console, create an account, and generate an API key.

Run the /connect command and search for **Venice AI**.

```
/connect
```

Enter your Venice AI API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Llama 3.3 70B_.

```
/models
```

---

### Vercel AI Gateway

Vercel AI Gateway lets you access models from OpenAI, Anthropic, Google, xAI, and more through a unified endpoint. Models are offered at list price with no markup.

Head over to the Vercel dashboard, navigate to the **AI Gateway** tab, and click **API keys** to create a new API key.

Run the /connect command and search for **Vercel AI Gateway**.

```
/connect
```

Enter your Vercel AI Gateway API key.

```
┌ API key││└ enter
```

Run the /models command to select a model.

```
/models
```

You can also customize models through your opencode config. Here’s an example of specifying provider routing order.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "vercel": {      "models": {        "anthropic/claude-sonnet-4": {          "options": {            "order": ["anthropic", "vertex"]          }        }      }    }  }}
```

Some useful routing options:

| Option | Description |
| ------ | ----------- |

| order | Provider sequence to try |
| ----- | ------------------------ |

| only | Restrict to specific providers |
| ---- | ------------------------------ |

| zeroDataRetention | Only use providers with zero data retention policies |
| ----------------- | ---------------------------------------------------- |

---

### xAI

Three ways to authenticate: a SuperGrok subscription via browser OAuth, the same SuperGrok subscription via a headless device-code flow (for VPS / SSH / Docker), or a pay-as-you-go API key from the xAI console.

#### Option A — SuperGrok OAuth (browser login)

Run the /connect command and search for **xAI**.

```
/connect
```

Select **xAI Grok OAuth (SuperGrok Subscription)**. OpenCode opens xAI’s consent screen in your browser and waits for the callback on http://127.0.0.1:56121/callback.

Run the /models command to select a Grok model.

```
/models
```

OpenCode refreshes the OAuth access token automatically. Any Grok or X Premium plan that includes Grok API access works; you do not need a separate XAI_API_KEY.

#### Option B — SuperGrok device-code (headless / remote server / VPS)

Use this when OpenCode is running somewhere a browser can’t reach the loopback redirect: a VPS, a remote dev box over SSH, inside Docker, in CI, etc. No callback port is opened on the host running OpenCode — instead xAI hands the CLI a short code that you type into a browser on any other device (laptop, phone, …).

Run the /connect command on the remote host and search for **xAI**.

```
/connect
```

Select **xAI Grok OAuth (Headless / Remote / VPS)**. OpenCode prints a verification URL and a short user code.

```
Open https://x.ai/device on any device and enter code: ABCD-1234
```

Open the URL on a device that has a browser (your laptop or phone), enter the code, and approve the consent screen. OpenCode polls xAI’s token endpoint and stores the resulting OAuth tokens once you approve. Token refresh works the same as Option A.

#### Option C — API key

Head over to the xAI console, create an account, and generate an API key.

Run the /connect command and search for **xAI**.

```
/connect
```

Select **Manually enter API Key** and paste your xAI API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _Grok Beta_.

```
/models
```

---

### Z.AI

Head over to the Z.AI API console, create an account, and click **Create a new API key**.

Run the /connect command and search for **Z.AI**.

```
/connect
```

If you are subscribed to the **GLM Coding Plan**, select **Z.AI Coding Plan**.

Enter your Z.AI API key.

```
┌ API key││└ enter
```

Run the /models command to select a model like _GLM-4.7_.

```
/models
```

---

### ZenMux

Head over to the ZenMux dashboard, click **Create API Key**, and copy the key.

Run the /connect command and search for ZenMux.

```
/connect
```

Enter the API key for the provider.

```
┌ API key││└ enter
```

Many ZenMux models are preloaded by default, run the /models command to select the one you want.

```
/models
```

You can also add additional models through your opencode config.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "zenmux": {      "models": {        "somecoolnewmodel": {}      }    }  }}
```

- opencode.json

---

## Custom provider

To add any **OpenAI-compatible** provider that’s not listed in the /connect command:

Tip

You can use any OpenAI-compatible provider with opencode. Most modern AI providers offer OpenAI-compatible APIs.

Run the /connect command and scroll down to **Other**.

```
$ /connect
┌  Add credential│◆  Select provider│  ...│  ● Other└
```

- Terminal window

Enter a unique ID for the provider.

```
$ /connect
┌  Add credential│◇  Enter provider id│  myprovider└
```

Terminal windowNote

Choose a memorable ID, you’ll use this in your config file.

Enter your API key for the provider.

```
$ /connect
┌  Add credential│▲  This only stores a credential for myprovider - you will need to configure it in opencode.json, check the docs for examples.│◇  Enter your API key│  sk-...└
```

- Terminal window

Create or update your opencode.json file in your project directory:

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "myprovider": {      "npm": "@ai-sdk/openai-compatible",      "name": "My AI ProviderDisplay Name",      "options": {        "baseURL": "https://api.myprovider.com/v1"      },      "models": {        "my-model-name": {          "name": "My Model Display Name"        }      }    }  }}
```

opencode.jsonHere are the configuration options:

- **npm**: AI SDK package to use, @ai-sdk/openai-compatible for OpenAI-compatible providers (for /v1/chat/completions). If your provider/model uses /v1/responses, use @ai-sdk/openai.
- **name**: Display name in UI.
- **models**: Available models.
- **options.baseURL**: API endpoint URL.
- **options.apiKey**: Optionally set the API key, if not using auth.
- **options.headers**: Optionally set custom headers.

More on the advanced options in the example below.

Run the /models command and your custom provider and models will appear in the selection list.

---

ExampleHere’s an example setting the apiKey, headers, and model limit options.

```
{  "$schema": "https://opencode.ai/config.json",  "provider": {    "myprovider": {      "npm": "@ai-sdk/openai-compatible",      "name": "My AI ProviderDisplay Name",      "options": {        "baseURL": "https://api.myprovider.com/v1",        "apiKey": "{env:ANTHROPIC_API_KEY}",        "headers": {          "Authorization": "Bearer custom-token"        }      },      "models": {        "my-model-name": {          "name": "My Model Display Name",          "limit": {            "context": 200000,            "output": 65536          }        }      }    }  }}
```

Configuration details:

- **apiKey**: Set using env variable syntax, learn more.
- **headers**: Custom headers sent with each request.
- **limit.context**: Maximum input tokens the model accepts.
- **limit.output**: Maximum tokens the model can generate.

The limit fields allow OpenCode to understand how much context you have left. Standard providers pull these from models.dev automatically.

---

## Troubleshooting

If you are having trouble with configuring a provider, check the following:

**Check the auth setup**: Run opencode auth list to see if the credentials
for the provider are added to your config.

This doesn’t apply to providers like Amazon Bedrock, that rely on environment variables for their auth.

For custom providers, check the opencode config and:

- Make sure the provider ID used in the /connect command matches the ID in your opencode config.
- The right npm package is used for the provider. For example, use @ai-sdk/cerebras for Cerebras. And for all other OpenAI-compatible providers, use @ai-sdk/openai-compatible (for /v1/chat/completions); if a model uses /v1/responses, use @ai-sdk/openai. For mixed setups under one provider, you can override per model via provider.npm.
- Check correct API endpoint is used in the options.baseURL field.

Edit pageFound a bug? Open an issueJoin our Discord communitySelect languageEnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文© Anomaly

Last updated: Jul 14, 2026
