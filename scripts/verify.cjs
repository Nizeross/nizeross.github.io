/* Full local gate with a persistent, failure-localized log. */
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const npm = process.env.npm_execpath;
if (!npm) throw new Error('Run this helper with npm run verify.');
const python = process.env.PYTHON || 'python';
const steps = [
  ['Content', python, ['scripts/site.py', 'check']],
  ['Markdown', process.execPath, [npm, 'run', 'lint']],
  ['Unit tests', python, ['-m', 'unittest', 'discover', '-s', 'tests', '-v']],
  ['Workflow tests', process.execPath, [npm, 'run', 'test:workflows']],
  ['Source security', python, ['scripts/security_check.py']],
  ['Dependency audit', process.execPath, [npm, 'audit', '--audit-level=low']],
  ['Hugo build', python, ['scripts/site.py', 'build']],
  ['Generated links', python, ['scripts/check_site.py']],
  ['Browser and accessibility', process.execPath, [npm, 'run', 'test:e2e']]
];
fs.mkdirSync(path.join(root, 'reports'), { recursive: true });
const log = path.join(root, 'reports/verify.log');
fs.writeFileSync(log, `Local verification: ${new Date().toISOString()}\n`);
for (const [name, executable, args] of steps) {
  console.log(`Checking: ${name}`);
  const result = spawnSync(executable, args, {
    cwd: root, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, PYTHONUTF8: '1' }
  });
  const output = `${result.stdout || ''}${result.stderr || ''}${result.error?.message || ''}`;
  fs.appendFileSync(log, `\n[${name}]\n${output}`);
  if (result.status !== 0) {
    console.error(output);
    console.error(`FAILED: ${name}. Full log: ${log}`);
    process.exit(result.status || 1);
  }
  console.log(`PASS: ${name}`);
}
console.log(`All local checks passed. Full log: ${log}`);
