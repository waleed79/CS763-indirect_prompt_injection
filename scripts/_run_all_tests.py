"""Run full pytest suite (not integration) and print results."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/", "-v", "--timeout=120",
     "-m", "not integration",
     "--tb=short", "-q"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
print(result.stdout[-5000:])  # last 5000 chars of stdout
if result.stderr:
    print("STDERR (last 1000):", result.stderr[-1000:])
sys.exit(result.returncode)
