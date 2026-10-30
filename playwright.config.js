process.env.PLAYWRIGHT_BROWSERS_PATH ||= require('node:path').join(__dirname, '.cache/playwright');
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }], ['json', { outputFile: 'reports/browser-results.json' }]],
  use: { baseURL: 'http://127.0.0.1:4173', channel: 'chromium', trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  webServer: process.env.BLOG_TEST_SERVER === 'managed' ? undefined : {
    command: 'node scripts/serve.cjs',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: false
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1080 } } },
    { name: 'mobile', use: { ...devices['iPhone 13'], defaultBrowserType: 'chromium' } }
  ]
});
