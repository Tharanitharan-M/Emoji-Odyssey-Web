"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api, { getUserIdFromToken } from "@/services/api";

export default function GenreSelectionPage() {
  const [genres, setGenres] = useState<string[]>([]);
  const [scores, setScores] = useState<{ [key: string]: number }>({});
  const router = useRouter();

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

    const fetchGenres = async () => {
      try {
        const response = await api.get("/singleplayer/get_genres");
        setGenres(response.data.genres || []);
      } catch (error) {
        console.error("Failed to fetch genres", error);
      }
    };

    const fetchScores = async () => {
      for (const genre of genres) {
        try {
          const response = await api.get(`/singleplayer/get_score/${userId}/${genre}`);
          setScores(prevScores => ({
            ...prevScores,
            [genre]: response.data.score || 0,
          }));
        } catch (error) {
          console.error(`Failed to fetch score for genre: ${genre}`, error);
        }
      }
    };

    fetchGenres();
    fetchScores();
  }, [genres]);

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 relative">
      
      {/* Logout Button */}
      <div className="absolute top-4 right-4">
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      <h1 className="text-3xl font-bold mb-6">Select a Genre</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {genres.map((genre) => (
          <div key={genre} className="bg-white rounded-lg shadow p-4 w-60">
            <h2 className="text-xl font-semibold capitalize mb-2">{genre}</h2>

            <button
              className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              onClick={() => router.push(`/singleplayer/levels?genre=${genre.toLowerCase()}`)}
            >
              Play
            </button>

            <div className="mt-2 text-sm text-gray-600">
              Score: <span className="font-bold">{scores[genre] || 0}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
