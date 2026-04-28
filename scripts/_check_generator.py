"""Check that DEF_02_SYSTEM_PROMPT exists in rag.generator."""
import pathlib

# Read file directly to verify content on disk
content = pathlib.Path("rag/generator.py").read_text(encoding="utf-8")
print("DEF_02_SYSTEM_PROMPT in file:", "DEF_02_SYSTEM_PROMPT" in content)
print("MUST NOT in file:", "MUST NOT" in content)
print("system_prompt in file:", "system_prompt" in content)

# Show lines 27-45
lines = content.split("\n")
print("\n--- Lines 27-45 ---")
for i, line in enumerate(lines[26:45], start=27):
    print(f"{i}: {line}")

# Now try the import
from rag.generator import DEF_02_SYSTEM_PROMPT
assert isinstance(DEF_02_SYSTEM_PROMPT, str), "Not a string"
assert "MUST NOT" in DEF_02_SYSTEM_PROMPT, "MUST NOT not found"
print("\nImport OK:", DEF_02_SYSTEM_PROMPT[:80])
