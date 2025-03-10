"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";

export default function JoinRoomPage() {
  const [roomCode, setRoomCode] = useState("");
  const router = useRouter();

  const joinRoom = async () => {
    try {
      const userId = localStorage.getItem("user_id");
      const response = await api.post("/multiplayer/join_room", {
        room_code: roomCode,
        user_id: userId,
      });

      router.push(`/multiplayer/room/${response.data.room_id}`);
    } catch (error) {
      console.error("Error joining room", error);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <input
        value={roomCode}
        onChange={(e) => setRoomCode(e.target.value)}
        placeholder="Enter Room Code"
        className="px-4 py-2 border rounded mb-4"
      />
      <button
        onClick={joinRoom}
        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Join Room
      </button>
    </div>
  );
}
