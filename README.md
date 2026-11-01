<p align="center">
  <img src="https://img.shields.io/badge/JAVASCRIPT-2FBF71?style=flat-square&labelColor=0C1712&logo=javascript&logoColor=E8F1EC" alt="JavaScript">
  <img src="https://img.shields.io/badge/PLAYWRIGHT-2FBF71?style=flat-square&labelColor=0C1712" alt="Playwright">
  <img src="https://img.shields.io/badge/BEST_SCORE-7,899-F5B461?style=flat-square&labelColor=0C1712" alt="Best score 7,899">
  <img src="https://img.shields.io/badge/CRASHES-0-7FE0A8?style=flat-square&labelColor=0C1712" alt="Crashes 0">
  <img src="https://img.shields.io/badge/LICENSE-MIT-7FE0A8?style=flat-square&labelColor=0C1712" alt="MIT license">
</p>

<img src="./assets/cards/hero.svg" width="100%" alt="DINO BOT: the Chrome Dino, on autopilot. A 44-line bot that jumps cactuses and ducks under birds. 7,899 points, 0 crashes, top speed 13.0.">

<p align="center">
  <a href="#-try-it-in-your-browser"><img src="https://img.shields.io/badge/▶_Try_it-in_your_browser-2FBF71?style=for-the-badge&labelColor=0C1712" alt="Try it in your browser"></a>
  <a href="media/dino-bot.mp4"><img src="https://img.shields.io/badge/🎥_Watch-full_video-2FBF71?style=for-the-badge&labelColor=0C1712" alt="Watch the full video"></a>
  <a href="https://github.com/HemashreeVI"><img src="https://img.shields.io/badge/More_by-HemashreeVI-2FBF71?style=for-the-badge&labelColor=0C1712&logo=github&logoColor=E8F1EC" alt="More projects by HemashreeVI"></a>
</p>

<img src="./assets/cards/title-demo.svg" width="100%" alt="01 Demo: Watch it play.">

<p align="center">
  <img src="media/demo.gif" width="100%" alt="The bot playing the Chrome Dino game at top speed: jumping cactuses and ducking under birds.">
</p>

<img src="./assets/cards/stats.svg" width="100%" alt="Results: 7,899 points in 7 minutes with 0 crashes; top game speed 13.0 reached; 200 decisions per second; 44 lines of JavaScript.">

<img src="./assets/cards/title-how.svg" width="100%" alt="02 How it works: Read, decide, act.">
<img src="./assets/cards/loop.svg" width="100%" alt="Read the game state (next obstacle, type, distance, height, speed), decide what to do (react at speed × 13: jump, duck or keep running), act (startJump, setDuck, drop fast after clearing). Repeats every 5 milliseconds.">

<img src="./assets/cards/title-rules.svg" width="100%" alt="03 The rules: Jump, duck or run.">
<img src="./assets/cards/rules.svg" width="100%" alt="Cactus: jump. Low bird: jump. Mid bird: duck. High bird: keep running.">

<img src="./assets/cards/title-try.svg" width="100%" alt="04 Try it: Run it yourself.">

### ▶ Try it in your browser

No install needed:

1. Open `chrome://dino` in Chrome.
2. Press `F12` and open the **Console** tab.
3. Paste the contents of [`bot.js`](bot.js) and press Enter.
4. Click the game and press Space. Then sit back. 🍿

To stop it, run `stopDinoBot()`.

### 🎥 Run it with Node and record a video

```bash
npm install
npx playwright install chromium
node play.js                      # watch it play
node play.js --record --headless  # save a video to ./videos
node play.js --seconds 300        # play for 5 minutes (default: 90 s)
```

`play.js` uses [Playwright](https://playwright.dev) to open Chromium, load the game, inject the bot and press Space. To turn a `.webm` recording into an `.mp4`:

```bash
ffmpeg -i videos/<file>.webm -c:v libx264 -pix_fmt yuv420p media/dino-bot.mp4
```

<img src="./assets/cards/title-lessons.svg" width="100%" alt="05 Lessons: Problems I ran into, and what's next.">
<img src="./assets/cards/lessons.svg" width="100%" alt="Solved: the game speeds up (the bot reacts earlier as speed grows); birds at three heights (heights are checked); long jumps at top speed (drops fast once clear); different Chrome versions (supports Runner.getInstance and Runner.instance_). Next: a screen-only version, and a NEAT neural network to race against this bot.">

<details>
<summary><b>📁 What's in the repo</b></summary>
<br/>

| File | What it does |
| --- | --- |
| [`bot.js`](bot.js) | The bot. Paste it into the console, or let `play.js` inject it. |
| [`play.js`](play.js) | Opens the game, starts the bot, records a video. |
| [`scripts/build_cards.py`](scripts/build_cards.py) | Generates the cards in this README (`python3 scripts/build_cards.py`). |
| [`media/`](media) | The demo GIF and the full video. |

</details>

<a href="https://github.com/HemashreeVI"><img src="./assets/cards/footer.svg" width="100%" alt="Dino Bot. Made by Hemashree, B.Tech CSE, VIT Chennai. If it made you smile, leave a star."></a>
