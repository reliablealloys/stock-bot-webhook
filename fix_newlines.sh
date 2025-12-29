#!/bin/bash
# Fix newline escaping in main.py

sed -i 's/\\\\\\\\n/\\n/g' main.py

echo "✅ Fixed newlines in main.py"
echo "Commit and push the changes"
