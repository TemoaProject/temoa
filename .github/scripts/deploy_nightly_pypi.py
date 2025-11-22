import copy
import os
import shutil
import subprocess
from datetime import UTC, datetime
from typing import Any

import boto3
import tomlkit
from botocore.exceptions import ClientError

# --- Configuration (from environment variables) ---
# Secrets
R2_ACCOUNT_ID = os.environ['R2_ACCOUNT_ID']
R2_ACCESS_KEY_ID = os.environ['R2_ACCESS_KEY_ID']
R2_SECRET_ACCESS_KEY = os.environ['R2_SECRET_ACCESS_KEY']
NIGHTLIES_GH_TOKEN = os.environ['NIGHTLIES_GH_TOKEN']
# Variables
R2_BUCKET_NAME = os.environ['R2_BUCKET_NAME']
R2_PACKAGES_PUBLIC_URL = os.environ['R2_PACKAGES_PUBLIC_URL']
GH_PAGES_INDEX_BASE_URL = os.environ['GH_PAGES_INDEX_BASE_URL']
GH_PAGES_REPO = os.environ['GH_PAGES_REPO']
GH_PAGES_BRANCH = os.environ['GH_PAGES_BRANCH']
SOURCE_COMMIT_SHA = os.environ.get('SOURCE_COMMIT_SHA', 'N/A')  # Passed from workflow

# --- Constants ---
TEMPORARY_OUTPUT_DIR = '/tmp/gh_pages_output'  # Temporary dir for dumb-pypi output
NIGHTLIES_REPO_CLONE_DIR = '/tmp/nightlies_repo_clone'  # Temporary dir for cloning gh-pages repo
UPLOADED_PACKAGE_LIST_FILE = os.path.join(TEMPORARY_OUTPUT_DIR, 'uploaded_package_list.txt')


# --- Boto3 S3 Client for R2 ---
s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)


def run_command(
    command: list[str],
    cwd: str | None = None,
    check: bool = True,
    mask_values: list[str] | None = None,
) -> str:
    """Helper to run shell commands."""

    def _redact(text: str) -> str:
        if not mask_values:
            return text
        redacted = text
        for secret in mask_values:
            if secret:
                redacted = redacted.replace(secret, '***')
        return redacted

    print(f'Running command: {" ".join(_redact(part) for part in command)}')
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(_redact(result.stdout))
    if result.stderr and check:
        print(_redact(result.stderr))
    return result.stdout.strip()


def get_current_temoa_version() -> str:
    """Reads the base version from pyproject.toml."""
    with open('pyproject.toml') as f:
        data = tomlkit.parse(f.read())
    return data['project']['version']


def generate_nightly_version(base_version: str) -> str:
    """Generates a PEP 440 compliant nightly version string."""
    today = datetime.now(UTC).strftime('%Y%m%d')
    return f'{base_version}.dev{today}'


def upload_packages_to_r2(dist_dir: str) -> None:
    """Uploads built packages from dist_dir to R2 and lists filenames."""
    os.makedirs(os.path.dirname(UPLOADED_PACKAGE_LIST_FILE), exist_ok=True)
    uploaded_filenames = []
    for filename in os.listdir(dist_dir):
        file_path = os.path.join(dist_dir, filename)
        if os.path.isfile(file_path):
            print(f'Uploading {filename} to R2 bucket {R2_BUCKET_NAME}...')
            try:
                s3_client.upload_file(
                    file_path,
                    R2_BUCKET_NAME,
                    filename,
                    ExtraArgs={'ContentType': 'application/octet-stream'},
                )
                print(f'Successfully uploaded {filename}')
                uploaded_filenames.append(filename)
            except ClientError as e:
                print(f'❌ ERROR uploading {filename} to R2: {e}')
                raise

    with open(UPLOADED_PACKAGE_LIST_FILE, 'w') as f:
        for fname in uploaded_filenames:
            f.write(f'{fname}\n')
    print(f'Generated {UPLOADED_PACKAGE_LIST_FILE} with {len(uploaded_filenames)} files.')


