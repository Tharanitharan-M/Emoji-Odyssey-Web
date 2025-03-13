"use client";

import { useRouter } from "next/navigation";

export default function BackButton({ to }: { to: string }) {
  const router = useRouter();

  return (
    <button
      onClick={() => router.push(to)}
      className="absolute top-4 left-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
    >
      Back
    </button>
  );
}
