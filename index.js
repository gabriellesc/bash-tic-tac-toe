'use strict';

const express = require('express');
const http = require('http');
const url = require('url');
const WebSocket = require('ws');
const { exec } = require('child_process');

const PORT = process.env.PORT || 3000;

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, clientTracking: true });

wss.on('connection', function connection(ws, req) {
    console.log('Client connected');

    // verify that this remote endpoint is still responsive
    ws.isAlive = true;
    ws.on('pong', () => (ws.isAlive = true));

    // exec a new child that runs the script using Bash
    const child = exec(`${__dirname}/ticTacToe.sh`, { shell: '/bin/bash' });

    // when input is received through the websocket, send it to the child's stdin
    ws.on('message', message => {
	console.log('received: %s', message);
	child.stdin.write(message.replace(/\r/g, '\n'));
    });

    // when the connection is closed, terminate the child
    ws.on('close', code => {
	console.log(`connection closed with code ${code}`);
	child.kill();
    });

    // when the child puts data on stdout, send it through the websocket
    child.stdout.on('data', data => {
	console.log(`stdout: ${data}`);
	ws.send(data.replace(/\n/g, '\r\n'));
    });

    // when the child puts data on stderr, send it through the websocket
    child.stderr.on('data', data => {
	console.log(`stderr: ${data}`);
	ws.send(data.replace(/\n/g, '\r\n'));
    });

    // when the child process terminates, close the websocket connection
    child.on('close', code => {
	console.log(`child process exited with code ${code}`);
	ws.close();
    });
});

// verify that each client is still responsive at intervals
const interval = setInterval(function ping() {
    wss.clients.forEach(function each(ws) {
	if (ws.isAlive === false) {
	    console.log('endpoint non-responsive');
	    return ws.terminate();
	}

	ws.isAlive = false;
	ws.ping(() => {});
    });
}, 300000);

server.listen(PORT, function listening() {
    console.log('Listening on %d', PORT);
});
