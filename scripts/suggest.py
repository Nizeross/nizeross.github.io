"""Offline writing suggestions. Never changes article text or calls an API."""
import argparse
import json
from pathlib import Path
import re
import sys

from check_content import ROOT, parse_document


def tokens(text):
    words = set(re.findall(r'[a-z][a-z0-9+#.-]{1,}', text.lower()))
    chinese = ''.join(re.findall(r'[\u4e00-\u9fff]', text))
    return words | {chinese[i:i + 2] for i in range(len(chinese) - 1)}


def similarity(a, b):
    return len(a & b) / max(1, len(a | b))


def suggest(path):
    path = path.resolve()
    if not path.is_relative_to(ROOT / 'content'):
        raise ValueError('Choose an article inside content/')
    meta, body = parse_document(path.read_text(encoding='utf-8'))
    lines = [x.strip() for x in body.splitlines() if x.strip() and not x.startswith(('#', '```', '{{', '!['))]
    vocab = tokens(body)
    related = []
    tags = set()
    for other in (ROOT / 'content/posts').rglob('*.md'):
        if other.resolve() == path:
            continue
        other_meta, other_body = parse_document(other.read_text(encoding='utf-8'))
        score = similarity(vocab, tokens(other_body))
        if score > 0:
            related.append({'path': other.relative_to(ROOT).as_posix(), 'score': round(score, 3)})
        tags.update(tag for tag in other_meta.get('tags', []) if tag.lower() in body.lower())
    return {'mode': 'offline-heuristic-not-generative-ai', 'reviewRequired': True,
            'summaryCandidate': ' '.join(lines[:2])[:160], 'tagCandidates': sorted(tags),
            'relatedCandidates': sorted(related, key=lambda x: -x['score'])[:3],
            'note': '仅供人工参考；没有修改文章，没有执行代码，没有联网。'}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('article', type=Path)
    args = parser.parse_args()
    print(json.dumps(suggest(args.article), ensure_ascii=False, indent=2))
