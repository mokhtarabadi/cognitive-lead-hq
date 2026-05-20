---
title: Share
url: https://opencode.ai/docs/share/
source: crawler
fetched_at: 2026-02-14T12:04:43.702294-03:00
rendered_js: false
word_count: 322
summary: This document explains how to use OpenCode's share feature to create and manage public links for collaborative conversations. It details the different sharing modes, configuration options, and privacy considerations for users and enterprises.
tags:
    - open-code
    - conversation-sharing
    - collaboration
    - privacy
    - configuration
    - data-retention
    - enterprise-security
category: guide
---

OpenCode’s share feature allows you to create public links to your OpenCode conversations, so you can collaborate with teammates or get help from others.

* * *

## [How it works](#how-it-works)

When you share a conversation, OpenCode:

1. Creates a unique public URL for your session
2. Syncs your conversation history to our servers
3. Makes the conversation accessible via the shareable link — `opncd.ai/s/<share-id>`

* * *

## [Sharing](#sharing)

OpenCode supports three sharing modes that control how conversations are shared:

* * *

### [Manual (default)](#manual-default)

By default, OpenCode uses manual sharing mode. Sessions are not shared automatically, but you can manually share them using the `/share` command:

This will generate a unique URL that’ll be copied to your clipboard.

To explicitly set manual mode in your [config file](https://opencode.ai/docs/config):

```

{
"$schema": "https://opncd.ai/config.json",
"share": "manual"
}
```

* * *

You can enable automatic sharing for all new conversations by setting the `share` option to `"auto"` in your [config file](https://opencode.ai/docs/config):

```

{
"$schema": "https://opncd.ai/config.json",
"share": "auto"
}
```

With auto-share enabled, every new conversation will automatically be shared and a link will be generated.

* * *

### [Disabled](#disabled)

You can disable sharing entirely by setting the `share` option to `"disabled"` in your [config file](https://opencode.ai/docs/config):

```

{
"$schema": "https://opncd.ai/config.json",
"share": "disabled"
}
```

To enforce this across your team for a given project, add it to the `opencode.json` in your project and check into Git.

* * *

## [Un-sharing](#un-sharing)

To stop sharing a conversation and remove it from public access:

This will remove the share link and delete the data related to the conversation.

* * *

## [Privacy](#privacy)

There are a few things to keep in mind when sharing a conversation.

* * *

### [Data retention](#data-retention)

Shared conversations remain accessible until you explicitly unshare them. This includes:

- Full conversation history
- All messages and responses
- Session metadata

* * *

### [Recommendations](#recommendations)

- Only share conversations that don’t contain sensitive information.
- Review conversation content before sharing.
- Unshare conversations when collaboration is complete.
- Avoid sharing conversations with proprietary code or confidential data.
- For sensitive projects, disable sharing entirely.

* * *

## [For enterprises](#for-enterprises)

For enterprise deployments, the share feature can be:

- **Disabled** entirely for security compliance
- **Restricted** to users authenticated through SSO only
- **Self-hosted** on your own infrastructure

[Learn more](https://opencode.ai/docs/enterprise) about using opencode in your organization.