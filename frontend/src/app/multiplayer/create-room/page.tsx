"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api, { getUserIdFromToken } from "@/services/api";
import BackButton from "@/components/BackButton";

export default function CreateRoomPage() {
  const [roomCode, setRoomCode] = useState("");
  const [roomId, setRoomId] = useState("");
  const [players, setPlayers] = useState<string[]>([]);
  const [username, setUsername] = useState("");
  const [rounds, setRounds] = useState(1);
  const [roomCreated, setRoomCreated] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleCreateRoom = async () => {
    try {
      const hostId = getUserIdFromToken();
      if (!hostId || !username.trim()) {
        setError("Please enter a valid name.");
        return;
      }

      const response = await api.post("/multiplayer/create_room", {
        host_id: hostId,
        username,
        total_rounds: rounds,
      });

      setRoomCode(response.data.room_code);
      setRoomId(response.data.room_id);
      setRoomCreated(true);
    } catch (error: any) {
      console.error("Error creating room", error.response?.data || error.message);
      setError(error.response?.data.error || "An unexpected error occurred.");
    }
  };

  // Fetch players every 5 seconds
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (roomId) {
      interval = setInterval(async () => {
        try {
          const response = await api.get(`/multiplayer/get_players/${roomId}`);
          setPlayers(response.data.players || []);
        } catch (error) {
          console.error("Error fetching players", error);
        }
      }, 5000);
    }

    return () => clearInterval(interval);
  }, [roomId]);

  const startGame = () => {
    router.push(`/multiplayer/room/${roomId}`);
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div>
        <BackButton to="/multiplayer" />
      </div>

      {!roomCreated && (
        <>
          <h1 className="text-3xl font-bold mb-6">Create Multiplayer Room</h1>

          <div className="flex items-center gap-2 mb-4">
            <label htmlFor="username" className="text-lg">Enter Name:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="border rounded px-3 py-1"
              placeholder="Your name"
            />
          </div>

          <div className="flex items-center gap-4 mb-4">
            <span>Number of Rounds:</span>
            <button onClick={() => setRounds((prev) => Math.max(1, prev - 1))} className="px-3 py-1 bg-gray-300 rounded">-</button>
            <span>{rounds}</span>
            <button onClick={() => setRounds((prev) => prev + 1)} className="px-3 py-1 bg-gray-300 rounded">+</button>
          </div>

          <button
            onClick={handleCreateRoom}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Create Room
          </button>

          {error && <p className="text-red-500 mt-4">{error}</p>}
        </>
      )}

      {roomCreated && (
        <>
          <h1 className="text-3xl font-bold mb-6">Multiplayer Room Created!</h1>
          <p className="mb-4 text-lg">
            Room Code: <strong className="text-xl">{roomCode}</strong>
          </p>

          <h2 className="text-xl font-semibold mb-2">Players in Room:</h2>
          <ul className="bg-white shadow p-4 rounded w-60">
            {players.length > 0 ? (
              players.map((player, index) => (
                <li key={index} className="border-b last:border-0 py-2 text-center">{player}</li>
              ))
            ) : (
              <li className="text-gray-500">Waiting for players to join...</li>
            )}
          </ul>

          <button
            onClick={startGame}
            disabled={players.length < 2}
            className={`mt-6 px-4 py-2 rounded ${
              players.length < 2
                ? "bg-gray-400 text-white cursor-not-allowed"
                : "bg-blue-500 text-white hover:bg-blue-600"
            }`}
          >
            {players.length < 2 ? "Waiting for Players..." : "Start Game"}
          </button>
        </>
      )}
    </div>
  );
}
