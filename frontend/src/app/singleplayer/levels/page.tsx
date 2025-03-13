"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import api, { getUserIdFromToken } from "@/services/api";
import BackButton from "@/components/BackButton";

export default function LevelsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const genre = searchParams.get("genre");

  const [completedLevels, setCompletedLevels] = useState(0);
  const totalLevels = 15;

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/auth/login");
  };

  useEffect(() => {
    const userId = getUserIdFromToken();
    if (!userId) {
      router.push("/auth/login");
      return;
    }

    const fetchProgress = async () => {
      try {
        const response = await api.get(`/singleplayer/get_levels/${userId}/${genre}`);
        setCompletedLevels(response.data.completed_levels);
      } catch (error) {
        console.error("Failed to fetch progress", error);
      }
    };

    fetchProgress();
  }, [genre, router]);

  const handleLevelClick = (levelNumber: number) => {
    if (levelNumber <= completedLevels + 1) {
      router.push(`/singleplayer/game?genre=${genre}&level=${levelNumber}`);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      
      {/* Logout Button */}
      <div className="absolute top-4 right-4">
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <h1 className="text-3xl font-bold mb-6 capitalize">{genre} Levels</h1>

      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: totalLevels }, (_, i) => i + 1).map((levelNumber) => (
          <button
            key={levelNumber}
            onClick={() => handleLevelClick(levelNumber)}
            disabled={levelNumber > completedLevels + 1}
            className={`px-6 py-3 rounded shadow ${
              levelNumber <= completedLevels
                ? "bg-green-500 text-white"
                : levelNumber === completedLevels + 1
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-500 cursor-not-allowed"
            }`}
          >
            {`Level ${levelNumber}`} {levelNumber > completedLevels + 1 && "🔒"}
          </button>
        ))}
      </div>

      {/* Back Button */}
      <button
        onClick={() => router.push("/singleplayer")}
        className="mt-6 px-6 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        Back to Genres
      </button>
    </div>
  );
}
