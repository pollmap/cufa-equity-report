#!/usr/bin/env node
/**
 * CUFA 다이어그램 PNG 스크린샷
 * Usage: node screenshot.js <input.html> <output.png>
 */
const { chromium } = require('playwright');
const fs = require('fs');

const [,, htmlPath, pngPath] = process.argv;
if (!htmlPath || !pngPath) {
  console.error('Usage: node screenshot.js <input.html> <output.png>');
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 800, height: 3000 },
    deviceScaleFactor: 2
  });
  const html = fs.readFileSync(htmlPath, 'utf8');
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);

  const card = await page.$('.card');
  if (!card) {
    console.error('Error: .card element not found');
    process.exit(1);
  }
  await card.screenshot({ path: pngPath, type: 'png' });
  const sz = fs.statSync(pngPath).size;
  console.log(`✅ ${pngPath} (${Math.round(sz / 1024)}KB)`);
  await browser.close();
})();
