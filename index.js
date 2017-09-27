'use strict';

const express = require('express');
const http = require('http');
const url = require('url');
const WebSocket = require('ws');
const { exec } = require('child_process');

const PORT = process.env.PORT || 3000;

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', function connection(ws, req) {
    console.log('Client connected');

    const location = url.parse(req.url, true);
    // You might use location.query.access_token to authenticate or share sessions
    // or req.headers.cookie (see http://stackoverflow.com/a/16395220/151312)

    const child = exec(`${__dirname}/ticTacToe.sh`, { shell: '/bin/bash' });

    ws.on('message', function incoming(message) {
	console.log('received: %s', message);
	child.stdin.write(message.replace(/\r/g, '\n'));
    });
    
    child.stdout.on('data', (data) => {
	console.log(`stdout: ${data}`);
	ws.send(data.replace(/\n/g, '\r\n'));
    });

    child.stderr.on('data', (data) => {
	console.log(`stderr: ${data}`);
	ws.send(data.replace(/\n/g, '\r\n'));
    });

    child.on('close', (code) => {
	console.log(`child process exited with code ${code}`);
	ws.close();
    });
});

server.listen(PORT, function listening() {
    console.log('Listening on %d', PORT);
});
