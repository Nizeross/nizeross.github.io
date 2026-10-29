const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const env = { ...process.env, PLAYWRIGHT_BROWSERS_PATH: path.join(root, '.cache/playwright') };
const cli = path.join(path.dirname(require.resolve('playwright/package.json')), 'cli.js');
const result = spawnSync(process.execPath, [cli, 'install', 'chromium', ...process.argv.slice(2)], { cwd: root, env, stdio: 'inherit' });
process.exit(result.status ?? 1);
