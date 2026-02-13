#!/bin/bash
# Test Windows CI SSH Connection

echo "🔍 Testing SSH connection to Windows CI..."
echo ""

# Wait for CI to start
echo "⏳ Waiting 30 seconds for CI to initialize..."
sleep 30

# Test SSH connection
echo "🔌 Attempting SSH connection..."
ssh -i ~/.ssh/id_rsa -o ConnectTimeout=10 -o StrictHostKeyChecking=no Administrator@35.241.96.74 -p 6012 "echo '✅ SSH connection successful!' && hostname && whoami && ft client-status"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSH test passed!"
    echo ""
    read -p "Power off the CI? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔌 Powering off CI..."
        ssh -i ~/.ssh/id_rsa Administrator@35.241.96.74 -p 6012 "Remove-Item C:\running.txt -Force; Write-Host 'CI will stop in next check cycle'"
        echo "✅ Power off signal sent"
    fi
else
    echo ""
    echo "❌ SSH connection failed"
    echo "Possible reasons:"
    echo "  1. CI not started yet (wait longer)"
    echo "  2. FRP client not connected"
    echo "  3. SSH keys not configured"
fi
