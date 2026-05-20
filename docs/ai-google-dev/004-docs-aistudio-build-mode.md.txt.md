---
title: Build apps in Google AI Studio
url: https://ai.google.dev/gemini-api/docs/aistudio-build-mode.md.txt
source: llms
fetched_at: 2026-04-29T11:16:13.160588-03:00
rendered_js: false
word_count: 1158
summary: This document provides an overview of using Google AI Studio's Build mode to develop and deploy full-stack applications using natural language prompts and the Gemini API.
tags:
    - google-ai-studio
    - gemini-api
    - full-stack-development
    - vibe-coding
    - ai-powered-coding
    - cloud-run
category: guide
optimized: true
optimized_at: '2026-04-29T14:29:00Z'
---
Use Google AI Studio to quickly build ("vibe code") and deploy apps testing the latest Gemini capabilities like [Nano Banana](https://ai.google.dev/gemini-api/docs/image-generation) and the [[003-docs-live-api-get-started-sdk.md.txt|Live API]]. Build mode supports **full-stack runtimes** — server-side logic, secure secrets management, and npm package support via natural language prompting.

## Get started

Start vibe coding in [Build mode](https://aistudio.google.com/apps):

- **Start with a prompt**: Enter a description of what to build. Use AI Chips to add features (image generation, Google Maps data). Speech-to-text is also available.
- **"I'm Feeling Lucky" button**: Get a creative spark — Gemini generates a project idea prompt.
- **Remix from the gallery**: Open a project from the [App Gallery](https://aistudio.google.com/apps?source=showcase) and select **Copy App**.

After running the prompt, code/files are generated with a live preview on the right.

## What is created?

Running your prompt creates a complete application:

- **Client-side**: web frontend (React by default).
- **Server-side**: Node.js runtime for secure API calls, database connections, and npm packages.

View generated code in the **Code** tab of the preview pane. The **Antigravity Agent** intelligently manages multi-file changes across your stack.

### The Antigravity Agent

The [Google Antigravity](https://antigravity.google) agent harness powers Build mode. It goes beyond simple code generation:

- **Context awareness**: maintains context of previous prompts and file states.
- **Multi-file management**: handles dependencies across multiple files.
- **Verified execution**: verifies code updates to reduce hallucinations.

## Full-stack capabilities

Build more than client-side prototypes:

- **Server-side runtime & npm**: use any npm package. The agent auto-installs packages as needed (data visualization, API clients). Request specific packages if desired.
- **Secrets management**: securely store API keys/secrets in **Settings**. Accessible server-side only — safe from client exposure.
- **Multiplayer**: build real-time collaborative experiences. Server runtime manages state and connections.
- **Firebase integration**: auto-provision Firebase (Firestore for persistent storage, Firebase Auth for "Sign in with Google"). Agent handles setup and writes the code.

[Learn more about developing full-stack apps](https://ai.google.dev/gemini-api/docs/aistudio-fullstack)

## Continue building

Refine your application after initial generation:

### Build in Google AI Studio

- **Iterate with Gemini**: use the chat panel to request modifications, new features, or styling changes.
- **Edit code directly**: open the **Code tab** for live edits.

### Develop externally

- **Download and develop locally**: export as a **ZIP file**, import into your editor.
- **Push to GitHub**: integrate with existing development/deployment workflows.

## Key features

- **Create and iterate on full-stack apps**: build with just a prompt; iterate via chat or **annotation mode** (highlight any UI element and describe the change).
- **Share and deploy**: share creations for collaboration/showcase, then deploy to Cloud Run when ready.
- **App gallery**: browse project ideas, preview applications instantly, remix to make your own.

## Deploy or archive your app

- **Google Cloud Run**: deploy as a scalable service. [Google Cloud Run](https://cloud.google.com/run) pricing may apply based on usage.
- **GitHub**: export to a GitHub repository.

## Limitations

### API Key security

> [!warning]
> - **Client-side**: never use real API keys directly in client-side code.
> - **Server-side**: use Secrets Management for sensitive keys.

### Deployment outside Google AI Studio

- Deploying to Cloud Run gives a public URL but uses your API key for all users' Gemini calls.
- JavaScript apps run client-side — ensure API keys have minimal access (other File Search Stores from the same project may be accessible).
- For secure external deployment (e.g., after downloading ZIP), move API-key logic server-side to prevent exposure. Not needed if deploying via Cloud Run.
> [!danger]
> Simply replacing the placeholder with a real API key in client-side code is strongly discouraged — the key becomes visible to any user.

### Error when sharing apps

If end users hit **403 Access Restricted** on shared URLs:

- **Browser extensions**: privacy tools (e.g., Privacy Badger) may block the app. Disable to test.
- **Build issues**: prompt the agent to "fix any build issues with the current code", then reshare.

## FAQ

### What is Build in AI Studio?

AI Studio Build takes you from a simple prompt to a production-ready, AI-powered application using Gemini. Describe what to build; Gemini generates the app. Explore the gallery and remix apps.

### Why does Build call Gemini API from client-side code?

Best practice is server-side calls to avoid key exposure. But AI Studio has a Gemini API proxy for client-side calls that attaches the key without exposing it in code. Client-side generation uses this proxy, simplifying code and enabling sharing without providing an API key.

### Is my API key exposed when sharing apps?

Don't use a real API key — use placeholder `process.env.GEMINI_API_KEY`. When others use your app, AI Studio proxies calls using *their* (not yours) API key. Code is visible to anyone who can view the app.

### Who can see my apps?

Apps are private by default. Shared users can view code and fork. Edit-permission sharing lets others modify your app's code.

### Can I run apps outside of AI Studio?

Deploy to [Cloud Run](https://cloud.google.com/run) for a public URL with a proxy keeping your API key private (but using your key for all calls). Download as ZIP — replacing the placeholder works but **should not** be deployed this way since users can see the key. Secure external deployment requires [[018-docs-migrate-to-cloud.md.txt|moving some logic server-side]].

### Can I develop apps locally with my own tools and then share them here?

Not yet available. Feedback welcome for future use-cases.

### How can I use a database or other storage with my apps?

AI Studio apps run in Cloud Run containers. Use any network-accessible storage (no firewall blocking dynamic IPs). Direct storage configuration within AI Studio is planned.

### How can I access the microphone, webcam, and other Navigator APIs?

Extra acknowledgement is required before accessing [Navigator APIs](https://developer.mozilla.org/en-US/docs/Web/API/Navigator). Add permission requests to `metadata.json`:

```json
{
  "name": "My app",
  "requestFramePermissions": [
    "microphone",
    "camera",
    "display-capture",
    "geolocation",
    "bluetooth",
    "clipboard-read",
    "serial",
    "usb"
  ]
}
```

Supported values are a subset of standard [policy-controlled features](https://github.com/w3c/webappsec-permissions-policy/blob/main/features.md).

### How can I use GitHub with my apps?

Create a repository and commit changes. Pulling remote changes is not currently supported.

### Can I give other users edit access to my app?

Not yet — coming soon.

### Why was my app flagged for policy violation?

Apps are automatically reviewed for policy compliance. Violations include: malware/phishing/impersonation, CSIA content, harassment, hate speech, human trafficking, sexually explicit content, violence/gore, harmful/dangerous content. Flagged apps are removed; appeals available. Repeated violations may terminate AI Studio access.

### What are my responsibilities as an app developer?

As the app owner, you're responsible for behavior and all data handled:

- **Legal Compliance & Third Party Rights**: comply with laws/regulations; don't violate IP or privacy rights.
- **Content Monitoring**: additional terms may apply (e.g., [Google Cloud Terms of Service](https://cloud.google.com/terms) for Firestore require publishing prohibited content policies).
- **Safe Implementation**: implement safeguards/moderation to prevent misuse.

See [use restrictions](https://ai.google.dev/gemini-api/terms#use-restrictions) in the Terms of Service.

### What terms apply to apps in the app gallery?

The [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms) apply, unless otherwise noted.

## What's next

- [[018-docs-migrate-to-cloud.md.txt|Developing Full-Stack Apps]]
- See examples in the [App Gallery](https://aistudio.google.com/apps?source=showcase).

#google-ai-studio #gemini-api #full-stack-development #vibe-coding #cloud-run
