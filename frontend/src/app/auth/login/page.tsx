"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { setToken } = useAuth();
  const router = useRouter();

  const handleLogin = () => {
    const dummyToken = "dummy_jwt_token";
    setToken(dummyToken);
    router.push("/game-mode");
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="p-6 bg-white rounded shadow-md w-80">
        <h2 className="text-xl font-bold mb-4">Login</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 mb-2 border rounded"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 mb-4 border rounded"
        />
        <button onClick={handleLogin} className="w-full bg-blue-500 text-white py-2 rounded">
          Login
        </button>
        <p className="text-center mt-4">
          Don't have an account?{" "}
          <button
            onClick={() => router.push("/auth/signup")}
            className="text-blue-500 underline"
          >
            Sign Up
          </button>
        </p>
      </div>
    </div>
  );
}
