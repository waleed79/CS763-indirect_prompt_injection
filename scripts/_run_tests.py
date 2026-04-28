"""Run pytest on test_defense.py and print results."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/test_defense.py", "-v", "--timeout=120",
     "-m", "not integration",
     "--tb=short"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[-3000:])
sys.exit(result.returncode)
