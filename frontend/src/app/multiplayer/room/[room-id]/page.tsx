"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import api from "@/services/api";
import BackButton from "@/components/BackButton";

export default function StartGamePage() {
  const { room_id } = useParams();
  const [emojiClue, setEmojiClue] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const router = useRouter();

  const submitPuzzle = async () => {
    try {
      const hostId = localStorage.getItem("user_id");
      await api.post("/multiplayer/set_emoji", {
        room_id,
        host_id: hostId,
        emoji_clue: emojiClue,
        correct_answer: correctAnswer,
      });

      router.push(`/multiplayer/room/${room_id}/game`);
    } catch (error) {
      console.error("Error submitting puzzle", error);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div>
      <BackButton to="/multiplayer/join-room" />
    </div>
      <h1 className="text-3xl font-bold mb-6">Submit Emoji Puzzle</h1>

      <input
        type="text"
        placeholder="Emoji Clue"
        value={emojiClue}
        onChange={(e) => setEmojiClue(e.target.value)}
        className="mb-4 p-2 border rounded w-60"
      />

      <input
        type="text"
        placeholder="Correct Answer"
        value={correctAnswer}
        onChange={(e) => setCorrectAnswer(e.target.value)}
        className="mb-4 p-2 border rounded w-60"
      />

      <button
        onClick={submitPuzzle}
        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Submit Puzzle
      </button>
    </div>
  );
}
