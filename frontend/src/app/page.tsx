"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const { token, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push("/auth/login");
    }
  }, [token, router]);

  if (!token) return null;

  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <div className="p-6 bg-white rounded shadow-md w-80">
        <h1 className="text-2xl font-bold mb-4">Welcome to Emoji Odyssey</h1>
        <button onClick={logout} className="w-full bg-red-500 text-white py-2 rounded">
          Logout
        </button>
      </div>
    </div>
  );
}
