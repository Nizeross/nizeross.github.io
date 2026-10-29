"""Fail closed unless the exact main commit came from an approved merged PR."""
import json
import os
import urllib.request


def approved_pull(pull, reviews, sha):
    if not (pull.get('merged_at') and pull['base']['ref'] == 'main' and pull.get('merge_commit_sha') == sha):
        return False
    latest = {}
    for review in reviews:
        login = review['user']['login']
        if review['state'] != 'COMMENTED':
            latest[login] = review
    if any(review['state'] == 'CHANGES_REQUESTED' for review in latest.values()):
        return False
    return any(review['state'] == 'APPROVED'
               and review.get('commit_id') == pull['head']['sha']
               and review['user'].get('type') != 'Bot'
               and login != pull['user']['login'] for login, review in latest.items())


def main():
    repo, sha = os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_SHA']
    token = os.environ['GITHUB_TOKEN']
    def get(path):
        request = urllib.request.Request(f'https://api.github.com/repos/{repo}/{path}', headers={
            'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    pulls = get(f'commits/{sha}/pulls?per_page=100')
    for pull in pulls:
        reviews = []
        for page in range(1, 11):
            batch = get(f'pulls/{pull["number"]}/reviews?per_page=100&page={page}')
            reviews.extend(batch)
            if len(batch) < 100:
                break
        else:
            raise SystemExit('Too many reviews; refusing ambiguous release')
        if approved_pull(pull, reviews, sha):
            print(f'Review gate passed for PR #{pull["number"]}')
            return
    raise SystemExit('Release blocked: no merged PR with approval of the final head commit by another human reviewer.')


if __name__ == '__main__':
    main()
