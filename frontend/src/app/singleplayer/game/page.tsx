"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import api, { getUserIdFromToken } from "@/services/api";

export default function GamePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const genre = searchParams.get("genre");
  const level = searchParams.get("level");

  const [emojiClue, setEmojiClue] = useState("");
  const [answerStructure, setAnswerStructure] = useState<string[][]>([]);
  const [userAnswer, setUserAnswer] = useState<string[][]>([]);
  const [score, setScore] = useState<number>(0);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const inputRefs = useRef<(HTMLInputElement | null)[][]>([]);

  useEffect(() => {
    const fetchGameData = async () => {
      const userId = getUserIdFromToken();
      if (!userId) {
        console.error("User ID is missing, redirecting to login.");
        router.push("/auth/login");
        return;
      }
  
      if (!genre) {
        console.error("Genre is missing.");
        return;
      }
  
      try {
        // Fetch level data
        const response = await api.get(`/singleplayer/get_levels/${userId}/${genre}`);
        const levelData = response.data.levels.find((lvl: any) => lvl.level_number == level);
  
        if (levelData && levelData.correct_answer) {
          setEmojiClue(levelData.emoji_clue);
          const words = levelData.correct_answer.split(" ");
          setAnswerStructure(words.map(word => Array(word.length).fill("")));
          setUserAnswer(words.map(word => Array(word.length).fill("")));
          inputRefs.current = words.map(word => Array(word.length).fill(null));
        } else {
          console.error("Correct answer or level data is missing for this level.");
        }
  
        // Fetch score
        try {
          const scoreResponse = await api.get(`/singleplayer/get_score/${userId}/${genre}`);
          setScore(scoreResponse.data.score || 0);
        } catch (scoreError) {
          console.error("Failed to fetch score:", scoreError.response?.data || scoreError.message);
        }
  
      } catch (error) {
        console.error("Error fetching game data:", error.response?.data || error.message);
      }
    };
  
    fetchGameData();
  }, [genre, level]);
  

  const handleInputChange = (wordIndex: number, charIndex: number, value: string) => {
    if (!/^[a-zA-Z]$/.test(value) && value !== "") return;
    const updatedAnswer = [...userAnswer];
    updatedAnswer[wordIndex][charIndex] = value;
    setUserAnswer(updatedAnswer);

    // Move to next input box if a letter is entered
    if (value && inputRefs.current[wordIndex][charIndex + 1]) {
      inputRefs.current[wordIndex][charIndex + 1]?.focus();
    } else if (value && inputRefs.current[wordIndex + 1]?.[0]) {
      inputRefs.current[wordIndex + 1][0]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, wordIndex: number, charIndex: number) => {
    if (e.key === "Backspace") {
      const updatedAnswer = [...userAnswer];
      if (updatedAnswer[wordIndex][charIndex]) {
        updatedAnswer[wordIndex][charIndex] = "";
      } else {
        if (charIndex > 0) {
          inputRefs.current[wordIndex][charIndex - 1]?.focus();
        } else if (wordIndex > 0 && inputRefs.current[wordIndex - 1]) {
          const prevWord = inputRefs.current[wordIndex - 1];
          prevWord[prevWord.length - 1]?.focus();
        }
      }
      setUserAnswer(updatedAnswer);
    }
  };

  const isSubmitDisabled = userAnswer.some(word => word.some(char => char.trim() === ""));

  const handleSubmit = async () => {
    const finalAnswer = userAnswer.map(word => word.join("")).join(" ").trim();
    const userId = getUserIdFromToken();

    try {
      const response = await api.post("/singleplayer/submit_answer", {
        user_id: userId,
        level_number: Number(level),
        answer: finalAnswer,
      });

      if (response.data.correct) {
        setMessage({ type: "success", text: "🎉 Correct Answer!" });

        // Refresh score immediately after correct submission
        const scoreResponse = await api.get(`/singleplayer/get_score/${userId}/${genre}`);
        setScore(scoreResponse.data.score || 0);

        // Redirect after 2 seconds to Levels Page
        setTimeout(() => {
          router.push(`/singleplayer/levels?genre=${genre}`);
        }, 2000);
      } else {
        setMessage({ type: "error", text: "❌ Wrong Answer! Try Again." });
        setUserAnswer(answerStructure.map(word => Array(word.length).fill("")));
      }
    } catch (error: any) {
      console.error("Submit Error:", error.response?.data || error.message);
      setMessage({ type: "error", text: "An error occurred while submitting your answer." });
    }
};



  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      
      {/* Score at Top Right */}
      <div className="absolute top-4 right-4 text-lg font-semibold">
        Score: <span className="text-blue-500">{score}</span>
      </div>

      <h1 className="text-3xl font-bold mb-6 capitalize">
        {genre} - Level {level}
      </h1>

      {/* Emoji Clue */}
      <div className="text-6xl mb-6">{emojiClue}</div>

      {/* Answer Input Boxes */}
      <div className="flex flex-col items-center gap-4">
        {answerStructure.map((word, wordIndex) => (
          <div key={wordIndex} className="flex gap-2">
            {word.map((_, charIndex) => (
              <input
                key={charIndex}
                ref={(el) => {
                  if (!inputRefs.current[wordIndex]) {
                    inputRefs.current[wordIndex] = [];
                  }
                  inputRefs.current[wordIndex][charIndex] = el;
                }}
                type="text"
                maxLength={1}
                value={userAnswer[wordIndex][charIndex]}
                onChange={(e) => handleInputChange(wordIndex, charIndex, e.target.value.toUpperCase())}
                onKeyDown={(e) => handleKeyDown(e, wordIndex, charIndex)}
                className="w-10 h-10 text-center border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            ))}
          </div>
        ))}
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={isSubmitDisabled}
        className={`mt-6 px-6 py-2 rounded ${
          isSubmitDisabled ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 text-white hover:bg-blue-600"
        }`}
      >
        Submit
      </button>

      {/* Custom Notification Message */}
      {message && (
        <div
          className={`mt-4 px-4 py-2 rounded ${
            message.type === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Back Button */}
      <button
        onClick={() => router.push(`/singleplayer/levels?genre=${genre}`)}
        className="mt-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        Back to Levels
      </button>
    </div>
  );
}
