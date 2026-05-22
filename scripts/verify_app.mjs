import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import http from 'http';
import fs from 'fs/promises';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
};

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
const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });

await page.goto(`http://127.0.0.1:${port}/`);
await page.waitForSelector('text=Shipyard Solver Lab');
await page.waitForSelector('#solutionTable tbody tr');
const title = await page.title();
if (!title.includes('Shipyard Solver Lab')) {
  throw new Error(`unexpected title: ${title}`);
}

const rows = await page.locator('#solutionTable tbody tr').count();
if (rows < 10) {
  throw new Error(`expected at least 10 solution rows, got ${rows}`);
}
const body = await page.locator('body').textContent();
if (!body.includes('One-Sentence Pitch') || !body.includes('solve-validate-package loop') || !body.includes('Judge Signal')) {
  throw new Error('missing one-sentence judge hook');
}
if (!body.includes('Beam search')) {
  throw new Error('missing beam search explanation');
}
if (!body.includes('candidates validated')) {
  throw new Error('missing benchmark validation trail');
}
if (!body.includes('Official Example Projection') || !body.includes('Not official feasibility scoring')) {
  throw new Error('missing official example projection boundary');
}
if (!body.includes('Official Checker Smoke') || !body.includes('Exact official checker PASS')) {
  throw new Error('missing official checker smoke proof');
}
if (!body.includes('Official Portfolio Candidate') || !body.includes('Candidate official algorithm PASS')) {
  throw new Error('missing official portfolio candidate proof');
}
if (!body.includes('1024 bay assignments') || !body.includes('matches the static bound')) {
  throw new Error('missing official portfolio static-bound proof');
}
if (!body.includes('Official Package') || !body.includes('outputs/official_submission_candidate.zip')) {
  throw new Error('missing official submission package proof');
}

await page.getByRole('button', { name: '日本語' }).click();
const japaneseBody = await page.locator('body').innerText();
if (!japaneseBody.includes('造船所ソルバーラボ') || !japaneseBody.includes('解く・検証する・提出パッケージ化する')) {
  throw new Error('Japanese UI toggle failed');
}
for (const marker of ['最高実行はベースラインより', '公式チェッカーがPASSしました', '公式形式の候補アルゴリズムがPASSしました', 'いいえ']) {
  if (!japaneseBody.includes(marker)) {
    throw new Error(`Japanese dynamic UI missing marker: ${marker}`);
  }
}
for (const leaked of ['candidates validated', 'Exact official checker PASS', 'Candidate official algorithm PASS', '>yes<']) {
  if (japaneseBody.includes(leaked)) {
    throw new Error(`Japanese UI leaked English dynamic text: ${leaked}`);
  }
}

await page.screenshot({ path: path.join(root, 'media', 'shipyard-solver-lab-full.png'), fullPage: true });
await browser.close();
server.close();

console.log('shipyard_solver_app_verify_ok');
console.log(`rows=${rows}`);
console.log('screenshot=media/shipyard-solver-lab-full.png');
