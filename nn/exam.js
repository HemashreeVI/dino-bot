// A fair showdown: the rule-based bot and the trained neural network play the
// same number of games under the same conditions (fast-forwarded clock, time cap).
//
//   node nn/exam.js                 20 games each, 10 game-minutes max per game
//   node nn/exam.js --games 40

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const arg = (name, def) => { const i = process.argv.indexOf(`--${name}`); return i >= 0 ? Number(process.argv[i + 1]) : def; };
const GAMES = arg('games', 20), MINUTES = arg('max-minutes', 10), WORKERS = 4;
const ROOT = path.join(__dirname, '..');

// Same fake clock as training. setInterval is captured too, so bot.js runs once per frame.
const fakeClock = () => {
  let now = 0, queue = [];
  window.__ticks = [];
  performance.now = () => now;
  Date.now = () => 1.7e12 + now;
  window.requestAnimationFrame = cb => { queue.push(cb); return queue.length; };
  window.cancelAnimationFrame = () => {};
  window.setInterval = fn => { window.__ticks.push(fn); return window.__ticks.length; };
  window.clearInterval = () => {};
  window.__clearFrames = () => { queue = []; };
  window.__frame = before => {
    now += 1000 / 60;
    const cbs = queue; queue = [];
    if (before) before();
    cbs.forEach(cb => cb(now));
  };
};

const playGames = ({ kind, weights, games, maxFrames }) => {
  const r = DinoNet.game();
  const think = kind === 'rules' ? () => __ticks.forEach(t => t()) : () => DinoNet.step(weights);
  const scores = [];
  let survived = 0;
  for (let n = 0; n < games; n++) {
    if (!r.crashed) { r.gameOver(); __clearFrames(); }
    r.restart();
    let f = 0;
    while (!r.crashed && f < maxFrames) { __frame(think); f++; }
    scores.push(r.distanceMeter.getActualDistance(r.distanceRan));
    if (!r.crashed) survived++;
  }
  return { scores, survived };
};

async function openPage(browser, kind) {
  const page = await browser.newPage();
  await page.addInitScript(fakeClock);
  await page.goto('chrome://dino').catch(() => {});
  await page.waitForTimeout(300);
  await page.evaluate(fs.readFileSync(path.join(__dirname, 'network.js'), 'utf8'));
  if (kind === 'rules') await page.evaluate(fs.readFileSync(path.join(ROOT, 'bot.js'), 'utf8'));
  for (let i = 0; i < 30; i++) await page.evaluate(() => __frame());
  await page.keyboard.press('Space');
  for (let i = 0; i < 240; i++) await page.evaluate(() => __frame());
  return page;
}

(async () => {
  const browser = await chromium.launch({ channel: 'chromium' });
  const { weights } = JSON.parse(fs.readFileSync(path.join(__dirname, 'brain.json'), 'utf8'));
  const maxFrames = MINUTES * 3600;
  const results = {};
  for (const kind of ['rules', 'brain']) {
    const pages = await Promise.all(Array.from({ length: WORKERS }, () => openPage(browser, kind)));
    const parts = await Promise.all(pages.map(p =>
      p.evaluate(playGames, { kind, weights, games: GAMES / WORKERS, maxFrames })));
    await Promise.all(pages.map(p => p.close()));
    const scores = parts.flatMap(x => x.scores);
    const survived = parts.reduce((n, x) => n + x.survived, 0);
    results[kind] = { games: scores.length, average: Math.round(scores.reduce((a, b) => a + b, 0) / scores.length),
      worst: Math.min(...scores), survived, scores };
    console.log(`${kind === 'rules' ? 'Rule-based bot ' : 'Neural network '}: average ${results[kind].average}, ` +
      `worst ${results[kind].worst}, survived all ${MINUTES} minutes in ${survived}/${scores.length} games`);
  }
  fs.writeFileSync(path.join(__dirname, 'exam-results.json'), JSON.stringify({ minutes: MINUTES, ...results }, null, 1));
  await browser.close();
})();
