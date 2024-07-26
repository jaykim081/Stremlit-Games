import streamlit as st
import streamlit.components.v1 as components
if 'game' not in st.session_state:
    st.session_state.game = 'Tetris'
st.title("Game Switcher")
st.write("Choose a game to play:")

col1, col2 = st.columns(2)
with col1:
    if st.button('Tetris'):
        st.session_state.game = 'Tetris'

with col2:
    if st.button('Ping Pong'):
        st.session_state.game = 'Ping Pong'
if st.session_state.game == 'Tetris':
    st.write("Tetris")
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Basic Tetris HTML Game</title>
      <meta charset="UTF-8">
      <style>
      html, body {
        height: 100%;
        margin: 0;
      }

      body {
        background: black;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      canvas {
        border: 1px solid white;
      }
      </style>
    </head>
    <body>
    <canvas width="320" height="640" id="game"></canvas>
    <script>
    // https://tetris.fandom.com/wiki/Tetris_Guideline

    // get a random integer between the range of [min,max]
    // @see https://stackoverflow.com/a/1527820/2124254
    function getRandomInt(min, max) {
      min = Math.ceil(min);
      max = Math.floor(max);

      return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // generate a new tetromino sequence
    // @see https://tetris.fandom.com/wiki/Random_Generator
    function generateSequence() {
      const sequence = ['I', 'J', 'L', 'O', 'S', 'T', 'Z'];

      while (sequence.length) {
        const rand = getRandomInt(0, sequence.length - 1);
        const name = sequence.splice(rand, 1)[0];
        tetrominoSequence.push(name);
      }
    }

    // get the next tetromino in the sequence
    function getNextTetromino() {
      if (tetrominoSequence.length === 0) {
        generateSequence();
      }

      const name = tetrominoSequence.pop();
      const matrix = tetrominos[name];

      // I and O start centered, all others start in left-middle
      const col = playfield[0].length / 2 - Math.ceil(matrix[0].length / 2);

      // I starts on row 21 (-1), all others start on row 22 (-2)
      const row = name === 'I' ? -1 : -2;

      return {
        name: name,      // name of the piece (L, O, etc.)
        matrix: matrix,  // the current rotation matrix
        row: row,        // current row (starts offscreen)
        col: col         // current col
      };
    }

    // rotate an NxN matrix 90deg
    // @see https://codereview.stackexchange.com/a/186834
    function rotate(matrix) {
      const N = matrix.length - 1;
      const result = matrix.map((row, i) =>
        row.map((val, j) => matrix[N - j][i])
      );

      return result;
    }

    // check to see if the new matrix/row/col is valid
    function isValidMove(matrix, cellRow, cellCol) {
      for (let row = 0; row < matrix.length; row++) {
        for (let col = 0; col < matrix[row].length; col++) {
          if (matrix[row][col] && (
              // outside the game bounds
              cellCol + col < 0 ||
              cellCol + col >= playfield[0].length ||
              cellRow + row >= playfield.length ||
              // collides with another piece
              playfield[cellRow + row][cellCol + col])
            ) {
            return false;
          }
        }
      }

      return true;
    }

    // place the tetromino on the playfield
    function placeTetromino() {
      for (let row = 0; row < tetromino.matrix.length; row++) {
        for (let col = 0; col < tetromino.matrix[row].length; col++) {
          if (tetromino.matrix[row][col]) {

            // game over if piece has any part offscreen
            if (tetromino.row + row < 0) {
              return showGameOver();
            }

            playfield[tetromino.row + row][tetromino.col + col] = tetromino.name;
          }
        }
      }

      // check for line clears starting from the bottom and working our way up
      for (let row = playfield.length - 1; row >= 0; ) {
        if (playfield[row].every(cell => !!cell)) {

          // drop every row above this one
          for (let r = row; r >= 0; r--) {
            for (let c = 0; c < playfield[r].length; c++) {
              playfield[r][c] = playfield[r-1][c];
            }
          }
        }
        else {
          row--;
        }
      }

      tetromino = getNextTetromino();
    }

    // show the game over screen
    function showGameOver() {
      cancelAnimationFrame(rAF);
      gameOver = true;

      context.fillStyle = 'black';
      context.globalAlpha = 0.75;
      context.fillRect(0, canvas.height / 2 - 30, canvas.width, 60);

      context.globalAlpha = 1;
      context.fillStyle = 'white';
      context.font = '36px monospace';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.fillText('GAME OVER!', canvas.width / 2, canvas.height / 2);
    }

    const canvas = document.getElementById('game');
    const context = canvas.getContext('2d');
    const grid = 32;
    const tetrominoSequence = [];

    // keep track of what is in every cell of the game using a 2d array
    // tetris playfield is 10x20, with a few rows offscreen
    const playfield = [];

    // populate the empty state
    for (let row = -2; row < 20; row++) {
      playfield[row] = [];

      for (let col = 0; col < 10; col++) {
        playfield[row][col] = 0;
      }
    }

    // how to draw each tetromino
    // @see https://tetris.fandom.com/wiki/SRS
    const tetrominos = {
      'I': [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
      ],
      'J': [
        [1,0,0],
        [1,1,1],
        [0,0,0],
      ],
      'L': [
        [0,0,1],
        [1,1,1],
        [0,0,0],
      ],
      'O': [
        [1,1],
        [1,1],
      ],
      'S': [
        [0,1,1],
        [1,1,0],
        [0,0,0],
      ],
      'Z': [
        [1,1,0],
        [0,1,1],
        [0,0,0],
      ],
      'T': [
        [0,1,0],
        [1,1,1],
        [0,0,0],
      ]
    };

    // color of each tetromino
    const colors = {
      'I': 'cyan',
      'O': 'yellow',
      'T': 'purple',
      'S': 'green',
      'Z': 'red',
      'J': 'blue',
      'L': 'orange'
    };

    let count = 0;
    let tetromino = getNextTetromino();
    let rAF = null;  // keep track of the animation frame so we can cancel it
    let gameOver = false;

    // game loop
    function loop() {
      rAF = requestAnimationFrame(loop);
      context.clearRect(0,0,canvas.width,canvas.height);

      // draw the playfield
      for (let row = 0; row < 20; row++) {
        for (let col = 0; col < 10; col++) {
          if (playfield[row][col]) {
            const name = playfield[row][col];
            context.fillStyle = colors[name];

            // drawing 1 px smaller than the grid creates a grid effect
            context.fillRect(col * grid, row * grid, grid-1, grid-1);
          }
        }
      }

      // draw the active tetromino
      if (tetromino) {

        // tetromino falls every 35 frames
        if (++count > 35) {
          tetromino.row++;
          count = 0;

          // place piece if it runs into anything
          if (!isValidMove(tetromino.matrix, tetromino.row, tetromino.col)) {
            tetromino.row--;
            placeTetromino();
          }
        }

        context.fillStyle = colors[tetromino.name];

        for (let row = 0; row < tetromino.matrix.length; row++) {
          for (let col = 0; col < tetromino.matrix[row].length; col++) {
            if (tetromino.matrix[row][col]) {

              // drawing 1 px smaller than the grid creates a grid effect
              context.fillRect((tetromino.col + col) * grid, (tetromino.row + row) * grid, grid-1, grid-1);
            }
          }
        }
      }
    }

    // listen to keyboard events to move the active tetromino
    document.addEventListener('keydown', function(e) {
      if (gameOver) return;

      // left and right arrow keys (move)
      if (e.which === 37 || e.which === 39) {
        const col = e.which === 37
          ? tetromino.col - 1
          : tetromino.col + 1;

        if (isValidMove(tetromino.matrix, tetromino.row, col)) {
          tetromino.col = col;
        }
      }

      // up arrow key (rotate)
      if (e.which === 38) {
        const matrix = rotate(tetromino.matrix);
        if (isValidMove(matrix, tetromino.row, tetromino.col)) {
          tetromino.matrix = matrix;
        }
      }

      // down arrow key (drop)
      if(e.which === 40) {
        const row = tetromino.row + 1;

        if (!isValidMove(tetromino.matrix, row, tetromino.col)) {
          tetromino.row = row - 1;

          placeTetromino();
          return;
        }

        tetromino.row = row;
      }
    });

    // start the game
    rAF = requestAnimationFrame(loop);
    </script>
    </body>
    </html>
    """, height=640)
else:
    st.write("Ping Pong")
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Simple Ping Pong Game</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: black;
            }
            canvas {
                background: white;
                display: block;
            }
        </style>
    </head>
    <body>
        <canvas id="pong" width="600" height="400"></canvas>
        <script>
            const canvas = document.getElementById("pong");
            const context = canvas.getContext("2d");

            const user = {
                x: 0,
                y: canvas.height / 2 - 50,
                width: 10,
                height: 100,
                color: "WHITE",
                score: 0
            };

            const com = {
                x: canvas.width - 10,
                y: canvas.height / 2 - 750,
                width: 10,
                height: 1500,
                color: "WHITE",
                score: 0
            };

            const ball = {
                x: canvas.width / 2,
                y: canvas.height / 2,
                radius: 10,
                speed: 5,
                velocityX: 5,
                velocityY: 5,
                color: "WHITE"
            };

            function drawRect(x, y, w, h, color) {
                context.fillStyle = color;
                context.fillRect(x, y, w, h);
            }

            function drawArc(x, y, r, color) {
                context.fillStyle = color;
                context.beginPath();
                context.arc(x, y, r, 0, Math.PI * 2, false);
                context.closePath();
                context.fill();
            }

            function drawText(text, x, y, color) {
                context.fillStyle = color;
                context.font = "45px fantasy";
                context.fillText(text, x, y);
            }

            function render() {
                drawRect(0, 0, canvas.width, canvas.height, "BLACK");
                drawRect(user.x, user.y, user.width, user.height, user.color);
                drawRect(com.x, com.y, com.width, com.height, com.color);
                drawArc(ball.x, ball.y, ball.radius, ball.color);
            }

            function update() {
                ball.x += ball.velocityX;
                ball.y += ball.velocityY;

                if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) {
                    ball.velocityY = -ball.velocityY;
                }

                let player = (ball.x < canvas.width / 2) ? user : com;

                if (collision(ball, player)) {
                    let collidePoint = ball.y - (player.y + player.height / 2);
                    collidePoint = collidePoint / (player.height / 2);
                    let angleRad = collidePoint * Math.PI / 4;
                    let direction = (ball.x < canvas.width / 2) ? 1 : -1;
                    ball.velocityX = direction * ball.speed * Math.cos(angleRad);
                    ball.velocityY = ball.speed * Math.sin(angleRad);
                    ball.speed += 0.1;
                }

                if (ball.x - ball.radius < 0) {
                    com.score++;
                    resetBall();
                } else if (ball.x + ball.radius > canvas.width) {
                    user.score++;
                    resetBall();
                }
            }

            function collision(b, p) {
                p.top = p.y;
                p.bottom = p.y + p.height;
                p.left = p.x;
                p.right = p.x + p.width;

                b.top = b.y - b.radius;
                b.bottom = b.y + b.radius;
                b.left = b.x - b.radius;
                b.right = b.x + b.radius;

                return p.left < b.right && p.top < b.bottom && p.right > b.left && p.bottom > b.top;
            }

            function resetBall() {
                ball.x = canvas.width / 2;
                ball.y = canvas.height / 2;
                ball.speed = 5;
                ball.velocityX = -ball.velocityX;
            }

            function game() {
                update();
                render();
            }

            const framePerSecond = 50;
            setInterval(game, 1000 / framePerSecond);

            window.addEventListener("mousemove", evt => {
                let rect = canvas.getBoundingClientRect();
                user.y = evt.clientY - rect.top - user.height / 2;
            });
        </script>
    </body>
    </html>
    """, height=400)
