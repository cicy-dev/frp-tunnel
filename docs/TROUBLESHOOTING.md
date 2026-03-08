# Troubleshooting

## Connection refused

```bash
# Check server is running
ft server status

# Check firewall ports are open
sudo ss -tlnp | grep -E '7000|6022'
```

## Token mismatch

```bash
# Check server token
cat ~/data/frp/frps.yaml | grep token

# Ensure client config has same token
cat ~/data/frp/frpc.yaml | grep token
```

## Binary not found

```bash
# Re-init to trigger download
ft server init -f
# or
ft client init -f
```

## Client won't connect

```bash
# Check logs
tail -20 ~/data/frp/frpc.log

# Test server reachability
nc -zv YOUR_SERVER_IP 7000

# Run frpc directly for verbose output
ft frpc -c ~/data/frp/frpc.yaml
```

## Server won't start

```bash
# Check logs
tail -20 ~/data/frp/frps.log

# Check port conflict
sudo ss -tlnp | grep 7000

# Validate config
ft frps verify -c ~/data/frp/frps.yaml
```

## Hot-reload fails

```bash
# frpc reload requires webServer to be configured in frpc.yaml
# Default config includes it. Check:
grep -A2 webServer ~/data/frp/frpc.yaml

# If missing, add:
# webServer:
#   addr: 127.0.0.1
#   port: 7400
```

## Debug mode

```bash
# Run with verbose output (foreground)
ft frps -c ~/data/frp/frps.yaml --log_level debug
ft frpc -c ~/data/frp/frpc.yaml --log_level debug
```

## Reset everything

```bash
ft stop
rm ~/data/frp/frps.yaml ~/data/frp/frpc.yaml
ft server init
ft client init --server IP --token TOKEN --port 6022
```
