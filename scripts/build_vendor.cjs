const path = require('node:path');
const root = path.resolve(__dirname, '..');
require('esbuild').buildSync({
  absWorkingDir: root,
  entryPoints: ['scripts/vendor-mermaid.mjs'],
  outfile: 'assets/lib/mermaid/mermaid.min.js',
  bundle: true,
  minify: true,
  platform: 'browser',
  format: 'iife',
  target: ['es2022'],
  legalComments: 'inline'
});
