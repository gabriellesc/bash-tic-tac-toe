# Tic-tac-toe Bash server

## How it works

### Architecture

The server is a Node.js WebSocket server, built using Express and [ws](https://github.com/websockets/ws).  
The primary tic-tac-toe engine is a single Bash script, which is run as a child process by the server.  
The server relays the child process's I/O to a client.

When the tic-tac-toe opponent is an expert AI, the Bash script calls a Python script containing the expert-level game logic.

When this Python script runs for the first time on a system, where it is not provided with an (up-to-date) [tree](https://github.com/gabriellesc/bash-tic-tac-toe/blob/master/tree) file, it builds a game tree with weights and serializes this tree (using Python's `pickle`). When it runs subsequently, the script de-serializes the tree, rather than rebuilding it.  
Each time the script is called, it receives the current state of the game board, and traverses the game tree to find the node corresponding to this game.

### Gameplay

The game can be played against another human player (using the same client), or against an AI.

The AI can play at each of these expertise levels (based on [this blog post](https://blog.ostermiller.org/tic-tac-toe-strategy) by Stephen Ostermiller):
- **Novice**: chooses random moves
- **Intermediate**: blocks an opponent's three-in-a-row or takes any three-in-a-row, if it can; otherwise, chooses random moves
- **Experienced**: plays at the intermediate level, but chooses the best possible opening move
- **Expert**: plays a solved game

### Program details of interest

1. The primary Bash script stores the current board state in a "fake" associative array.  
That is, the state of each board square is stored as a variable with a common prefix and a unique (indexing) suffix, eg. `square1`, `square2`, etc.

    To access the state of an arbitrary square (one whose index is stored in another variable), we need to evaluate `$square$index`. This means forcing variable expansion to occur in two stages: first, we need to expand `$index` to produce `$square1`, and then we need to expand `$square1`.
   
    We do this using `eval` and quoting, eg.
    ```
    eval echo '$square'$index
    ```

    In this example, `eval` causes `$index` to be expanded but not `$square` because it is quoted, and then causes the new command `echo $square1` to be executed.

2. To receive user input from stdin, the primary Bash script uses `read`. Messages from the client are passed directly to the stdin of the Bash process without being sanitized or validated (subject to change - see [#2](https://github.com/gabriellesc/bash-tic-tac-toe/issues/2)).  
This creates potential security vulnerabilities, mitigated by:
   - the program accepts a limited range of (single character) input
   - the result of `read` is double-quoted when first used
   - the result of `read` is immediately checked against a strict regex

3. The secondary Python script builds a game tree for tic-tac-toe and assigns weights to nodes using the [minimax algorithm](http://www.flyingmachinestudios.com/programming/minimax/).

## How to use it

The server is currently accessible at [wss://bash-tic-tac-toe.herokuapp.com/](wss://bash-tic-tac-toe.herokuapp.com/).  
A client interface exists at [https://gabriellesc.github.io/ticTacToe/index.html](https://gabriellesc.github.io/ticTacToe/index.html), which uses [Xterm.js](https://xtermjs.org/) to emulate the experience of interacting directly with the Bash script in a terminal.

## License
Licensed under the MIT License. See [LICENSE](LICENSE) for more information.
