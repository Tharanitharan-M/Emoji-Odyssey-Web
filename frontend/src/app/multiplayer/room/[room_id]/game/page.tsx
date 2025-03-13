"use client";

import { useEffect, useState } from "react";
import api from "@/services/api";
import { useParams, useRouter } from "next/navigation";

export default function GamePage() {
  const params = useParams();
  const room_id = params?.room_id as string;
  const [emojiClue, setEmojiClue] = useState("");
  const [answer, setAnswer] = useState("");
  const [players, setPlayers] = useState([]);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  // ✅ Fetch the question when the game starts
  useEffect(() => {
    const fetchQuestion = async () => {
        try {
          const response = await api.post("/multiplayer/get_random_question");
          setEmojiClue(response.data.emoji_clue);
        } catch (error: any) {
          console.error("Error fetching question:", error.response?.data || error.message);
          setError(error.response?.data.error || "Failed to fetch question.");
        }
      };      

    if (room_id) {
      fetchQuestion();
    } else {
      console.error("room_id is null or undefined");
      setError("Invalid Room ID. Cannot start the game.");
    }
  }, [room_id]);

  // ✅ Submit Answer
  const submitAnswer = async () => {
    if (!answer.trim()) {
      setError("Please enter an answer.");
      return;
    }

    setIsSubmitting(true);
    try {
      const userId = localStorage.getItem("user_id");
      const response = await api.post("/multiplayer/submit_answer", {
        room_id,
        user_id: userId,
        answer,
      });

      if (response.data.correct) {
        setAnswer("");
        setError("");
      } else {
        setError("Incorrect answer. Try again!");
      }
    } catch (error: any) {
      console.error("Error submitting answer:", error.response?.data || error.message);
      setError(error.response?.data.error || "Failed to submit answer.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // ✅ Real-Time Score Fetching
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/multiplayer/get_scores/${room_id}`);
        setPlayers(response.data.players || []);
      } catch (error: any) {
        console.error("Error fetching scores:", error.response?.data || error.message);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [room_id]);

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <h1 className="text-3xl font-bold mb-6">Guess the Emoji!</h1>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      <p className="text-xl mb-4">{emojiClue}</p>

      <input
        type="text"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Your Answer"
        className="border p-2 rounded mb-4"
      />

      <button
        onClick={submitAnswer}
        disabled={isSubmitting}
        className={`px-4 py-2 rounded ${
          isSubmitting ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 text-white hover:bg-blue-600"
        }`}
      >
        {isSubmitting ? "Submitting..." : "Submit Answer"}
      </button>

      <h2 className="text-xl font-semibold mt-6">Scores:</h2>
      <ul className="bg-white shadow p-4 rounded w-60">
        {players.length > 0 ? (
          players.map((player, index) => (
            <li key={index} className="border-b last:border-0 py-2 text-center">
              {player.username}: {player.score} points
            </li>
          ))
        ) : (
          <li className="text-gray-500">Waiting for players to score...</li>
        )}
      </ul>
    </div>
  );
}
