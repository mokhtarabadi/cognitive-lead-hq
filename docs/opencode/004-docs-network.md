---
title: Network
url: https://opencode.ai/docs/network/
source: crawler
fetched_at: 2026-02-14T12:04:41.409044-03:00
rendered_js: false
word_count: 88
summary: This document explains how to configure proxy settings and custom CA certificates for OpenCode in enterprise network environments. It covers environment variables, authentication, and trust configurations for secure connections.
tags:
    - proxy-configuration
    - environment-variables
    - custom-certificates
    - enterprise-networking
    - authentication
    - network-security
category: configuration
---

OpenCode supports standard proxy environment variables and custom certificates for enterprise network environments.

* * *

## [Proxy](#proxy)

OpenCode respects standard proxy environment variables.

```

# HTTPS proxy (recommended)
export HTTPS_PROXY=https://proxy.example.com:8080
# HTTP proxy (if HTTPS not available)
export HTTP_PROXY=http://proxy.example.com:8080
# Bypass proxy for local server (required)
export NO_PROXY=localhost,127.0.0.1
```

You can configure the server’s port and hostname using [CLI flags](https://opencode.ai/docs/cli#run).

* * *

### [Authenticate](#authenticate)

If your proxy requires basic authentication, include credentials in the URL.

```

export HTTPS_PROXY=http://username:password@proxy.example.com:8080
```

For proxies requiring advanced authentication like NTLM or Kerberos, consider using an LLM Gateway that supports your authentication method.

* * *

## [Custom certificates](#custom-certificates)

If your enterprise uses custom CAs for HTTPS connections, configure OpenCode to trust them.

```

export NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```

This works for both proxy connections and direct API access.