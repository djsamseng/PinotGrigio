import express, { Express } from "express";
import cors from "cors";
import { Server as SocketIOServer, Socket } from "socket.io";

import router from "./routes/router";

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());
app.use(router);

const server = app.listen(PORT, () => {
    console.log("Server running on port:", PORT);
});

const io = new SocketIOServer(server);

const motorControllerSockets: Array<Socket> = [];

router.put("/control", (req, resp) => {
    console.log("Control:", req.body);
    io.sockets.in("braincontrol").emit("braincontrol", req.body);
    resp.send({});
});

io.on("connection", (socket) => {
    console.log("Got socket.io connection");
    socket.on("create or join", (room) => {
        console.log('create or join');
        const roomSockets = io.sockets.adapter.rooms.get(room);
        if (!roomSockets) {
            socket.join(room);
            console.log("Created room:", room);
            socket.emit('created', room, socket.id);
            return;
        }
        const numClientsInRoom = roomSockets.size;
        if (numClientsInRoom === 0) {
            socket.join(room);
            console.log("Created room:", room);
            socket.emit('created', room, socket.id);
        }
        else {
            io.sockets.in(room).emit('join', room);
            console.log("Room:", room, " now has ", numClientsInRoom + 1, " client(s)");
            socket.join(room);
            socket.emit('joined', room, socket.id);
        }
    });
    socket.on('disconnecting', () => {
        console.log("disconnecting:", socket.id);
        const roomsWasIn = io.sockets.adapter.sids.get(socket.id);
        if (!roomsWasIn) {
            console.log("Disconnecting: was not in any rooms");
            return;
        }
        for (const roomName of roomsWasIn.keys()) {
            const room = io.sockets.adapter.rooms.get(roomName);
            if (room) {
                const numRemainingClients = room.size - 1;
                console.log("Disconnecting: was in room:", roomName);
                console.log("Room:", roomName, " now has ", numRemainingClients, " client(s)");
                if (numRemainingClients === 1) {
                    console.log("Sending isInitiator");
                    io.sockets.in(roomName).emit("isinitiator", roomName);
                }
            }

        }
    });

    // Motor control
    socket.on("registerForMotorControl", () => {
        console.log("Registered for motor control!");
        motorControllerSockets.push(socket);
    });
    socket.on("motor", (data) => {
        console.log("Motor:", data);
        for (const motorSocket of motorControllerSockets) {
            motorSocket.emit("motor", data);
        }
    });

    // Audio data
    socket.on("registerForAudioData", () =>{
        socket.join("audiodata");
    })
    socket.on("audiodata", (data) => {
        io.sockets.in("audiodata").emit("audiodata", data);
    });
    socket.on("registerForRpiAudio", () => {
        socket.join("rpiaudio");
    });
    socket.on("rpiaudio", (data) => {
        io.sockets.in("rpiaudio").emit("rpiaudio", data);
    });

    // Control data
    socket.on("registerForBrainControl", () => {
        socket.join("braincontrol");
    });
});
