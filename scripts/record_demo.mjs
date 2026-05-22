import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs/promises';
import http from 'http';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const videoDir = path.join(root, 'media', 'demo-video-raw');
const finalVideo = path.join(root, 'media', 'shipyard-solver-lab-demo.webm');
const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
};

await fs.rm(videoDir, { recursive: true, force: true });
await fs.mkdir(videoDir, { recursive: true });

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || '/', 'http://localhost');
  const relative = url.pathname === '/' ? '/index.html' : url.pathname;
  const filePath = path.normalize(path.join(root, relative));
  if (!filePath.startsWith(root)) {
    res.writeHead(403);
    res.end('forbidden');
    return;
  }
  try {
    const body = await fs.readFile(filePath);
    res.writeHead(200, { 'content-type': contentTypes[path.extname(filePath)] || 'text/plain' });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end('not found');
  }
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const { port } = server.address();

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1440, height: 1080 },
  recordVideo: {
    dir: videoDir,
    size: { width: 1440, height: 1080 },
  },
});

const page = await context.newPage();
await page.goto(`http://127.0.0.1:${port}/`, { waitUntil: 'networkidle' });
await page.waitForSelector('text=Official Portfolio Candidate');
await page.waitForTimeout(12000);

await page.getByRole('heading', { name: 'Run Boundary' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(12000);
await page.getByRole('heading', { name: 'Official Example Projection' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(14000);
await page.getByRole('heading', { name: 'Official Checker Smoke' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(14000);
await page.getByRole('heading', { name: 'Official Portfolio Candidate' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(16000);
await page.getByRole('heading', { name: 'Official Package' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(12000);
await page.getByRole('heading', { name: 'Yard Layout' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(15000);
await page.getByRole('heading', { name: 'Solution Table' }).scrollIntoViewIfNeeded();
await page.waitForTimeout(15000);
await page.locator('.footer-note').scrollIntoViewIfNeeded();
await page.waitForTimeout(12000);

const video = page.video();
await context.close();
await browser.close();
server.close();

const rawPath = await video.path();
await fs.rm(finalVideo, { force: true });
await fs.rename(rawPath, finalVideo);
await fs.rm(videoDir, { recursive: true, force: true });

console.log('shipyard_solver_demo_video_ok');
console.log(`video=${path.relative(root, finalVideo)}`);
