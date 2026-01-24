"use client";

import { Search, MapPin, Star, Phone, Home, User, MessageCircle, Users, Settings } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function HomePage() {
  // Placeholder data
  const userGreeting = "Pooja";
  const [activeTab, setActiveTab] = useState("home");
  const router = useRouter();
  
  const tabs = [
    { id: "home", icon: Home, label: "Home", href: "/" },
    { id: "profile", icon: User, label: "Profile", href: "/profile" },
    { id: "chat", icon: MessageCircle, label: "Chat", href: "/symptom-assistant" },
    { id: "forum", icon: Users, label: "Forum", href: "/community-forum" },
    { id: "settings", icon: Settings, label: "Settings", href: "/" },
  ];
  
  const clinics = [
    {
      id: 1,
      name: "Paws & Care Clinic",
      address: "123 Pet St, Downtown",
      rating: 4.8,
    },
    {
      id: 2,
      name: "Happy Tails Veterinary",
      address: "456 Animal Ave, Midtown",
      rating: 4.9,
    },
  ];

  const vets = [
    {
      id: 1,
      name: "Dr. Sarah Johnson",
      title: "DVM",
      hospital: "Paws & Care Clinic",
      status: "Available to chat",
      avatar: "🐾",
    },
    {
      id: 2,
      name: "Dr. Michael Chen",
      title: "DVM",
      hospital: "Happy Tails Veterinary",
      status: "Available to chat",
      avatar: "🩺",
    },
  ];

  return (
    <main className="min-h-screen bg-gray-50 pb-24">
      {/* Hero Header */}
      <section className="bg-gradient-to-br from-blue-400 to-blue-500 pt-8 pb-32 px-4 relative">
        <div className="mx-auto max-w-2xl">
          <div className="flex items-center justify-between">
            {/* Left: Avatar & Greeting */}
            <div className="flex-1">
              <h1 className="text-2xl font-semibold text-gray-900">
                Hello Fuzzy Friend,
              </h1>
              <p className="mt-1 text-gray-600 text-sm font-medium" style={{fontFamily: 'var(--font-poppins)'}}>
                How can we help today?
              </p>
            </div>

            {/* Right: Decorative Interactive Paw */}
            <div className="group cursor-pointer ml-4">
              <style>{`
                @keyframes paw-rotate {
                  0%, 100% { transform: rotate(0deg) scale(1); }
                  25% { transform: rotate(-5deg) scale(1.1); }
                  50% { transform: rotate(0deg) scale(1.2); }
                  75% { transform: rotate(5deg) scale(1.1); }
                }
                .paw-interactive:hover {
                  animation: paw-rotate 0.8s ease-in-out infinite;
                }
              `}</style>
              <div className="w-16 h-16 rounded-full bg-white/25 backdrop-blur-sm flex items-center justify-center text-4xl ring-2 ring-white/50 group-hover:ring-white/80 group-hover:bg-white/40 transition-all duration-300 paw-interactive">
                🐾
              </div>
              <div className="text-white/70 text-xs font-semibold text-center mt-2 group-hover:text-white transition-colors" style={{fontFamily: 'var(--font-poppins)'}}>
                
              </div>
            </div>
          </div>
        </div>

        {/* Quick Symptom Check Card - Overlapping */}
        <div className="mx-auto max-w-2xl px-4 -mb-20 relative z-20 mt-12">
          <div className="bg-white rounded-3xl shadow-xl p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h2 className="text-lg font-bold text-gray-900" style={{fontFamily: 'var(--font-poppins)'}}>
                  Quick Symptom Check
                </h2>
                <p className="text-sm text-gray-600 font-medium mt-1" style={{fontFamily: 'var(--font-poppins)'}}>
                  Get urgency guidance in under 2 minutes
                </p>
              </div>
              <span className="bg-blue-100 text-blue-700 text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap ml-2">
                Recommended
              </span>
            </div>

        

            {/* CTA Button */}
            <a
              href="/onboarding"
              className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white font-bold py-3 px-4 rounded-2xl text-center hover:shadow-lg hover:from-blue-600 hover:to-blue-700 transition-all active:scale-95"
            >
              Get Started
            </a>
          </div>
        </div>
      </section>

      {/* Content Sections */}
      <div className="mx-auto max-w-2xl px-4 mt-12 space-y-8">
        {/* Nearby Clinics */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-medium text-gray-900" style={{fontFamily: 'var(--font-poppins)'}}>
                My Clinics
              </h2>
              <p className="text-sm text-gray-500 mt-1" style={{fontFamily: 'var(--font-poppins)'}}>
                Bensonhurst Veterinary Care
              </p>
            </div>
            <div className="relative w-32">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search"
                className="w-full bg-gray-100 border border-gray-200 rounded-lg pl-8 pr-3 py-2 text-xs font-medium placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          </div>

          <div className="space-y-3">
            {clinics.map((clinic) => (
              <div
                key={clinic.id}
                className="bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-xl flex-shrink-0">
                    🏥
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-gray-900 text-sm" style={{fontFamily: 'var(--font-poppins)'}}>
                      {clinic.name}
                    </h4>
                    <div className="flex items-center gap-1 text-xs text-gray-600 mt-1" style={{fontFamily: 'var(--font-poppins)'}}>
                      <MapPin size={14} />
                      <span className="truncate">{clinic.address}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Star size={14} className="fill-yellow-400 text-yellow-400" />
                    <span className="text-xs font-semibold text-gray-700">
                      {clinic.rating}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Vets / Available to Chat */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900" style={{fontFamily: 'var(--font-poppins)'}}>
              👨‍⚕️ Vets
            </h2>
            <div className="relative w-32">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search"
                className="w-full bg-gray-100 border border-gray-200 rounded-lg pl-8 pr-3 py-2 text-xs font-medium placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          </div>

          <div className="space-y-3">
            {vets.map((vet) => (
              <div
                key={vet.id}
                className="bg-white rounded-2xl p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-xl flex-shrink-0">
                      {vet.avatar}
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-bold text-gray-900 text-sm" style={{fontFamily: 'var(--font-poppins)'}}>
                        {vet.name}, {vet.title}
                      </h4>
                      <p className="text-xs text-gray-600 mt-1" style={{fontFamily: 'var(--font-poppins)'}}>{vet.hospital}</p>
                      <div className="mt-2">
                        <span className="inline-block bg-green-100 text-green-700 text-xs font-semibold px-2 py-1 rounded-full" style={{fontFamily: 'var(--font-poppins)'}}>
                          ✓ {vet.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Phone
                    size={20}
                    className="text-blue-500 flex-shrink-0 hover:scale-110 transition-transform cursor-pointer"
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* About Us */}
        <section className="mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h3 className="text-base font-bold text-gray-900 mb-3" style={{fontFamily: 'var(--font-poppins)'}}>
              About Fuzzy Friend
            </h3>
            <p className="text-sm text-gray-600 font-medium leading-relaxed mb-4" style={{fontFamily: 'var(--font-poppins)'}}>
              Fuzzy Friend helps pet owners assess symptom urgency to reduce unnecessary ER visits while identifying truly urgent cases. We give you the clarity and confidence to make the right decision for your pet's health.
            </p>
            <button className="text-blue-600 font-bold text-sm hover:text-blue-700 transition-colors" style={{fontFamily: 'var(--font-poppins)'}}>
              Learn more →
            </button>
          </div>
        </section>

        {/* Bottom Navigation */}
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-2xl">
          <style>{`
            @keyframes pop {
              0% { transform: scale(1) rotate(0deg); }
              50% { transform: scale(1.4) rotate(-10deg); }
              100% { transform: scale(1) rotate(0deg); }
            }
            .icon-pop:hover {
              animation: pop 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }
          `}</style>
          <div className="mx-auto max-w-2xl px-4 flex justify-around items-center">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    router.push(tab.href);
                  }}
                  className={`flex-1 py-4 px-2 flex flex-col items-center gap-1 transition-all duration-200 group relative`}
                  title={tab.label}
                >
                  {/* Glow background on hover */}
                  <div className="absolute inset-0 rounded-full bg-blue-100 opacity-0 group-hover:opacity-100 transition-opacity duration-200 -z-10 scale-75"></div>
                  
                  <Icon
                    size={28}
                    className={`transition-all duration-200 icon-pop ${
                      isActive
                        ? "text-blue-600 scale-125"
                        : "text-gray-600 group-hover:text-blue-500 group-hover:scale-125"
                    }`}
                    strokeWidth={isActive ? 2.5 : 2}
                    fill={isActive ? "currentColor" : "none"}
                  />
                  <span className={`text-xs font-bold transition-all ${isActive ? "text-blue-600 opacity-100" : "text-gray-600 opacity-0 group-hover:opacity-75"}`} style={{fontFamily: 'var(--font-poppins)'}}>
                    {tab.label}
                  </span>
                </button>
              );
            })}
          </div>
        </nav>
      </div>
    </main>
  );
}
