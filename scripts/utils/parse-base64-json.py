import base64
import json
import sys

def parse_base64_json(base64_data):
    # Add padding if needed
    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += '=' * (4 - missing_padding)
    decoded = base64.b64decode(base64_data).decode('utf-8')
    return json.loads(decoded)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = parse_base64_json(sys.argv[1])
        print(json.dumps(data, indent=2))
    else:
        print("Usage: python parse-base64-json.py <base64_encoded_json>")
