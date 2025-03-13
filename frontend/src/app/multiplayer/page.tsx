"use client";

import { useRouter } from "next/navigation";
import BackButton from "@/components/BackButton";

export default function MultiplayerOptions() {
  const router = useRouter();

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div>
            <BackButton to="/game-mode" />
          </div>
      <h1 className="text-4xl font-bold mb-6">Multiplayer Options</h1>

      <button
        className="px-4 py-2 bg-green-500 text-white rounded mb-4 w-60 hover:bg-green-600"
        onClick={() => router.push("/multiplayer/create-room")}
      >
        ➕ Create Room
      </button>

      <button
        className="px-4 py-2 bg-yellow-500 text-white rounded w-60 hover:bg-yellow-600"
        onClick={() => router.push("/multiplayer/join-room")}
      >
        🔑 Join Room
      </button>
    </div>
  );
}