def deploy_dumb_pypi_index(nightly_version: str) -> None:
    """Generates dumb-pypi index and pushes to GitHub Pages."""
    print(f'Generating dumb-pypi index in {TEMPORARY_OUTPUT_DIR}...')
    run_command(['mkdir', '-p', TEMPORARY_OUTPUT_DIR])

    # Run dumb-pypi (this will use the dumb-pypi executable found in uv env)
    run_command(
        [
            'dumb-pypi',
            '--package-list',
            UPLOADED_PACKAGE_LIST_FILE,
            '--packages-url',
            R2_PACKAGES_PUBLIC_URL,
            '--output-dir',
            os.path.join(TEMPORARY_OUTPUT_DIR, 'simple/'),
            '--title',
            'Temoa Nightly PyPI Index',
        ]
    )
    print('dumb-pypi index generated.')

    print(f'Cloning {GH_PAGES_REPO} to {NIGHTLIES_REPO_CLONE_DIR}...')
    run_command(
        [
            'git',
            'clone',
            f'https://x-access-token:{NIGHTLIES_GH_TOKEN}@github.com/{GH_PAGES_REPO}.git',
            NIGHTLIES_REPO_CLONE_DIR,
        ],
        mask_values=[NIGHTLIES_GH_TOKEN],
    )

    run_command(
        ['git', 'config', 'user.name', os.environ.get('GITHUB_ACTOR', 'github-actions[bot]')],
        cwd=NIGHTLIES_REPO_CLONE_DIR,
    )  # Use GITHUB_ACTOR if available
    run_command(
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        cwd=NIGHTLIES_REPO_CLONE_DIR,
    )

    # Ensure the target branch exists or create it as orphan
    # Check if branch exists by trying to switch without creating
    try:
        run_command(['git', 'checkout', GH_PAGES_BRANCH], cwd=NIGHTLIES_REPO_CLONE_DIR)
    except subprocess.CalledProcessError:
        try:
            run_command(
                ['git', 'checkout', '--track', f'origin/{GH_PAGES_BRANCH}'],
                cwd=NIGHTLIES_REPO_CLONE_DIR,
            )
        except subprocess.CalledProcessError:
            run_command(
                ['git', 'checkout', '--orphan', GH_PAGES_BRANCH], cwd=NIGHTLIES_REPO_CLONE_DIR
            )

    # Clean existing content (except .git)
    # Use shutil.rmtree for directories and os.remove for files
    for item in os.listdir(NIGHTLIES_REPO_CLONE_DIR):
        if item == '.git':
            continue
        item_path = os.path.join(NIGHTLIES_REPO_CLONE_DIR, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Use shutil for robust directory deletion

    print(
        f'Copying generated index from {TEMPORARY_OUTPUT_DIR}/simple/ to '
        f'{NIGHTLIES_REPO_CLONE_DIR}...'
    )
    for item in os.listdir(os.path.join(TEMPORARY_OUTPUT_DIR, 'simple')):
        src_path = os.path.join(TEMPORARY_OUTPUT_DIR, 'simple', item)
        dest_path = os.path.join(NIGHTLIES_REPO_CLONE_DIR, item)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)

    run_command(['git', 'add', '.'], cwd=NIGHTLIES_REPO_CLONE_DIR)

    commit_message = (
        f'Automated nightly deploy of Temoa {nightly_version} (source commit: {SOURCE_COMMIT_SHA})'
    )

    try:
        run_command(['git', 'commit', '-m', commit_message], cwd=NIGHTLIES_REPO_CLONE_DIR)
        print('Committing changes...')
        run_command(
            ['git', 'push', 'origin', GH_PAGES_BRANCH],
            cwd=NIGHTLIES_REPO_CLONE_DIR,
            mask_values=[NIGHTLIES_GH_TOKEN],
        )
        print('✅ Nightly index pushed to GitHub Pages.')
    except subprocess.CalledProcessError as e:
        if 'nothing to commit' in e.stderr:
            print('No changes to commit for GitHub Pages index.')
        else:
            print(f'❌ ERROR committing/pushing to GitHub Pages: {e}')
            raise

    print(f'Nightly build index updated on GitHub Pages: {GH_PAGES_INDEX_BASE_URL}simple/')


def main() -> None:
    """Main execution function for nightly PyPI deployment."""
    print('Starting Temoa nightly PyPI deployment process...')

    # 1. Determine version
    base_version = get_current_temoa_version()
    nightly_version = generate_nightly_version(base_version)
    print(f'Nightly version to deploy: {nightly_version}')

    # 2. Store original pyproject.toml data for restoration

    original_pyproject_data: dict[str, Any]
    with open('pyproject.toml') as f:
        original_pyproject_data = tomlkit.parse(f.read())

    # Use try-finally to guarantee restoration
    try:
        # 3. Create a copy to modify for the build version
        modified_data = copy.deepcopy(original_pyproject_data)
        modified_data['project']['version'] = nightly_version

        with open('pyproject.toml', 'w') as f:
            f.write(tomlkit.dumps(modified_data))
        print(f'Temporarily updated pyproject.toml version to {nightly_version}')

        # 4. Build sdist and wheel
        dist_dir = 'dist'
        run_command(['uv', 'build', '--sdist', '--wheel'])  # Using uv build
        print('sdist and wheel built.')

        # 5. Upload packages to R2
        upload_packages_to_r2(dist_dir)
        print('Packages uploaded to R2.')

        # 6. Generate dumb-pypi index and push to GitHub Pages
        deploy_dumb_pypi_index(nightly_version)
        print('dumb-pypi index deployed.')

    finally:
        # 7. Restore original pyproject.toml unconditionally
        with open('pyproject.toml', 'w') as f:
            f.write(tomlkit.dumps(original_pyproject_data))
        print('Restored original pyproject.toml.')

    print('✅ Temoa nightly PyPI deployment complete.')


if __name__ == '__main__':
    main()
