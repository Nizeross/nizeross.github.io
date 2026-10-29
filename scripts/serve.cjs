/* Loopback-only static server for deterministic browser checks. */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../.build/site');
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.xml': 'application/xml', '.woff2': 'font/woff2', '.woff': 'font/woff' };
const server = http.createServer((req, res) => {
  let file;
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    file = path.resolve(root, '.' + pathname);
    if (file !== root && !file.startsWith(root + path.sep)) throw new Error('Invalid path');
    if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    const bytes = fs.readFileSync(file);
    res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
    res.end(bytes);
  } catch {
    res.writeHead(404, { 'content-type': 'text/plain' }); res.end('Not found');
  }
}).listen(4173, '127.0.0.1', () => console.log('Local preview: http://127.0.0.1:4173'));
module.exports = server;
