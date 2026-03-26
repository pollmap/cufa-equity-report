#!/usr/bin/env node
/**
 * CUFA 다이어그램 배치 PNG 스크린샷
 * Usage: node batch_screenshot.js <html_dir> <png_dir>
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [,, htmlDir, pngDir] = process.argv;
if (!htmlDir || !pngDir) {
  console.error('Usage: node batch_screenshot.js <html_dir> <png_dir>');
  process.exit(1);
}

fs.mkdirSync(pngDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const files = fs.readdirSync(htmlDir)
    .filter(f => f.endsWith('.html')).sort();

  console.log(`Processing ${files.length} files...`);

  for (const file of files) {
    const page = await browser.newPage({
      viewport: { width: 800, height: 3000 },
      deviceScaleFactor: 2
    });
    const html = fs.readFileSync(path.join(htmlDir, file), 'utf8');
    await page.setContent(html, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    const card = await page.$('.card');
    if (!card) { console.warn(`⚠️ ${file}: .card not found, skipping`); continue; }

    const pngName = file.replace('.html', '.png');
    await card.screenshot({ path: path.join(pngDir, pngName), type: 'png' });
    const sz = fs.statSync(path.join(pngDir, pngName)).size;
    console.log(`  ✅ ${pngName} (${Math.round(sz / 1024)}KB)`);
    await page.close();
  }
  await browser.close();
  console.log(`Done! ${files.length} PNGs saved to ${pngDir}`);
})();
