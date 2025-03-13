"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import api, { getUserIdFromToken } from "@/services/api";
import BackButton from "@/components/BackButton";

export default function JoinRoomPage() {
  const [name, setName] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [roomId, setRoomId] = useState("");
  const [players, setPlayers] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [hasJoined, setHasJoined] = useState(false);
  const [isMounted, setIsMounted] = useState(false); // To prevent SSR mismatch
  const router = useRouter();

  useEffect(() => {
    setIsMounted(true); // Mark when the component is mounted
  }, []);

  const handleJoinRoom = async () => {
    try {
      const userId = getUserIdFromToken();
      if (!userId || !name || !roomCode) {
        setError("Please provide your name and a valid room code.");
        return;
      }

      const response = await api.post("/multiplayer/join_room", {
        room_code: roomCode,
        user_id: userId,
        player_name: name,
      });

      setRoomId(response.data.room_id);
      setHasJoined(true);
      setError("");
    } catch (error: any) {
      console.error("Error joining room", error.response?.data || error.message);
      setError(error.response?.data.error || "Failed to join room.");
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (roomId && isMounted) {
      interval = setInterval(async () => {
        try {
          const response = await api.get(`/multiplayer/get_players/${roomId}`);
          setPlayers(response.data.players || []);
        } catch (error) {
          console.error("Error fetching players", error);
        }
      }, 10000); // Poll every 10 seconds
    }

    return () => clearInterval(interval);
  }, [roomId, isMounted]);

  if (!isMounted) return null; // Skip rendering until the component is mounted

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div>
      <BackButton to="/game-mode" />
      {/* Your Join Room Content */}
    </div>
      <h1 className="text-3xl font-bold mb-6">
        {hasJoined ? "Room Details" : "Join Multiplayer Room"}
      </h1>

      {!hasJoined && (
        <>
          <input
            type="text"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="border px-4 py-2 rounded mb-4"
          />
          <input
            type="text"
            placeholder="Room Code"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value)}
            className="border px-4 py-2 rounded mb-4"
          />
          <button onClick={handleJoinRoom} className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
            Join Room
          </button>
        </>
      )}

      {hasJoined && (
        <>
          <p className="mt-4">Room Code: <strong>{roomCode}</strong></p>
          <h2 className="text-xl font-semibold mt-6 mb-2">Players in Room:</h2>
          <ul className="bg-white shadow p-4 rounded w-60">
            {players.map((player, index) => (
              <li key={index} className="border-b last:border-0 py-2">
                {player}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
