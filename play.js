// Opens the Chrome Dino game, starts the bot, and (optionally) records a video.
//
//   node play.js                 watch the bot play in a browser window
//   node play.js --record        also save a video to ./videos
//   node play.js --seconds 120   stop after 120 seconds (default: 90)
//   node play.js --headless      no visible window (useful with --record)

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const record = args.includes('--record');
const headless = args.includes('--headless');
const secondsArg = args.indexOf('--seconds');
const seconds = secondsArg >= 0 ? Number(args[secondsArg + 1]) : 90;
const size = { width: 1280, height: 720 };

// Title and live score drawn on top of the game, so they show in the video.
const overlay = () => {
  const box = document.createElement('div');
  box.innerHTML = `
    <div style="font:700 34px system-ui,sans-serif;color:#202124">This Dino is playing itself</div>
    <div style="font:400 20px system-ui,sans-serif;color:#5f6368;margin-top:6px">
      A small JavaScript bot reads the game state and decides when to jump or duck</div>`;
  box.style.cssText = 'position:fixed;top:28px;left:0;right:0;text-align:center;z-index:9';
  const score = document.createElement('div');
  score.style.cssText = 'position:fixed;bottom:60px;left:0;right:0;text-align:center;' +
    'font:700 44px ui-monospace,monospace;color:#202124;z-index:9';
  document.body.append(box, score);
  const game = () => Runner.getInstance ? Runner.getInstance() : Runner.instance_;
  setInterval(() => {
    const r = game();
    const pts = r.distanceMeter.getActualDistance(r.distanceRan);
    score.textContent = `SCORE ${String(pts).padStart(5, '0')}   SPEED ${r.currentSpeed.toFixed(1)}`;
  }, 100);
};

(async () => {
  const browser = await chromium.launch({ channel: 'chromium', headless });
  const context = await browser.newContext({
    viewport: size,
    ...(record && { recordVideo: { dir: path.join(__dirname, 'videos'), size } }),
  });
  const page = await context.newPage();

  // chrome://dino "fails" to load on purpose: the game lives on the error page.
  await page.goto('chrome://dino').catch(() => {});
  await page.waitForTimeout(1000);
  await page.evaluate(overlay);
  await page.evaluate(fs.readFileSync(path.join(__dirname, 'bot.js'), 'utf8'));
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
