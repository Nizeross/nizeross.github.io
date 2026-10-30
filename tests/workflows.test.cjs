const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const YAML = require('yaml');

function workflow(file) {
  const document = YAML.parseDocument(fs.readFileSync(file, 'utf8'), { uniqueKeys: true });
  assert.deepEqual(document.errors, []);
  return document.toJS();
}

test('quality workflow is valid and read-only', () => {
  const value = workflow('.github/workflows/quality.yml');
  assert.ok(Object.hasOwn(value.on, 'pull_request'));
  assert.ok(Object.hasOwn(value.on, 'workflow_call'));
  assert.deepEqual(value.permissions, { contents: 'read' });
  assert.equal(Object.hasOwn(value.on, 'pull_request_target'), false);
  const steps = value.jobs.verify.steps;
  assert.ok(steps.some(step => step.run?.includes('python scripts/check_site.py')));
  assert.ok(steps.some(step => step.run === 'npm run test:e2e'));
});

test('proposal releases only after review, verification, packaging and environment approval', () => {
  const value = workflow('.github/workflow-proposals/pages.yml');
  assert.deepEqual(value.on.push.branches, ['main']);
  assert.equal(value.jobs.validate.needs, 'review-gate');
  assert.equal(value.jobs.package.needs, 'validate');
  assert.equal(value.jobs.deploy.needs, 'package');
  assert.equal(value.jobs.deploy.environment.name, 'github-pages');
  assert.equal(value.jobs.deploy.permissions.pages, 'write');
  assert.equal(value.jobs.package.permissions.actions, 'read');
  assert.equal(fs.existsSync('.github/workflows/pages.yml'), false);
});

test('existing production workflow remains syntactically valid', () => {
  const value = workflow('.github/workflows/hugo.yaml');
  assert.deepEqual(value.on.push.branches, ['main']);
});
