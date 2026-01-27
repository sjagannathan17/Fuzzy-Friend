"use client";

import { useRouter } from "next/navigation";

export default function SymptomResultsPage({ searchParams }: { searchParams?: Record<string, string> }) {
  // Optionally, get results from query params or context
  // For now, just show a placeholder
  const router = useRouter();

  // Example: get result data from searchParams or context
  // const result = searchParams?.result || "";

  return (
    <main className="min-h-screen bg-gray-50 pb-24 px-4">
      <div className="max-w-2xl mx-auto py-10 space-y-8">
        <header className="space-y-1">
          <h1 className="text-2xl font-bold text-gray-900">Symptom Check Results</h1>
          <p className="text-sm text-gray-500">Here’s what we found based on your answers.</p>
        </header>
        <section className="bg-white rounded-2xl shadow-sm p-6 space-y-4 border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Assessment</h2>
          <p className="text-gray-700 text-base font-medium">Your pet’s results will appear here. (Integrate with chat output or backend as needed.)</p>
        </section>
        <button
          className="w-full rounded-2xl bg-blue-600 px-4 py-3 text-center text-white text-base font-semibold shadow-md hover:bg-blue-700 active:scale-[0.99] transition"
          onClick={() => router.push("/")}
        >
          Back to Home
        </button>
      </div>
    </main>
  );
}
