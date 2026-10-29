const path = require('node:path');
const { spawn } = require('node:child_process');
const server = require('./serve.cjs');
const cli = path.join(path.dirname(require.resolve('@playwright/test/package.json')), 'cli.js');
server.on('error', error => { console.error(error.message); process.exit(1); });
server.on('listening', () => {
  const child = spawn(process.execPath, [cli, 'test', ...process.argv.slice(2)], {
    cwd: path.resolve(__dirname, '..'),
    env: { ...process.env, BLOG_TEST_SERVER: 'managed' },
    stdio: 'inherit'
  });
  child.on('error', error => { console.error(error.message); server.close(() => process.exit(1)); });
  child.on('exit', code => { server.close(() => process.exit(code ?? 1)); });
});
