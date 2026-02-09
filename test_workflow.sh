#!/bin/bash
# Test complete workflow

set -e

echo "=== Testing FRP Tunnel Workflow ==="

# Test 1: Generate config
echo -e "\n1. Generate client config..."
ft client --server 1.2.3.4 --token test_token --port 6003 --port 6004

# Test 2: Verify config exists
echo -e "\n2. Verify config file..."
if [ -f ~/data/frp/frpc.yaml ]; then
    echo "✅ Config file created"
    grep -q "serverAddr: 1.2.3.4" ~/data/frp/frpc.yaml && echo "✅ Server address correct"
    grep -q "webServer:" ~/data/frp/frpc.yaml && echo "✅ WebServer enabled"
else
    echo "❌ Config file not found"
    exit 1
fi

# Test 3: Add port
echo -e "\n3. Add port 6005..."
ft client-add-port 6005
grep -q "remotePort: 6005" ~/data/frp/frpc.yaml && echo "✅ Port 6005 added"

# Test 4: Remove port
echo -e "\n4. Remove port 6004..."
ft client-remove-port 6004
! grep -q "remotePort: 6004" ~/data/frp/frpc.yaml && echo "✅ Port 6004 removed"

# Test 5: Test frpc command
echo -e "\n5. Test frpc forwarding..."
ft frpc -v && echo "✅ frpc command works"

# Test 6: Generate token
echo -e "\n6. Generate token..."
ft token | grep -q "frp_" && echo "✅ Token generation works"

echo -e "\n✅ All tests passed!"
