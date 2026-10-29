const { test, expect } = require('@playwright/test');
const { AxeBuilder } = require('@axe-core/playwright');
const fs = require('node:fs');

async function appearance(page, mode) {
  await page.addInitScript((value) => localStorage.setItem('appearance', value), mode);
  await page.emulateMedia({ colorScheme: mode });
}

test('homepage navigation, theme, responsive layout and accessibility', async ({ page }, info) => {
  const failures = [];
  page.on('pageerror', error => failures.push(error.message));
  await appearance(page, 'light');
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('保持好奇');
  await expect(page.getByRole('link', { name: '进入文章归档' })).toHaveAttribute('href', '/posts/');
  await expect(page.locator('.topic-card')).toHaveCount(5);
  const width = await page.evaluate(() => ({ actual: document.documentElement.scrollWidth, available: innerWidth }));
  expect(width.actual).toBeLessThanOrEqual(width.available + 1);
  expect(await page.locator('body').evaluate(el => getComputedStyle(el).backgroundColor)).toBe('rgb(255, 255, 255)');
  const toggle = info.project.name === 'mobile' ? '#appearance-switcher-mobile' : '#appearance-switcher';
  await page.locator(toggle).click();
  await expect(page.locator('html')).toHaveClass(/dark/);
  expect(await page.locator('body').evaluate(el => getComputedStyle(el).backgroundColor)).toBe('rgb(30, 41, 59)');
  const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(axe.violations).toEqual([]);
  await page.screenshot({ path: `reports/home-${info.project.name}-dark.png`, fullPage: true });
  await page.locator(toggle).click();
  await page.screenshot({ path: `reports/home-${info.project.name}-light.png`, fullPage: true });
  expect(failures).toEqual([]);
});

test('search finds a legacy article', async ({ page }, info) => {
  await page.goto('/');
  await page.locator(info.project.name === 'mobile' ? '#search-button-mobile' : '#search-button').click();
  await page.locator('#search-query').fill('PCL2');
  await expect(page.locator('#search-results a').first()).toContainText('PCL2');
  await page.locator('#search-results a').first().click();
  await expect(page).toHaveURL(/posts\/pcl2-memory-optimization/);
});

test('article code, math, image zoom, progress, taxonomy and anchor', async ({ page }, info) => {
  await page.goto('/writing/');
  await expect(page.locator('.katex').first()).toBeVisible();
  await expect(page.locator('.highlight')).toBeVisible();
  await expect(page.locator('.copy-button')).toBeAttached();
  await page.locator('.article-content img').first().click();
  await expect(page.locator('.medium-zoom-image--opened')).toBeVisible();
  await page.keyboard.press('Escape');
  await page.locator('.article-content a[href="#代码"]').click();
  await expect(page).toHaveURL(/#%E4%BB%A3%E7%A0%81|#代码/);
  await page.evaluate(() => scrollTo(0, document.body.scrollHeight));
  await expect.poll(() => page.locator('.reading-progress').evaluate(el => el.value)).toBeGreaterThan(90);
  await page.screenshot({ path: `reports/reading-${info.project.name}.png`, fullPage: true });
  await page.goto('/posts/how-build-blog/');
  await expect(page.locator('#TableOfContents')).toBeAttached();
  await expect(page.locator('a[href*="/tags/hugo/"]').first()).toBeVisible();
  const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect(axe.violations).toEqual([]);
});

test('primary routes, metadata, projects and mobile menu', async ({ page }, info) => {
  for (const path of ['/posts/', '/projects/', '/projects/personal-blog/', '/about/', '/links/', '/categories/', '/tags/']) {
    const response = await page.goto(path);
    expect(response.status()).toBe(200);
    await expect(page.locator('h1')).toHaveCount(1);
    await expect(page.locator('link[rel="canonical"]')).toBeAttached();
    expect(await page.locator('meta[name="description"]').getAttribute('content')).toBeTruthy();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
    expect(overflow, path).toBeFalsy();
  }
  await page.goto('/projects/');
  await expect(page.getByRole('heading', { name: '个人博客与自动化发布系统' })).toBeVisible();
  if (info.project.name === 'mobile') {
    await page.locator('label[for="mobile-menu-toggle"]').first().click();
    await expect(page.locator('[role="dialog"]')).toBeVisible();
    await page.locator('[role="dialog"]').getByRole('link', { name: 'About', exact: true }).click();
    await expect(page).toHaveURL(/\/about\//);
  }
  fs.mkdirSync('reports', { recursive: true });
  await page.screenshot({ path: `reports/about-${info.project.name}.png`, fullPage: true });
});
