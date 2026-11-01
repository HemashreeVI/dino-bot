// Trains the Dino's neural network by neuroevolution, inside the real Chrome Dino game.
//
//   node nn/train.js                    train with default settings
//   node nn/train.js --generations 40   train longer
//
// How it works:
//   1. Start with a population of random networks (random weights).
//   2. Each one plays the game a few times. Its fitness is its average score.
//   3. The best few survive unchanged; the rest are replaced by children of good
//      parents (mix two parents' weights, then mutate a few of them a little).
//   4. Repeat. Nobody tells the network what to do; good behaviour just survives.
//
// Training runs on a fake clock, so the game plays hundreds of times faster than
// real time, and several game tabs run in parallel.

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const arg = (name, def) => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? Number(process.argv[i + 1]) : def;
};
const CFG = {
  population: arg('population', 60),
  generations: arg('generations', 100),
  elites: 4,
  tournament: 3,
  mutationRate: 0.12,
  mutationSize: 0.4,
  runsPerBrain: arg('runs', 5),
  maxMinutes: arg('max-minutes', 10),   // game time cap per run
  workers: arg('workers', 4),
  examGames: 20,
  stopAfterPerfect: 10,
};

const NETWORK = fs.readFileSync(path.join(__dirname, 'network.js'), 'utf8');
const OUT_BRAIN = path.join(__dirname, 'brain.json');
const OUT_LOG = path.join(__dirname, 'training-log.json');

// Replaces the page's clock so we decide when each game frame happens.
const fakeClock = () => {
  let now = 0, queue = [];
  performance.now = () => now;
  Date.now = () => 1.7e12 + now;
  window.requestAnimationFrame = cb => { queue.push(cb); return queue.length; };
  window.cancelAnimationFrame = () => {};
  window.__clearFrames = () => { queue = []; };
  window.__frame = before => {
    now += 1000 / 60;
    const cbs = queue; queue = [];
    if (before) before();
    cbs.forEach(cb => cb(now));
  };
};

// Runs inside the page: play `runs` games with these weights, return the scores.
const evaluateInPage = ({ weights, runs, maxFrames }) => {
  const r = DinoNet.game();
  const scores = [];
  let survived = 0;
  for (let n = 0; n < runs; n++) {
    if (!r.crashed) { r.gameOver(); __clearFrames(); }  // restart() only works after a game over
    r.restart();
    let f = 0;
    while (!r.crashed && f < maxFrames) {
      __frame(() => DinoNet.step(weights));
      f++;
    }
    scores.push(r.distanceMeter.getActualDistance(r.distanceRan));
    if (!r.crashed) survived++;
  }
  return { scores, survived };
};

async function openWorker(browser) {
  const page = await browser.newPage();
  await page.addInitScript(fakeClock);
  await page.goto('chrome://dino').catch(() => {});   // the game lives on the error page
  await page.waitForTimeout(300);
  await page.evaluate(NETWORK);
  for (let i = 0; i < 30; i++) await page.evaluate(() => __frame());
  await page.keyboard.press('Space');
  for (let i = 0; i < 240; i++) await page.evaluate(() => __frame()); // let the intro finish
  return page;
}

// ---------------------------------------------------------------- evolution
const SIZE = (() => { const I = 7, H = 8, O = 3; return H * (I + 1) + O * (H + 1); })();
const gauss = () => Math.sqrt(-2 * Math.log(1 - Math.random())) * Math.cos(2 * Math.PI * Math.random());
const randomBrain = () => Array.from({ length: SIZE }, () => gauss());

function pick(pop) {
  let best = null;
  for (let i = 0; i < CFG.tournament; i++) {
    const c = pop[Math.floor(Math.random() * pop.length)];
    if (!best || c.fitness > best.fitness) best = c;
  }
  return best;
}

function child(a, b) {
  return a.weights.map((w, i) => {
    let v = Math.random() < 0.5 ? w : b.weights[i];
    if (Math.random() < CFG.mutationRate) v += gauss() * CFG.mutationSize;
    return v;
  });
}

