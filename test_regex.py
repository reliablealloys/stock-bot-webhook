import re

# Test the broken regex
text = "50mm 304L"
broken_pattern = r'(\\d+\\.?\\d*)\\s*mm'
working_pattern = r'(\d+\.?\d*)\s*mm'

print(f"Testing: {text}")
print(f"Broken pattern result: {re.search(broken_pattern, text.lower())}")
print(f"Working pattern result: {re.search(working_pattern, text.lower())}")

# The fix: Line 165 should be:
# size_match = re.search(r'(\d+\.?\d*)\s*mm', text_lower)
