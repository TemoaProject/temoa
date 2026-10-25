import shutil
import subprocess

import temoa


def _find_temoa_path() -> str:
    path = shutil.which('temoa')
    if not path:
        raise RuntimeError('temoa executable not found in PATH')
    return path


def test_import() -> None:
    print(f'Importing temoa version: {temoa.__version__}')
    assert temoa.__version__ is not None


def test_cli() -> None:
    print('Running temoa --version CLI command...')
    temoa_path = _find_temoa_path()

    result = subprocess.run(
        [temoa_path, '--version'], capture_output=True, text=True, timeout=10, check=True
    )
    print(f'CLI output: {result.stdout.strip()}')
    assert 'Temoa Version:' in result.stdout
    assert temoa.__version__ in result.stdout


def test_help() -> None:
    print('Running temoa --help CLI command...')
    temoa_path = _find_temoa_path()

    result = subprocess.run(
        [temoa_path, '--help'], capture_output=True, text=True, timeout=10, check=True
    )
    assert 'The Temoa Project' in result.stdout


if __name__ == '__main__':
    test_import()
    test_cli()
    test_help()
    print('\n✅ Smoke test passed!')
