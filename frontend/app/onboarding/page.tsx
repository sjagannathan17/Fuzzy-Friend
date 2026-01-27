"use client";


import { useState } from "react";
import { usePet } from "../../components/PetContext";
import { useRouter } from "next/navigation";

export default function OnboardingPage() {
  const [nameError, setNameError] = useState("");
  const [localPetName, setLocalPetName] = useState("");
  const { setPetName } = usePet();
  const router = useRouter();
  const [species, setSpecies] = useState<"Dog" | "Cat">("Dog");
  const [age, setAge] = useState(2);
  const [breed, setBreed] = useState("");
  const [sex, setSex] = useState<"Male" | "Female" | "Unknown">("Female");
  const [spayStatus, setSpayStatus] = useState<"Yes" | "No" | "Unknown">("Yes");
  const [heatCycle, setHeatCycle] = useState("Unknown");
  const [vaccination, setVaccination] = useState("Fully vaccinated");
  const [lifestyle, setLifestyle] = useState("Indoor only");
  const [historyFlags, setHistoryFlags] = useState<string[]>([]);

  const heatCycleVisible = spayStatus === "No" && sex === "Female" && (species === "Dog" || species === "Cat");

  const toggleFlag = (flag: string) => {
    setHistoryFlags((prev) =>
      prev.includes(flag) ? prev.filter((f) => f !== flag) : [...prev, flag]
    );
  };

  const historyOptions = [
    "Surgery",
    "Hospitalization",
    "Adverse reaction to medication",
    "History of eating things they shouldn’t",
    "Seizures",
    "Previous emergency vet visit",
  ];

  const heatOptions = [
    "Within 1 month",
    "1–3 months",
    "3–6 months",
    "More than 6 months",
    "Unknown",
  ];

  const vaccinationOptions = [
    "Fully vaccinated",
    "Started but not completed",
    "Not vaccinated",
    "Unknown",
  ];

  const lifestyleOptions = [
    "Indoor only",
    "Mostly indoor with supervised outdoor time",
    "Indoor/outdoor",
    "Mostly outdoor",
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!localPetName.trim()) {
      setNameError("Please enter your pet's name.");
      return;
    }
    setPetName(localPetName.trim());
    setNameError("");
    router.push("/");
  };

  return (
    <main className="min-h-screen bg-gray-50 pb-24 px-4">
      <div className="max-w-2xl mx-auto py-6 space-y-6">
        {/* Header */}
        <header className="space-y-1">
          <h1 className="text-2xl font-bold text-gray-900">Just a few quick questions!</h1>
          <p className="text-sm text-gray-500">
            This will take under 2 minutes.
          </p>
        </header>

        {/* Pet Basics */}
        <form onSubmit={handleSubmit}>
          <section className="bg-white rounded-2xl shadow-sm p-5 space-y-4 border border-gray-100">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Pet basics</h2>
              <p className="text-sm text-gray-500">Tell us a bit about your pet.</p>
            </div>
            <div className="space-y-3">
              <label className="block">
                <span className="text-sm font-medium text-gray-900">What is your pet's name? <span className="text-red-500">*</span></span>
                <input
                  type="text"
                  
                  onChange={(e) => setLocalPetName(e.target.value)}
                  placeholder="e.g., Bella"
                  required
                  className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                />
                {nameError && <span className="text-xs text-red-500">{nameError}</span>}
              </label>
            <div className="space-y-1">
              <span className="text-sm font-medium text-gray-900">Species</span>
              <div className="grid grid-cols-2 gap-2">
                {["Dog", "Cat"].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setSpecies(option as "Dog" | "Cat")}
                    className={`rounded-xl border px-3 py-2 text-sm font-semibold transition shadow-sm ${
                      species === option
                        ? "border-blue-500 bg-blue-50 text-blue-700"
                        : "border-gray-200 bg-white text-gray-700"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <label className="block">
                <span className="text-sm font-medium text-gray-900">Age (years)</span>
                <input
                  type="number"
                  min={0}
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium text-gray-900">Breed</span>
                <input
                  type="text"
                  value={breed}
                  onChange={(e) => setBreed(e.target.value)}
                  placeholder="e.g., Labrador"
                  className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                />
              </label>
            </div>
            <div className="space-y-1">
              <span className="text-sm font-medium text-gray-900">Sex</span>
              <div className="grid grid-cols-3 gap-2">
                {["Male", "Female", "Unknown"].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setSex(option as "Male" | "Female" | "Unknown")}
                    className={`rounded-xl border px-3 py-2 text-sm font-semibold transition shadow-sm ${
                      sex === option
                        ? "border-blue-500 bg-blue-50 text-blue-700"
                        : "border-gray-200 bg-white text-gray-700"
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>
          </section>

        {/* Spay/Neuter + Heat */}
        <section className="bg-white rounded-2xl shadow-sm p-5 space-y-3 border border-gray-100">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Spay/Neuter + Heat cycle</h2>
            <p className="text-sm text-gray-500">Required</p>
          </div>
          <div className="space-y-2">
          
              {["Yes", "No", "Unknown"].map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setSpayStatus(option as "Yes" | "No" | "Unknown")}
                  className={`rounded-xl border px-3 py-2 text-sm font-semibold transition shadow-sm ${
                    spayStatus === option
                      ? "border-blue-500 bg-blue-50 text-blue-700"
                      : "border-gray-200 bg-white text-gray-700"
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          
          {heatCycleVisible && (
            <div className="space-y-2">
              <span className="text-sm font-medium text-gray-900">When was her last heat cycle?</span>
              <div className="relative">
                <select
                  value={heatCycle}
                  onChange={(e) => setHeatCycle(e.target.value)}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                >
                  {heatOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </section>

        {/* Vaccination Status */}
        <section className="bg-white rounded-2xl shadow-sm p-5 space-y-3 border border-gray-100">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Vaccination status</h2>
            <p className="text-sm text-gray-500">Required</p>
          </div>
          <div className="space-y-2">
            
            <div className="space-y-2">
              {vaccinationOptions.map((option) => (
                <label
                  key={option}
                  className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm transition hover:border-blue-300"
                >
                  <input
                    type="radio"
                    name="vaccination"
                    value={option}
                    checked={vaccination === option}
                    onChange={() => setVaccination(option)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          </div>
        </section>

        {/* Lifestyle */}
        <section className="bg-white rounded-2xl shadow-sm p-5 space-y-3 border border-gray-100">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Lifestyle / Environment</h2>
            <p className="text-sm text-gray-500">Required</p>
          </div>
          <div className="space-y-2">
      
            <div className="space-y-2">
              {lifestyleOptions.map((option) => (
                <label
                  key={option}
                  className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm transition hover:border-blue-300"
                >
                  <input
                    type="radio"
                    name="lifestyle"
                    value={option}
                    checked={lifestyle === option}
                    onChange={() => setLifestyle(option)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          </div>
        </section>

        {/* Medical History Flags */}
        <section className="bg-white rounded-2xl shadow-sm p-5 space-y-3 border border-gray-100">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Medical history flags</h2>
            <p className="text-sm text-gray-500">Required • Select all that apply</p>
          </div>
          <div className="space-y-2">
            <div className="space-y-2">
              {historyOptions.map((flag) => (
                <label
                  key={flag}
                  className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm transition hover:border-blue-300"
                >
                  <input
                    type="checkbox"
                    checked={historyFlags.includes(flag)}
                    onChange={() => toggleFlag(flag)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span>{flag}</span>
                </label>
              ))}
            </div>
            <p className="text-xs text-gray-500">These help us assess risk factors.</p>
          </div>
        </section>

          {/* Primary Action */}
          <section className="space-y-2">
            <button
              type="submit"
              className="w-full rounded-2xl bg-blue-600 px-4 py-3 text-center text-white text-base font-semibold shadow-md hover:bg-blue-700 active:scale-[0.99] transition"
            >
              Let’s begin 🐾
            </button>
            <p className="text-xs text-gray-500 text-center">
              This tool does not provide a medical diagnosis.
            </p>
          </section>
        </form>

        {/* Safety Disclaimer */}
        <section className="bg-amber-50 border border-amber-200 text-amber-900 rounded-2xl p-4 shadow-sm">
          <p className="text-sm font-semibold">Safety first</p>
          <p className="text-sm mt-1">
            If your pet has trouble breathing, collapses, has seizures, or heavy bleeding, seek emergency veterinary care immediately.
          </p>
        </section>
      </div>
    </main>
  );
}
