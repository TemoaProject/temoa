#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from typing import Any


def parse_version(version_str: str) -> dict[str, Any]:
    """
    Parses a PEP 440 version string into its components.
    Basic supported format: major.minor.patch[a|b|rcN]
    """
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:([abc]|rc)(\d+))?$'
    match = re.match(pattern, version_str)
    if not match:
        raise ValueError(f"Version '{version_str}' does not match expected format X.Y.Z[a|b|rcN]")

    major, minor, patch, pre_type, pre_num = match.groups()
    return {
        'major': int(major),
        'minor': int(minor),
        'patch': int(patch),
        'pre_type': pre_type,
        'pre_num': int(pre_num) if pre_num else None,
    }


def stringify_version(components: dict[str, Any]) -> str:
    base = f'{components["major"]}.{components["minor"]}.{components["patch"]}'
    if components['pre_type']:
        return f'{base}{components["pre_type"]}{components["pre_num"] or 1}'
    return base


def bump_version(components: dict[str, Any], part: str) -> dict[str, Any]:
    new = components.copy()

    if part == 'major':
        new['major'] += 1
        new['minor'] = 0
        new['patch'] = 0
        new['pre_type'] = None
        new['pre_num'] = None
    elif part == 'minor':
        new['minor'] += 1
        new['patch'] = 0
        new['pre_type'] = None
        new['pre_num'] = None
    elif part == 'patch':
        new['patch'] += 1
        new['pre_type'] = None
        new['pre_num'] = None
    elif part in ['a', 'b', 'rc', 'alpha', 'beta']:
        pre_map = {'alpha': 'a', 'beta': 'b', 'rc': 'rc', 'a': 'a', 'b': 'b'}
        target_pre = pre_map[part]
        pre_ordinal = {'a': 0, 'b': 1, 'rc': 2}

        # Check for precedence to prevent downgrading within the same patch version
        if new['pre_type'] and pre_ordinal[target_pre] < pre_ordinal[new['pre_type']]:
            new['patch'] += 1
            new['pre_type'] = target_pre
            new['pre_num'] = 1
        elif new['pre_type'] == target_pre:
            new['pre_num'] = (new['pre_num'] or 0) + 1
        else:
            # If moving to higher precedence (e.g., a -> b) or starting from final
            if not new['pre_type']:
                new['patch'] += 1
            new['pre_type'] = target_pre
            new['pre_num'] = 1
    elif part == 'final':
        new['pre_type'] = None
        new['pre_num'] = None
    else:
        raise ValueError(f'Unknown part to bump: {part}')

    return new


def main() -> None:
    parser = argparse.ArgumentParser(description='Bump Temoa version in temoa/__about__.py')
    parser.add_argument(
        'part',
        choices=['major', 'minor', 'patch', 'alpha', 'beta', 'rc', 'final', 'a', 'b'],
        help='The part of the version to bump',
    )
    parser.add_argument('--dry-run', action='store_true', help="Don't write to file")

    args = parser.parse_args()

    about_path = Path('temoa/__about__.py')
    if not about_path.exists():
        print(f'Error: {about_path} not found.')
        sys.exit(1)

    content = about_path.read_text()
    version_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", content)
    if not version_match:
        print('Error: Could not find __version__ in temoa/__about__.py')
        sys.exit(1)

    old_version_str = version_match.group(1)
    try:
        components = parse_version(old_version_str)
    except ValueError as e:
        print(f'Error: {e}')
        sys.exit(1)

    new_components = bump_version(components, args.part)
    new_version_str = stringify_version(new_components)

    if old_version_str == new_version_str:
        print(f'Version is already {new_version_str}. No change made.')
        return

    print(f'Bumping version: {old_version_str} -> {new_version_str}')

    if not args.dry_run:
        new_content = content.replace(
            f"__version__ = '{old_version_str}'", f"__version__ = '{new_version_str}'"
        )
        new_content = new_content.replace(
            f'__version__ = "{old_version_str}"', f'__version__ = "{new_version_str}"'
        )

        # Also update TEMOA_MAJOR and TEMOA_MINOR if they changed
        if new_components['major'] != components['major']:
            new_content = re.sub(
                r'TEMOA_MAJOR = \d+', f'TEMOA_MAJOR = {new_components["major"]}', new_content
            )
        if new_components['minor'] != components['minor']:
            new_content = re.sub(
                r'TEMOA_MINOR = \d+', f'TEMOA_MINOR = {new_components["minor"]}', new_content
            )

        about_path.write_text(new_content)
        print(f'Successfully updated {about_path}')

        print('\nNext steps:')
        print(f'  git add {about_path}')
        print(f'  git commit -m "chore: bump version to {new_version_str}"')
        print(f'  git tag -a v{new_version_str} -m "Release v{new_version_str}"')
        print(f'  git push origin v{new_version_str}')
    else:
        print('Dry run: file not modified.')


if __name__ == '__main__':
    main()
