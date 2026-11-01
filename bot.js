// Chrome Dino auto-player.
// Paste this into the DevTools console on chrome://dino (or the offline page),
// then press Space to start. Run `stopDinoBot()` to turn it off.
(() => {
  const game = () =>
    typeof Runner.getInstance === 'function' ? Runner.getInstance() : Runner.instance_;

  const TREX_WIDTH = 44;
  const LOOK_AHEAD = 13;     // how many frames ahead we react (scaled by speed)
  const BIRD_HIGH_Y = 60;    // birds above this fly over the dino's head
  const BIRD_MID_Y = 80;     // birds between HIGH and MID need a duck

  function tick() {
    const r = game();
    if (!r || !r.playing || r.crashed) return;

    const dino = r.tRex;
    const front = dino.xPos + TREX_WIDTH;
    const next = r.horizon.obstacles.find(o => o.xPos + o.width > dino.xPos);

    if (!next) { dino.setDuck(false); return; }

    const distance = next.xPos - front;
    const isBird = next.typeConfig.type === 'PTERODACTYL';
    const reactAt = r.currentSpeed * LOOK_AHEAD;

    if (isBird && next.yPos < BIRD_HIGH_Y) {          // high bird: just keep running
      dino.setDuck(false);
    } else if (isBird && next.yPos < BIRD_MID_Y) {    // mid bird: duck under it
      if (distance < reactAt && !dino.jumping) dino.setDuck(true);
    } else if (distance < reactAt && distance > -next.width) {
      dino.setDuck(false);
      if (!dino.jumping) dino.startJump(r.currentSpeed);   // cactus or low bird: jump
    } else if (dino.jumping && distance < -next.width / 2) {
      dino.setSpeedDrop();                            // cleared it: land fast
    } else {
      dino.setDuck(false);
    }
  }

  const id = setInterval(tick, 5);
  window.stopDinoBot = () => clearInterval(id);
  console.log('Dino bot running. Press Space to start, stopDinoBot() to stop.');
})();
