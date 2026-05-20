---
title: Web
url: https://opencode.ai/docs/web/
source: crawler
fetched_at: 2026-02-14T12:04:42.16383-03:00
rendered_js: false
word_count: 300
summary: This guide explains how to launch and configure the OpenCode web interface for browser-based AI coding. It covers server setup, networking options like mDNS and CORS, authentication, and managing coding sessions.
tags:
    - web-interface
    - server-configuration
    - opencode
    - authentication
    - networking
    - mdns
category: guide
---

Using OpenCode in your browser.

OpenCode can run as a web application in your browser, providing the same powerful AI coding experience without needing a terminal.

![OpenCode Web - New Session](https://opencode.ai/docs/_astro/web-homepage-new-session.BB1mEdgo_Z1AT1v3.webp)

## [Getting Started](#getting-started)

Start the web interface by running:

This starts a local server on `127.0.0.1` with a random available port and automatically opens OpenCode in your default browser.

* * *

## [Configuration](#configuration)

You can configure the web server using command line flags or in your [config file](https://opencode.ai/docs/config).

### [Port](#port)

By default, OpenCode picks an available port. You can specify a port:

### [Hostname](#hostname)

By default, the server binds to `127.0.0.1` (localhost only). To make OpenCode accessible on your network:

```

opencodeweb--hostname0.0.0.0
```

When using `0.0.0.0`, OpenCode will display both local and network addresses:

```

Local access:       http://localhost:4096
Network access:     http://192.168.1.100:4096
```

### [mDNS Discovery](#mdns-discovery)

Enable mDNS to make your server discoverable on the local network:

This automatically sets the hostname to `0.0.0.0` and advertises the server as `opencode.local`.

You can customize the mDNS domain name to run multiple instances on the same network:

```

opencodeweb--mdns--mdns-domainmyproject.local
```

### [CORS](#cors)

To allow additional domains for CORS (useful for custom frontends):

```

opencodeweb--corshttps://example.com
```

### [Authentication](#authentication)

To protect access, set a password using the `OPENCODE_SERVER_PASSWORD` environment variable:

```

OPENCODE_SERVER_PASSWORD=secretopencodeweb
```

The username defaults to `opencode` but can be changed with `OPENCODE_SERVER_USERNAME`.

* * *

## [Using the Web Interface](#using-the-web-interface)

Once started, the web interface provides access to your OpenCode sessions.

### [Sessions](#sessions)

View and manage your sessions from the homepage. You can see active sessions and start new ones.

![OpenCode Web - Active Session](https://opencode.ai/docs/_astro/web-homepage-active-session.BbK4Ph6e_Z1O7nO1.webp)

### [Server Status](#server-status)

Click “See Servers” to view connected servers and their status.

![OpenCode Web - See Servers](https://opencode.ai/docs/_astro/web-homepage-see-servers.BpCOef2l_ZB0rJd.webp)

* * *

## [Attaching a Terminal](#attaching-a-terminal)

You can attach a terminal TUI to a running web server:

```

# Start the web server
opencodeweb--port4096
# In another terminal, attach the TUI
opencodeattachhttp://localhost:4096
```

This allows you to use both the web interface and terminal simultaneously, sharing the same sessions and state.

* * *

## [Config File](#config-file)

You can also configure server settings in your `opencode.json` config file:

```

{
"server": {
"port": 4096,
"hostname": "0.0.0.0",
"mdns": true,
"cors": ["https://example.com"]
}
}
```

Command line flags take precedence over config file settings.