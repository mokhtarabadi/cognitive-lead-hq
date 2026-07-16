# Windows-wsl

> Source: https://opencode.ai/docs/windows-wsl

# Windows (WSL)

Run OpenCode on Windows using WSL for the best experience.

While OpenCode can run directly on Windows, we recommend using Windows Subsystem for Linux (WSL) for the best experience. WSL provides a Linux environment that works seamlessly with OpenCode’s features.

Why WSL?

WSL offers better file system performance, full terminal support, and compatibility with development tools that OpenCode relies on.

---

## Setup

**Install WSL**

If you haven’t already, install WSL using the official Microsoft guide.

**Install OpenCode in WSL**

Once WSL is set up, open your WSL terminal and install OpenCode using one of the installation methods.

```
curl -fsSL https://opencode.ai/install | bash
```

- Terminal window

**Use OpenCode from WSL**

Navigate to your project directory (access Windows files via /mnt/c/, /mnt/d/, etc.) and run OpenCode.

```
cd /mnt/c/Users/YourName/projectopencode
```

- Terminal window

---

## Desktop App + WSL Server

If you prefer using the OpenCode Desktop app but want to run the server in WSL:

**Start the server in WSL** with --hostname 0.0.0.0 to allow external connections:

```
opencode serve --hostname 0.0.0.0 --port 4096
```

- Terminal window

**Connect the Desktop app** to http://localhost:4096

Note

If localhost does not work in your setup, connect using the WSL IP address instead (from WSL: hostname -I) and use http://<wsl-ip>:4096.

Caution

When using --hostname 0.0.0.0, set OPENCODE_SERVER_PASSWORD to secure the server.

```
OPENCODE_SERVER_PASSWORD=your-password opencode serve --hostname 0.0.0.0
```

---

## Web Client + WSL

For the best web experience on Windows:

**Run opencode web in the WSL terminal** rather than PowerShell:

```
opencode web --hostname 0.0.0.0
```

- Terminal window

**Access from your Windows browser** at http://localhost:<port> (OpenCode prints the URL)

Running opencode web from WSL ensures proper file system access and terminal integration while still being accessible from your Windows browser.

---

## Accessing Windows Files

WSL can access all your Windows files through the /mnt/ directory:

- C: drive → /mnt/c/
- D: drive → /mnt/d/
- And so on…

Example:

```
cd /mnt/c/Users/YourName/Documents/projectopencode
```

Tip

For the smoothest experience, consider cloning/copying your repo into the WSL filesystem (for example under ~/code/) and running OpenCode there.

---

## Tips

- Keep OpenCode running in WSL for projects stored on Windows drives - file access is seamless
- Use VS Code’s WSL extension alongside OpenCode for an integrated development workflow
- Your OpenCode config and sessions are stored within the WSL environment at ~/.local/share/opencode/

Edit pageFound a bug? Open an issueJoin our Discord communitySelect languageEnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文© Anomaly

Last updated: Jul 14, 2026
