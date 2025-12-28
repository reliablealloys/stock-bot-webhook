#!/usr/bin/env python3
"""
Quick fix script to correct the regex pattern in main.py
Run this to fix the double-escaped regex issue
"""

import re

# Read the file
with open('main.py', 'r') as f:
    content = f.read()

# Fix the broken regex pattern
content = content.replace(
    r"size_match = re.search(r'(\\\\d+\\\\.?\\\\d*)\\\\s*mm', text_lower)",
    r"size_match = re.search(r'(\d+\.?\d*)\s*mm', text_lower)"
)

# Write back
with open('main.py', 'w') as f:
    f.write(content)

print("✅ Fixed regex pattern in main.py!")
print("The bot should now correctly parse messages like '50mm 304L'")
