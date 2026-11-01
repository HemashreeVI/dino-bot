// Opens the Chrome Dino game, starts a bot, and (optionally) records a video.
//
//   node play.js                    the rule-based bot (bot.js)
//   node play.js --brain            the trained neural network (nn/brain.json)
//   node play.js --brain --gen 1    the best network from generation 1 (to compare)
//   node play.js --record           also save a video to ./videos
//   node play.js --seconds 120      stop after 120 seconds (default: 90)
//   node play.js --headless         no visible window (useful with --record)

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const opt = name => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : undefined; };
const record = args.includes('--record');
const headless = args.includes('--headless');
const useBrain = args.includes('--brain');
const generation = opt('gen') && Number(opt('gen'));
const seconds = Number(opt('seconds') || 90);
const size = { width: 1280, height: 720 };

function loadBrain() {
  if (!generation) {
    const b = JSON.parse(fs.readFileSync(path.join(__dirname, 'nn', 'brain.json'), 'utf8'));
    return { weights: b.weights, label: `Neural network · champion of generation ${b.generation}` };
  }
  const log = JSON.parse(fs.readFileSync(path.join(__dirname, 'nn', 'training-log.json'), 'utf8'));
  const g = log.generations.find(x => x.generation === generation);
  return { weights: g.weights, label: `Neural network · generation ${generation}` };
}

// Title and live score drawn on top of the game, so they show in the video.
const overlay = ({ title, subtitle, bottom }) => {
  const box = document.createElement('div');
  box.innerHTML = `
    <div style="font:700 34px system-ui,sans-serif;color:#202124">${title}</div>
    <div style="font:400 20px system-ui,sans-serif;color:#5f6368;margin-top:6px">${subtitle}</div>`;
  box.style.cssText = 'position:fixed;top:28px;left:0;right:0;text-align:center;z-index:9';
  const score = document.createElement('div');
  score.style.cssText = `position:fixed;bottom:${bottom}px;left:0;right:0;text-align:center;` +
    'font:700 40px ui-monospace,monospace;color:#202124;z-index:9';
  document.body.append(box, score);
  const game = () => Runner.getInstance ? Runner.getInstance() : Runner.instance_;
  setInterval(() => {
    const r = game();
    const pts = r.distanceMeter.getActualDistance(r.distanceRan);
    score.textContent = `SCORE ${String(pts).padStart(5, '0')}   SPEED ${r.currentSpeed.toFixed(1)}`;
  }, 100);
};

// Runs the network every frame and draws it: neurons light up as it thinks.
const brainPlayer = weights => {
  const W = 520, H = 210;
  const cv = document.createElement('canvas');
  cv.width = W * 2; cv.height = H * 2;
  cv.style.cssText = `position:fixed;left:50%;transform:translateX(-50%);bottom:24px;width:${W}px;height:${H}px;z-index:9`;
  document.body.append(cv);
  const g = cv.getContext('2d');
  g.scale(2, 2);
  const inNames = ['distance', 'height', 'width', 'speed', 'in air', 'next gap', 'bird?'];
  const col = (x, n, top, bottom) =>
    Array.from({ length: n }, (_, i) => [x, top + (bottom - top) * (n === 1 ? 0.5 : i / (n - 1))]);
  const I = col(110, 7, 14, 196), Hd = col(270, 8, 10, 200), O = col(410, 3, 55, 155);

  function draw(s) {
    g.clearRect(0, 0, W, H);
    let k = 0;
    const line = (a, b, w, act) => {
      const alpha = Math.min(0.9, Math.abs(w * act) * 0.45 + 0.05);
      g.strokeStyle = w > 0 ? `rgba(65,105,225,${alpha})` : `rgba(220,110,60,${alpha})`;
      g.lineWidth = Math.min(3, Math.abs(w) * 0.7 + 0.3);
      g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke();
    };
    for (let h = 0; h < DinoNet.HIDDEN; h++) {
      k++;
      for (let i = 0; i < DinoNet.INPUTS; i++) line(I[i], Hd[h], weights[k++], s.x[i]);
    }
    for (let o = 0; o < DinoNet.OUTPUTS; o++) {
      k++;
      for (let h = 0; h < DinoNet.HIDDEN; h++) line(Hd[h], O[o], weights[k++], s.hidden[h]);
    }
    const dot = (p, v, r) => {
      g.fillStyle = '#fff'; g.strokeStyle = '#202124'; g.lineWidth = 1.5;
      g.beginPath(); g.arc(p[0], p[1], r, 0, 7); g.fill(); g.stroke();
      g.fillStyle = `rgba(32,33,36,${Math.min(1, Math.abs(v))})`;
      g.beginPath(); g.arc(p[0], p[1], r - 3, 0, 7); g.fill();
    };
    g.font = '12px ui-monospace,monospace'; g.textAlign = 'right'; g.textBaseline = 'middle';
    I.forEach((p, i) => { dot(p, s.x[i], 7); g.fillStyle = '#5f6368'; g.fillText(inNames[i], p[0] - 13, p[1]); });
    Hd.forEach((p, h) => dot(p, s.hidden[h], 7));
    g.textAlign = 'left'; g.font = '700 16px ui-monospace,monospace';
    O.forEach((p, o) => {
      const on = o === s.choice;
      dot(p, on ? 1 : 0.1, 10);
      g.fillStyle = on ? '#2f54c8' : '#b0b4b8';
      g.fillText(DinoNet.ACTIONS[o], p[0] + 17, p[1]);
    });
  }

  let last = null;
  const loop = () => {
    const s = DinoNet.step(weights);
    if (s) last = s;
    if (last) draw(last);
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
};

(async () => {
  const brain = useBrain && loadBrain();
  const browser = await chromium.launch({ channel: 'chromium', headless });
  const context = await browser.newContext({
    viewport: size,
    ...(record && { recordVideo: { dir: path.join(__dirname, 'videos'), size } }),
  });
  const page = await context.newPage();

  // chrome://dino "fails" to load on purpose: the game lives on the error page.
  await page.goto('chrome://dino').catch(() => {});
  await page.waitForTimeout(1000);
  if (brain) {
    await page.evaluate(overlay, { title: brain.label, bottom: 245,
      subtitle: 'Nobody wrote its rules: it learned to play through evolution' });
    await page.evaluate(fs.readFileSync(path.join(__dirname, 'nn', 'network.js'), 'utf8'));
    await page.evaluate(brainPlayer, brain.weights);
  } else {
    await page.evaluate(overlay, { title: 'This Dino is playing itself', bottom: 60,
      subtitle: 'A small JavaScript bot reads the game state and decides when to jump or duck' });
    await page.evaluate(fs.readFileSync(path.join(__dirname, 'bot.js'), 'utf8'));
  }
  await page.waitForTimeout(1500);
  await page.keyboard.press('Space');

  const start = Date.now();
  let result;
  while (Date.now() - start < seconds * 1000) {
    await page.waitForTimeout(500);
    result = await page.evaluate(() => {
      const r = Runner.getInstance ? Runner.getInstance() : Runner.instance_;
      return { score: r.distanceMeter.getActualDistance(r.distanceRan), crashed: r.crashed };
    });
    if (result.crashed) break;
  }
  await page.waitForTimeout(1500);
  console.log(`Score: ${result.score}${result.crashed ? ' (crashed)' : ' (still running)'}`);

  const video = page.video();
  await context.close();
  await browser.close();
  if (video) console.log('Video saved to', await video.path());
})();
