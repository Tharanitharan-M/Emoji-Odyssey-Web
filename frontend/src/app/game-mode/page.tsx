"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function GameModeSelection() {
  const router = useRouter();
  const { logout } = useAuth();

  // Check authentication on page load
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/login");
    }
  }, [router]);

  const handleLogout = () => {
    logout();
    localStorage.removeItem("token");
    router.push("/auth/login");
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100">
      
      <button
        onClick={handleLogout}
        className="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
      >
        Logout
      </button>

      <h1 className="text-4xl font-bold mb-6">Select Game Mode</h1>

      <button
        className="px-4 py-2 bg-blue-500 text-white rounded mb-4 w-60 hover:bg-blue-600"
        onClick={() => router.push("/singleplayer")}
      >
        🎮 Single Player
      </button>
    </div>
  );
}
