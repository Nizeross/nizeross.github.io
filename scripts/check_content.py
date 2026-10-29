"""Validate author-owned TOML Markdown and local image paths without a network."""
import ast
import datetime as dt
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TYPES = {'technical', 'project', 'reading', 'essay', 'life'}


def parse_document(text):
    lines = text.lstrip('\ufeff').splitlines()
    if not lines or lines[0].strip() != '+++':
        raise ValueError('Expected TOML frontmatter delimited by +++')
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == '+++')
    except StopIteration as exc:
        raise ValueError('Unclosed frontmatter') from exc
    return tomllib.loads('\n'.join(lines[1:end])), '\n'.join(lines[end + 1:])


def check_document(path, text, root=ROOT):
    errors = []
    try:
        meta, body = parse_document(text)
    except (ValueError, tomllib.TOMLDecodeError) as exc:
        return [str(exc)]
    if not isinstance(meta.get('title'), str) or not meta['title'].strip():
        errors.append('title must be a non-empty string')
    if 'draft' in meta and not isinstance(meta['draft'], bool):
        errors.append('draft must be a boolean')
    if 'kind' in meta:
        errors.append('Use contentType, not Hugo reserved key kind')
    for field in ('tags', 'categories', 'stack'):
        value = meta.get(field, [])
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f'{field} must be a list of non-empty strings')
    is_post = 'posts' in path.relative_to(root).parts
    if is_post:
        if not meta.get('summary') or not meta.get('categories'):
            errors.append('Posts require summary and categories')
        if meta.get('contentType') not in TYPES:
            errors.append('Unknown or missing contentType')
        try:
            date = meta.get('date')
            parsed = dt.datetime.fromisoformat(date.replace('Z', '+00:00')) if isinstance(date, str) else date
            if not isinstance(parsed, dt.datetime) or parsed.tzinfo is None:
                raise ValueError()
        except (ValueError, AttributeError):
            errors.append('date must be an ISO datetime with timezone')
    if path.suffix != '.md' or not re.fullmatch(r'_?index|[\w]+(?:-[\w]+)*', path.stem):
        errors.append('Filename must be index.md, _index.md or a safe slug.md')
    for part in path.relative_to(root / 'content').parts[:-1]:
        if not re.fullmatch(r'[\w]+(?:-[\w]+)*', part):
            errors.append(f'Unsafe directory slug: {part}')
    if meta.get('github') and not re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+/?', meta['github']):
        errors.append('github must be a GitHub repository HTTPS URL')
    in_fence = None
    code = []
    language = ''
    for number, line in enumerate(body.splitlines(), 1):
        fence = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            marker, suffix = fence.groups()
            if in_fence is None:
                in_fence, language, code = marker, suffix.strip(), []
            elif marker[0] == in_fence[0] and len(marker) >= len(in_fence) and not suffix.strip():
                if language == 'python':
                    try:
                        ast.parse('\n'.join(code))
                    except SyntaxError as exc:
                        errors.append(f'Python code block syntax: {exc.msg}')
                in_fence = None
            continue
        if in_fence:
            code.append(line)
            continue
        if re.search(r'<\s*script\b|javascript\s*:', line, re.I):
            errors.append(f'line {number}: active script content is not allowed')
        for target in re.findall(r'!\[[^\]]*\]\(([^\s)]+)', line):
            parsed = urlsplit(target.strip('<>'))
            if parsed.scheme or parsed.netloc:
                continue
            decoded = unquote(parsed.path)
            target_path = (root / 'static' / decoded.lstrip('/')) if decoded.startswith('/') else path.parent / decoded
            target_path = target_path.resolve()
            if not target_path.is_relative_to(root.resolve()) or not target_path.is_file():
                errors.append(f'Missing or out-of-project image: {target}')
    if in_fence:
        errors.append('Unclosed code fence')
    return errors


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    paths = sorted((ROOT / 'content').rglob('*.md'))
    failures = []
    for path in paths:
        for error in check_document(path, path.read_text(encoding='utf-8')):
            failures.append(f'{path.relative_to(ROOT)}: {error}')
    print('\n'.join(failures) if failures else f'PASS: {len(paths)} Markdown documents; frontmatter, names, images and Python examples')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
