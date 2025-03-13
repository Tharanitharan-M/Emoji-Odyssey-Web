"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api, { getUserIdFromToken } from "@/services/api";
import BackButton from "@/components/BackButton";

export default function GenreSelectionPage() {
  const [genres, setGenres] = useState<string[]>([]);
  const [scores, setScores] = useState<{ [key: string]: number }>({});
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/auth/login");
  };

  useEffect(() => {
    const fetchGenresAndScores = async () => {
      const userId = getUserIdFromToken();
      if (!userId) {
        router.push("/auth/login");
        return;
      }

      try {
        // Fetch Genres
        const genresResponse = await api.get("/singleplayer/get_genres");
        const fetchedGenres = genresResponse.data.genres || [];
        setGenres(fetchedGenres);

        // Fetch Scores for Each Genre
        const scoresData: { [key: string]: number } = {};
        for (const genre of fetchedGenres) {
          try {
            const scoreResponse = await api.get(`/singleplayer/get_score/${userId}/${genre}`);
            scoresData[genre] = scoreResponse.data.score || 0;
          } catch (scoreError) {
            console.error(`Failed to fetch score for genre: ${genre}`, scoreError);
          }
        }
        setScores(scoresData);
      } catch (fetchError: any) {
        console.error("Failed to fetch genres or scores", fetchError);
        setError(fetchError.response?.data?.error || "Failed to load data");
      }
    };

    fetchGenresAndScores();
  }, []);

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 relative">
      <div>
      <BackButton to="/game-mode" />
      {/* Your Levels Content */}
    </div>
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

      {error && (
        <p className="text-red-500 mb-4">{error}</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {genres.length > 0 ? (
          genres.map((genre) => (
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
          ))
        ) : (
          <p className="text-gray-500">No genres available. Please try again later.</p>
        )}
      </div>
    </div>
  );
}
