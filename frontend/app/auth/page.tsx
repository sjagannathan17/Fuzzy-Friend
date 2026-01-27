"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim() || (isSignUp && !name.trim())) {
      setError("Please fill in all required fields.");
      return;
    }
    setError("");
    // Simulate auth, then route to onboarding
    router.push("/onboarding");
  };

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 space-y-6 border border-gray-100">
        <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
          {isSignUp ? "Sign Up" : "Sign In"}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignUp && (
            <label className="block">
              <span className="text-sm font-medium text-gray-900">Name</span>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                placeholder="Your name"
                required
              />
            </label>
          )}
          <label className="block">
            <span className="text-sm font-medium text-gray-900">Email</span>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="you@email.com"
              required
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-gray-900">Password</span>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="••••••••"
              required
            />
          </label>
          {error && <div className="text-xs text-red-500 text-center">{error}</div>}
          <button
            type="submit"
            className="w-full rounded-2xl bg-blue-600 px-4 py-3 text-center text-white text-base font-semibold shadow-md hover:bg-blue-700 active:scale-[0.99] transition"
          >
            {isSignUp ? "Create Account" : "Sign In"}
          </button>
        </form>
        <div className="text-center text-sm text-gray-600">
          {isSignUp ? (
            <>
              Already have an account?{' '}
              <button className="text-blue-600 font-bold hover:underline" onClick={() => setIsSignUp(false)}>
                Sign In
              </button>
            </>
          ) : (
            <>
              New here?{' '}
              <button className="text-blue-600 font-bold hover:underline" onClick={() => setIsSignUp(true)}>
                Create an account
              </button>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
