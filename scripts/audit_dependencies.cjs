/* Preserve audit evidence without installing or changing the upstream theme. */
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
fs.mkdirSync(path.join(root, 'reports'), { recursive: true });
let rootFailed = false;
for (const [name, args] of [['dependency', ['audit', '--json']], ['theme', ['audit', '--prefix', 'themes/blowfish', '--json']]]) {
  const result = spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', args, {
    cwd: root, encoding: 'utf8', shell: process.platform === 'win32', maxBuffer: 8 * 1024 * 1024
  });
  try {
    const report = JSON.parse(result.stdout);
    if (!report.metadata) throw new Error('Audit response has no metadata');
    fs.writeFileSync(path.join(root, `reports/${name}-audit.json`), JSON.stringify(report, null, 2));
    console.log(`${name}: ${JSON.stringify(report.metadata.vulnerabilities)}`);
    if (name === 'dependency') rootFailed = report.metadata.vulnerabilities.total > 0;
    if (name === 'theme') {
      for (const key of ['mermaid', 'dompurify', 'katex', 'lodash-es']) {
        const entry = report.vulnerabilities[key];
        if (entry) console.log(`${key}: ${entry.severity}, affected ${entry.range}`);
      }
    }
  } catch (error) {
    console.error(`${name} audit could not complete: ${error.message}`);
    rootFailed = true;
  }
}
process.exit(rootFailed ? 1 : 0);
