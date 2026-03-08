# Installation

## pip (recommended)

```bash
pip install frp-tunnel
```

## From source

```bash
git clone https://github.com/cicy-dev/frp-tunnel.git
cd frp-tunnel
pip install .
```

## FRP Binaries

Binaries are bundled in `bin/` for default platforms (linux_arm64, darwin_amd64, windows_amd64).

For other platforms, `ft server init` or `ft client init` will auto-download from GitHub releases.

Manual download: https://github.com/fatedier/frp/releases

## Verify

```bash
ft --version
ft -h
```

## Server Firewall

Open these ports on your server:

| Port | Purpose |
|------|---------|
| 7000 | FRP control |
| 7500 | Dashboard (optional) |
| 6000-6100 | Tunnel ports (adjust as needed) |

### GCP

```bash
gcloud compute firewall-rules create frp-tunnel \
    --allow tcp:6000-6100,tcp:7000,tcp:7500
```

### UFW (Ubuntu)

```bash
sudo ufw allow 7000/tcp
sudo ufw allow 7500/tcp
sudo ufw allow 6000:6100/tcp
```