async function evaluateAll(pages, brains, maxFrames) {
  const results = new Array(brains.length);
  let next = 0;
  await Promise.all(pages.map(async page => {
    while (next < brains.length) {
      const i = next++;
      const { scores, survived } = await page.evaluate(evaluateInPage, { weights: brains[i], runs: CFG.runsPerBrain, maxFrames });
      results[i] = { weights: brains[i], scores, survived, fitness: scores.reduce((s, x) => s + x, 0) / scores.length };
    }
  }));
  return results;
}

(async () => {
  const maxFrames = CFG.maxMinutes * 60 * 60;
  console.log(`Training: ${CFG.population} brains × ${CFG.generations} generations, ` +
    `${CFG.runsPerBrain} games each, up to ${CFG.maxMinutes} game-minutes per game.\n`);

  const browser = await chromium.launch({ channel: 'chromium' });
  const pages = await Promise.all(Array.from({ length: CFG.workers }, () => openWorker(browser)));

  const log = { config: CFG, generations: [] };
  let brains = Array.from({ length: CFG.population }, randomBrain);
  let champion = null;
  let perfectStreak = 0;
  const started = Date.now();

  for (let g = 1; g <= CFG.generations; g++) {
    const pop = (await evaluateAll(pages, brains, maxFrames)).sort((a, b) => b.fitness - a.fitness);
    const best = pop[0];
    const avg = pop.reduce((s, p) => s + p.fitness, 0) / pop.length;
    if (!champion || best.fitness >= champion.fitness) champion = { ...best, generation: g };

    log.generations.push({ generation: g, best: Math.round(best.fitness), average: Math.round(avg),
      bestScores: best.scores, weights: best.weights });
    console.log(`gen ${String(g).padStart(2)}  best ${String(Math.round(best.fitness)).padStart(5)}  ` +
      `avg ${String(Math.round(avg)).padStart(5)}  (${best.scores.join(', ')})  ` +
      `${((Date.now() - started) / 1000).toFixed(0)}s`);

    fs.writeFileSync(OUT_LOG, JSON.stringify(log));
    fs.writeFileSync(OUT_BRAIN, JSON.stringify({ generation: champion.generation,
      fitness: Math.round(champion.fitness), scores: champion.scores, weights: champion.weights }));

    // Stop early once the best brain survives every game to the time cap, 10 generations in a row.
    perfectStreak = best.survived === CFG.runsPerBrain ? perfectStreak + 1 : 0;
    if (perfectStreak >= CFG.stopAfterPerfect) {
      console.log(`\nThe best brain survived every game for ${CFG.stopAfterPerfect} generations in a row. Done!`);
      break;
    }

    const next = pop.slice(0, CFG.elites).map(p => p.weights);
    while (next.length < CFG.population) next.push(child(pick(pop), pick(pop)));
    brains = next;
  }

  // Final exam: the champion plays fresh games it has never seen.
  const examRuns = await Promise.all(pages.map(page =>
    page.evaluate(evaluateInPage, { weights: champion.weights, runs: CFG.examGames / CFG.workers, maxFrames })));
  const exam = examRuns.flatMap(x => x.scores);
  const examSurvived = examRuns.reduce((n, x) => n + x.survived, 0);
  console.log(`\nFinal exam (${exam.length} new games): average ${Math.round(exam.reduce((a, b) => a + b, 0) / exam.length)}, ` +
    `worst ${Math.min(...exam)}, survived the full ${CFG.maxMinutes} minutes in ${examSurvived}/${exam.length}`);
  fs.writeFileSync(OUT_BRAIN, JSON.stringify({ generation: champion.generation,
    fitness: Math.round(champion.fitness), scores: champion.scores, exam, examSurvived, weights: champion.weights }));

  await browser.close();
  console.log(`\nBest brain: generation ${champion.generation}, average score ${Math.round(champion.fitness)}.`);
  console.log(`Saved to ${path.relative(process.cwd(), OUT_BRAIN)}`);
})();
