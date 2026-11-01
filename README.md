# 🦖 Dino Bot

A small bot that plays the Chrome Dino game by itself: it jumps over cactuses, ducks under birds and keeps going at the game's top speed.

![Dino bot playing](media/demo.gif)

Full video: [media/dino-bot.mp4](media/dino-bot.mp4)

## How it works

Instead of looking at the screen, the bot reads the game's own state from the page. About 200 times a second it:

1. Finds the next obstacle in front of the dino.
2. Works out how far away it is.
3. Decides what to do:
   - **Cactus or low bird:** jump.
   - **Mid-height bird:** duck under it.
   - **High bird:** keep running, it flies overhead.
4. Once the obstacle is behind it, it drops back to the ground quickly so it's ready for the next one.

The game keeps getting faster, so the bot reacts earlier as speed goes up: the trigger distance is `speed × 13`.

## Try it in your browser (no install)

1. Open `chrome://dino` in Chrome.
2. Press `F12` and open the **Console** tab.
3. Paste the contents of [`bot.js`](bot.js) and press Enter.
4. Click the game and press Space.

To stop it, run `stopDinoBot()` in the console.

## Run it automatically and record a video

Needs [Node.js](https://nodejs.org).

```bash
npm install
npx playwright install chromium
node play.js                      # watch it play
node play.js --record --headless  # save a video to ./videos
node play.js --seconds 300        # play for 5 minutes (default: 90 seconds)
```

`play.js` uses [Playwright](https://playwright.dev) to open Chromium, load the game, add the bot and press Space. Videos are saved as `.webm`. To turn one into an `.mp4`:

```bash
ffmpeg -i videos/<file>.webm -c:v libx264 -pix_fmt yuv420p media/dino-bot.mp4
```

## Problems I ran into

- **The game speeds up.** A fixed jump distance works early on and fails later, so the bot's reaction distance grows with speed.
- **Birds fly at three heights.** Jumping into a mid-height bird ends the game, so the bot has to tell the heights apart.
- **Long jumps at high speed.** The bot sometimes landed right on the next cactus. Making it drop back down once it has cleared an obstacle fixed this.
- **Different Chrome versions.** Newer Chrome uses `Runner.getInstance()`; older versions use `Runner.instance_`. The bot supports both.

## Ideas for next steps

- A version that only uses screenshots, so it works without reading the game's code.
- Train a neural network (for example with NEAT) to learn the game by itself, and compare it with this rule-based bot.

## License

MIT
