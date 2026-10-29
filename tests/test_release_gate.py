import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_gate import approved_pull


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.pull = {'merged_at': '2026-10-29', 'base': {'ref': 'main'}, 'merge_commit_sha': 'release',
                     'head': {'sha': 'final'}, 'user': {'login': 'author'}}
        self.review = {'state': 'APPROVED', 'commit_id': 'final', 'user': {'login': 'reviewer', 'type': 'User'}}

    def test_valid_review(self):
        self.assertTrue(approved_pull(self.pull, [self.review], 'release'))

    def test_direct_push(self):
        self.pull['merge_commit_sha'] = 'other'
        self.assertFalse(approved_pull(self.pull, [self.review], 'release'))

    def test_self_review(self):
        self.review['user']['login'] = 'author'
        self.assertFalse(approved_pull(self.pull, [self.review], 'release'))

    def test_stale_review(self):
        self.review['commit_id'] = 'older'
        self.assertFalse(approved_pull(self.pull, [self.review], 'release'))

    def test_dismissed_review(self):
        dismissed = dict(self.review, state='DISMISSED')
        self.assertFalse(approved_pull(self.pull, [self.review, dismissed], 'release'))

    def test_requested_changes(self):
        changes = {'state': 'CHANGES_REQUESTED', 'commit_id': 'final', 'user': {'login': 'second'}}
        self.assertFalse(approved_pull(self.pull, [self.review, changes], 'release'))

    def test_no_review(self):
        self.assertFalse(approved_pull(self.pull, [], 'release'))

    def test_unmerged_pull(self):
        self.pull['merged_at'] = None
        self.assertFalse(approved_pull(self.pull, [self.review], 'release'))


if __name__ == '__main__':
    unittest.main()
