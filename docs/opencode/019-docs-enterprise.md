---
title: Enterprise
url: https://opencode.ai/docs/enterprise/
source: crawler
fetched_at: 2026-02-14T12:04:35.479957-03:00
rendered_js: false
word_count: 684
summary: This document provides an overview of security, deployment, and configuration options for implementing OpenCode within an enterprise environment, focusing on data privacy and internal infrastructure integration.
tags:
    - opencode-enterprise
    - security
    - data-privacy
    - sso-integration
    - enterprise-deployment
    - configuration
category: guide
---

Using OpenCode securely in your organization.

OpenCode Enterprise is for organizations that want to ensure that their code and data never leaves their infrastructure. It can do this by using a centralized config that integrates with your SSO and internal AI gateway.

To get started with OpenCode Enterprise:

1. Do a trial internally with your team.
2. [**Contact us**](mailto:contact@anoma.ly) to discuss pricing and implementation options.

* * *

## [Trial](#trial)

OpenCode is open source and does not store any of your code or context data, so your developers can simply [get started](https://opencode.ai/docs/) and carry out a trial.

* * *

### [Data handling](#data-handling)

**OpenCode does not store your code or context data.** All processing happens locally or through direct API calls to your AI provider.

This means that as long as you are using a provider you trust, or an internal AI gateway, you can use OpenCode securely.

The only caveat here is the optional `/share` feature.

* * *

#### [Sharing conversations](#sharing-conversations)

If a user enables the `/share` feature, the conversation and the data associated with it are sent to the service we use to host these share pages at opencode.ai.

The data is currently served through our CDN’s edge network, and is cached on the edge near your users.

We recommend you disable this for your trial.

```

{
"$schema": "https://opencode.ai/config.json",
"share": "disabled"
}
```

[Learn more about sharing](https://opencode.ai/docs/share).

* * *

### [Code ownership](#code-ownership)

**You own all code produced by OpenCode.** There are no licensing restrictions or ownership claims.

* * *

## [Pricing](#pricing)

We use a per-seat model for OpenCode Enterprise. If you have your own LLM gateway, we do not charge for tokens used. For further details about pricing and implementation options, [**contact us**](mailto:contact@anoma.ly).

* * *

## [Deployment](#deployment)

Once you have completed your trial and you are ready to use OpenCode at your organization, you can [**contact us**](mailto:contact@anoma.ly) to discuss pricing and implementation options.

* * *

### [Central Config](#central-config)

We can set up OpenCode to use a single central config for your entire organization.

This centralized config can integrate with your SSO provider and ensures all users access only your internal AI gateway.

* * *

### [SSO integration](#sso-integration)

Through the central config, OpenCode can integrate with your organization’s SSO provider for authentication.

This allows OpenCode to obtain credentials for your internal AI gateway through your existing identity management system.

* * *

### [Internal AI gateway](#internal-ai-gateway)

With the central config, OpenCode can also be configured to use only your internal AI gateway.

You can also disable all other AI providers, ensuring all requests go through your organization’s approved infrastructure.

* * *

### [Self-hosting](#self-hosting)

While we recommend disabling the share pages to ensure your data never leaves your organization, we can also help you self-host them on your infrastructure.

This is currently on our roadmap. If you’re interested, [**let us know**](mailto:contact@anoma.ly).

* * *

## [FAQ](#faq)

What is OpenCode Enterprise?

OpenCode Enterprise is for organizations that want to ensure that their code and data never leaves their infrastructure. It can do this by using a centralized config that integrates with your SSO and internal AI gateway.

How do I get started with OpenCode Enterprise?

Simply start with an internal trial with your team. OpenCode by default does not store your code or context data, making it easy to get started.

Then [**contact us**](mailto:contact@anoma.ly) to discuss pricing and implementation options.

How does enterprise pricing work?

We offer per-seat enterprise pricing. If you have your own LLM gateway, we do not charge for tokens used. For further details, [**contact us**](mailto:contact@anoma.ly) for a custom quote based on your organization’s needs.

Is my data secure with OpenCode Enterprise?

Yes. OpenCode does not store your code or context data. All processing happens locally or through direct API calls to your AI provider. With central config and SSO integration, your data remains secure within your organization’s infrastructure.

Can we use our own private NPM registry?

OpenCode supports private npm registries through Bun’s native `.npmrc` file support. If your organization uses a private registry, such as JFrog Artifactory, Nexus, or similar, ensure developers are authenticated before running OpenCode.

To set up authentication with your private registry:

```

npmlogin--registry=https://your-company.jfrog.io/api/npm/npm-virtual/
```

This creates `~/.npmrc` with authentication details. OpenCode will automatically pick this up.

Alternatively, you can manually configure a `.npmrc` file:

```

registry=https://your-company.jfrog.io/api/npm/npm-virtual/
//your-company.jfrog.io/api/npm/npm-virtual/:_authToken=${NPM_AUTH_TOKEN}
```

Developers must be logged into the private registry before running OpenCode to ensure packages can be installed from your enterprise registry.