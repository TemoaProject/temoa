import subprocess
import sys
import temoa

def test_import() -> None:
    print(f"Importing temoa version: {temoa.__version__}")
    assert temoa.__version__ is not None

def test_cli() -> None:
    print("Running temoa --version CLI command...")
    result = subprocess.run(["temoa", "--version"], capture_output=True, text=True)
    print(f"CLI output: {result.stdout.strip()}")
    assert result.returncode == 0
    assert "Temoa Version:" in result.stdout
    assert temoa.__version__ in result.stdout

def test_help() -> None:
    print("Running temoa --help CLI command...")
    result = subprocess.run(["temoa", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "The Temoa Project" in result.stdout

if __name__ == "__main__":
    try:
        test_import()
        test_cli()
        test_help()
        print("\n✅ Smoke test passed!")
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        sys.exit(1)
