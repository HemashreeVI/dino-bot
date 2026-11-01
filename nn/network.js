// The Dino's brain: a tiny neural network, plus how it sees and acts in the game.
// This file runs inside the game page (it is injected), so it is plain browser JS.
//
//   7 inputs  ->  8 hidden neurons (tanh)  ->  3 outputs: JUMP, DUCK, RUN
//
// Nobody wrote rules for it. Its weights come from nn/train.js (neuroevolution).
(() => {
  const INPUTS = 7, HIDDEN = 8, OUTPUTS = 3;
  const ACTIONS = ['JUMP', 'DUCK', 'RUN'];
  const SIZE = HIDDEN * (INPUTS + 1) + OUTPUTS * (HIDDEN + 1); // weights + biases

  const game = () =>
    typeof Runner.getInstance === 'function' ? Runner.getInstance() : Runner.instance_;

  // What the dino "sees", scaled to roughly 0..1.
  function sense(r) {
    const dino = r.tRex;
    const ahead = r.horizon.obstacles.filter(o => o.xPos + o.width > dino.xPos);
    const [a, b] = ahead;
    return [
      a ? Math.min(a.xPos - dino.xPos, 600) / 600 : 1, // distance to next obstacle
      a ? a.yPos / 150 : 0,                             // its height (birds fly higher)
      a ? a.width / 80 : 0,                             // its width (cactus groups)
      r.currentSpeed / 13,                              // game speed
      (93 - dino.yPos) / 100,                           // how high the dino is in the air
      b ? Math.min(b.xPos - dino.xPos, 600) / 600 : 1,  // distance to the obstacle after
      a && a.typeConfig.type === 'PTERODACTYL' ? 1 : 0, // is it a bird?
    ];
  }

  // Forward pass. Returns hidden and output activations (used for the live drawing too).
  function think(w, x) {
    let k = 0;
    const hidden = [];
    for (let h = 0; h < HIDDEN; h++) {
      let s = w[k++];
      for (let i = 0; i < INPUTS; i++) s += w[k++] * x[i];
      hidden.push(Math.tanh(s));
    }
    const out = [];
    for (let o = 0; o < OUTPUTS; o++) {
      let s = w[k++];
      for (let h = 0; h < HIDDEN; h++) s += w[k++] * hidden[h];
      out.push(s);
    }
    return { hidden, out };
  }

  // Press the "keys" the network chose, the same way a player would.
  function act(r, out) {
    const dino = r.tRex;
    const choice = out.indexOf(Math.max(...out));
    if (choice === 0) {
      dino.setDuck(false);
      if (!dino.jumping) dino.startJump(r.currentSpeed);
    } else if (choice === 1) {
      if (dino.jumping) dino.setSpeedDrop();   // "down" in the air = fall faster
      else dino.setDuck(true);
    } else {
      dino.setDuck(false);
    }
    return choice;
  }

  // One decision: look, think, act. Called once per game frame.
  function step(w) {
    const r = game();
    if (!r || !r.playing || r.crashed) return null;
    const x = sense(r);
    const { hidden, out } = think(w, x);
    const choice = act(r, out);
    return { x, hidden, out, choice };
  }

  window.DinoNet = { INPUTS, HIDDEN, OUTPUTS, SIZE, ACTIONS, game, sense, think, act, step };
})();
