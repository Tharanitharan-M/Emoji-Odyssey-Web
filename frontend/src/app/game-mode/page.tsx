"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function GameModeSelection() {
  const router = useRouter();
  const { token, logout } = useAuth();

  useEffect(() => {
    if (!token) {
      router.push("/auth/login");
    }
  }, [token, router]);

  if (!token) return null;

  const handleLogout = () => {
    logout();
    router.push("/auth/login");
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100">
      <h1 className="text-4xl font-bold mb-6">Select Game Mode</h1>

      <button
        className="px-4 py-2 bg-blue-500 text-white rounded mb-4 w-60"
        onClick={() => router.push("/singleplayer")}
      >
        🎮 Single Player
      </button>

      <button
        className="px-4 py-2 bg-green-500 text-white rounded w-60"
        onClick={() => router.push("/multiplayer")}
      >
        🏆 Multiplayer
      </button>

      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded"
      >
        Logout
      </button>
    </div>
  );
}
