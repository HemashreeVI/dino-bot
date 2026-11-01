<p align="center">
  <img src="https://img.shields.io/badge/JAVASCRIPT-4169E1?style=flat-square&labelColor=0A1024&logo=javascript&logoColor=EAEEFA" alt="JavaScript">
  <img src="https://img.shields.io/badge/PLAYWRIGHT-4169E1?style=flat-square&labelColor=0A1024" alt="Playwright">
  <img src="https://img.shields.io/badge/NEURAL_NETWORK-NEUROEVOLUTION-4169E1?style=flat-square&labelColor=0A1024" alt="Neural network trained by neuroevolution">
  <img src="https://img.shields.io/badge/BEST_SCORE-7,899-F5B461?style=flat-square&labelColor=0A1024" alt="Best score 7,899">
  <img src="https://img.shields.io/badge/CRASHES-0-8EA8FF?style=flat-square&labelColor=0A1024" alt="Crashes 0">
  <img src="https://img.shields.io/badge/LICENSE-MIT-8EA8FF?style=flat-square&labelColor=0A1024" alt="MIT license">
</p>

<img src="./assets/cards/hero.svg" width="100%" alt="DINO BOT: the Chrome Dino, on autopilot. A 44-line bot that jumps cactuses and ducks under birds. 7,899 points, 0 crashes, top speed 13.0.">

<p align="center">
  <a href="#-try-it-in-your-browser"><img src="https://img.shields.io/badge/▶_Try_it-in_your_browser-4169E1?style=for-the-badge&labelColor=0A1024" alt="Try it in your browser"></a>
  <a href="media/dino-bot.mp4"><img src="https://img.shields.io/badge/🎥_Watch-full_video-4169E1?style=for-the-badge&labelColor=0A1024" alt="Watch the full video"></a>
  <a href="https://github.com/HemashreeVI"><img src="https://img.shields.io/badge/More_by-HemashreeVI-4169E1?style=for-the-badge&labelColor=0A1024&logo=github&logoColor=EAEEFA" alt="More projects by HemashreeVI"></a>
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

<img src="./assets/cards/title-nn.svg" width="100%" alt="06 Neural network: It learned by itself.">

<p align="center">
  <img src="media/nn-demo.gif" width="100%" alt="The trained neural network playing the Chrome Dino game. Below the game, its neurons light up live as it decides to jump, duck or run.">
</p>

Then I asked a harder question: **can it learn to play without any rules at all?**

The second bot is a tiny neural network. It sees 7 numbers about the game (how far away the next obstacle is, how high and wide it is, the speed, and so on) and picks one of 3 actions: **JUMP**, **DUCK** or **RUN**. At the start its weights are random, so it plays terribly.

<img src="./assets/cards/network.svg" width="100%" alt="The trained network: 7 inputs (distance, height, width, speed, in air, next gap, bird?), 8 hidden neurons and 3 outputs (jump, duck, run).">

It learns through **neuroevolution**, the same family of ideas as NEAT:

1. 60 random brains each play the real Chrome Dino game 5 times. Their score is their fitness.
2. The 4 best survive unchanged. The rest are replaced by "children": two good parents' weights mixed together, with a few small random mutations.
3. Repeat, generation after generation. Nobody tells it what to do; good behaviour simply survives.

<img src="./assets/cards/curve.svg" width="100%" alt="Learning curve: the best brain's score per generation, from almost nothing to the 10-minute cap.">

> **Training trick:** the game normally runs in real time, which would make training take days. `nn/train.js` swaps the page's clock for a fake one and drives the game frame by frame, so it runs **hundreds of times faster** than real time, in 4 tabs at once.

<img src="./assets/cards/title-versus.svg" width="100%" alt="07 Showdown: Rules vs brain.">
<img src="./assets/cards/versus.svg" width="100%" alt="Rule-based bot versus evolved neural network, each playing the same 20-game exam with a 10-minute cap: the rules survived 20 of 20 games, the neural network 17 of 20.">

Same exam for both: 20 games each, on the same fast-forwarded clock, up to 10 minutes per game (`node nn/exam.js`).
**The hand-written rules still win, but only just.** The network figured out almost everything by itself, starting from random numbers, in 31 generations. 🦖

### 🧠 Train your own brain

```bash
node nn/train.js            # evolve a new brain (a few minutes)
node nn/export.js           # pack it into nn/nn-bot.js
node play.js --brain        # watch it play, with its neurons lighting up
node play.js --brain --gen 1   # compare with the clueless generation-1 brain
node nn/exam.js             # the showdown: rules vs brain, same 20 games
```

Or, without installing anything: paste [`nn/nn-bot.js`](nn/nn-bot.js) into the console on `chrome://dino` and press Space.

<details>
<summary><b>📁 What's in the repo</b></summary>
<br/>

| File | What it does |
| --- | --- |
| [`bot.js`](bot.js) | The bot. Paste it into the console, or let `play.js` inject it. |
| [`play.js`](play.js) | Opens the game, starts a bot (`--brain` for the neural network), records a video. |
| [`nn/network.js`](nn/network.js) | The neural network: what it sees, how it thinks, how it presses keys. |
| [`nn/train.js`](nn/train.js) | Neuroevolution training in the real game, on a fast-forwarded clock. |
| [`nn/brain.json`](nn/brain.json) | The trained brain (its weights). |
| [`nn/training-log.json`](nn/training-log.json) | Scores for every generation, plus each generation's best brain. |
| [`nn/exam.js`](nn/exam.js) | The fair showdown between the two bots. |
| [`nn/nn-bot.js`](nn/nn-bot.js) | The trained brain as one file to paste into the console. |
| [`scripts/build_cards.py`](scripts/build_cards.py) | Generates the cards in this README (`python3 scripts/build_cards.py`). |
| [`media/`](media) | The demo GIF and the full video. |

</details>

<a href="https://github.com/HemashreeVI"><img src="./assets/cards/footer.svg" width="100%" alt="Dino Bot. Made by Hemashree, B.Tech CSE, VIT Chennai. If it made you smile, leave a star."></a>
