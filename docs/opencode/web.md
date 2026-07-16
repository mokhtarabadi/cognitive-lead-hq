# Web

> Source: https://opencode.ai/docs/web/

# Web

Using OpenCode in your browser.

OpenCode can run as a web application in your browser, providing the same powerful AI coding experience without needing a terminal.
![OpenCode Web - New Session](/docs/_astro/web-homepage-new-session.BB1mEdgo_Z1AT1v3.webp)

## Getting Started

Start the web interface by running:

```
opencode web
```

This starts a local server on 127.0.0.1 with a random available port and automatically opens OpenCode in your default browser.

Caution

If OPENCODE_SERVER_PASSWORD is not set, the server will be unsecured. This is fine for local use but should be set for network access.

Windows Users

For the best experience, run opencode web from WSL rather than PowerShell. This ensures proper file system access and terminal integration.

---

## Configuration

You can configure the web server using command line flags or in your config file.

### Port

By default, OpenCode picks an available port. You can specify a port:

```
opencode web --port 4096
```

### Hostname

By default, the server binds to 127.0.0.1 (localhost only). To make OpenCode accessible on your network:

```
opencode web --hostname 0.0.0.0
```

When using 0.0.0.0, OpenCode will display both local and network addresses:

```
  Local access:       http://localhost:4096  Network access:     http://192.168.1.100:4096
```

### mDNS Discovery

Enable mDNS to make your server discoverable on the local network:

```
opencode web --mdns
```

This automatically sets the hostname to 0.0.0.0 and advertises the server as opencode.local.

You can customize the mDNS domain name to run multiple instances on the same network:

```
opencode web --mdns --mdns-domain myproject.local
```

### CORS

To allow additional domains for CORS (useful for custom frontends):

```
opencode web --cors https://example.com
```

### Authentication

To protect access, set a password using the OPENCODE_SERVER_PASSWORD environment variable:

```
OPENCODE_SERVER_PASSWORD=secret opencode web
```

The username defaults to opencode but can be changed with OPENCODE_SERVER_USERNAME.

---

## Using the Web Interface

Once started, the web interface provides access to your OpenCode sessions.

### Sessions

View and manage your sessions from the homepage. You can see active sessions and start new ones.
![OpenCode Web - Active Session](/docs/_astro/web-homepage-active-session.BbK4Ph6e_Z1O7nO1.webp)

### Server Status

Click “See Servers” to view connected servers and their status.
![OpenCode Web - See Servers](/docs/_astro/web-homepage-see-servers.BpCOef2l_ZB0rJd.webp)
---

## Attaching a Terminal

You can attach a terminal TUI to a running web server:

```
# Start the web serveropencode web --port 4096
# In another terminal, attach the TUIopencode attach http://localhost:4096
```

This allows you to use both the web interface and terminal simultaneously, sharing the same sessions and state.

---

## Config File

You can also configure server settings in your opencode.json config file:

```
{  "server": {    "port": 4096,    "hostname": "0.0.0.0",    "mdns": true,    "cors": ["https://example.com"]  }}
```

Command line flags take precedence over config file settings.

Edit pageFound a bug? Open an issueJoin our Discord communitySelect languageEnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文© Anomaly

Last updated: Jul 14, 2026
