"use client";

import { Send, Upload, Home, User, MessageCircle, Users, Settings, X, ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useRef } from "react";

interface Message {
  id: string;
  type: "user" | "ai";
  content: string;
  urgencyLevel?: "low" | "medium" | "high" | "critical";
  timestamp: Date;
}

export default function SymptomAssistant() {
  const [activeTab, setActiveTab] = useState("chat");
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "ai",
      content: "Hello! 👋 I'm your AI Symptom Assistant. I can help you assess your pet's symptoms and determine urgency levels. Tell me what symptoms your pet is experiencing.",
      timestamp: new Date(Date.now() - 5 * 60000),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const tabs = [
    { id: "home", icon: Home, label: "Home", href: "/" },
    { id: "profile", icon: User, label: "Profile", href: "/profile" },
    { id: "chat", icon: MessageCircle, label: "Chat", href: "/symptom-assistant" },
    { id: "forum", icon: Users, label: "Forum", href: "/" },
    { id: "settings", icon: Settings, label: "Settings", href: "/" },
  ];

  // Example AI responses
  const aiResponses = [
    {
      content: "Vomiting and lethargy can indicate several conditions. This is a **MEDIUM** urgency case - consider veterinary care within 24 hours. If vomiting persists or your pet shows signs of severe dehydration, seek immediate care.",
      urgency: "medium" as const,
    },
    {
      content: "Difficulty breathing and coughing are concerning symptoms. This is a **HIGH** urgency case - your pet should see a vet within a few hours. Respiratory issues can escalate quickly.",
      urgency: "high" as const,
    },
    {
      content: "Loss of appetite for more than a day warrants attention. This is **LOW** to **MEDIUM** urgency - schedule a vet visit within 1-2 days to rule out underlying issues.",
      urgency: "low" as const,
    },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate AI response delay
    setTimeout(() => {
      const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: randomResponse.content,
        urgencyLevel: randomResponse.urgency,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);
      scrollToBottom();
    }, 800);
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setUploadedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const getUrgencyColor = (urgency?: string) => {
    switch (urgency) {
      case "critical":
        return "bg-red-100 text-red-800";
      case "high":
        return "bg-orange-100 text-orange-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 pb-24 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 pt-6 pb-4 shadow-lg">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <button
              onClick={() => router.push("/")}
              className="p-2 hover:bg-blue-700 rounded-full transition-colors"
              title="Go back to home"
            >
              <ArrowLeft size={24} />
            </button>
            <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-poppins)" }}>
              🏥 AI Symptom Assistant
            </h1>
          </div>
          <p className="text-blue-100 text-sm ml-12">Get instant urgency assessment for your pet</p>
        </div>
      </header>

      {/* Chat Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-md ${
                message.type === "user"
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-white text-gray-800 rounded-bl-none border border-gray-200"
              }`}
            >
              <p className="text-sm font-medium leading-relaxed" style={{ fontFamily: "var(--font-poppins)" }}>
                {message.content}
              </p>

              {/* Urgency Badge for AI messages */}
              {message.type === "ai" && message.urgencyLevel && (
                <div className={`mt-3 inline-block px-3 py-1 rounded-full text-xs font-bold ${getUrgencyColor(message.urgencyLevel)}`}>
                  Urgency: {message.urgencyLevel.toUpperCase()}
                </div>
              )}

              <span className={`text-xs mt-2 block ${message.type === "user" ? "text-blue-100" : "text-gray-500"}`}>
                {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 px-4 py-3 rounded-2xl rounded-bl-none border border-gray-200 shadow-md">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-4 py-4 shadow-xl max-w-2xl mx-auto w-full">
        {/* Image Preview */}
        {uploadedImage && (
          <div className="mb-4 relative inline-block">
            <img
              src={uploadedImage}
              alt="Uploaded symptom"
              className="h-24 w-24 object-cover rounded-lg border-2 border-blue-300"
            />
            <button
              onClick={removeImage}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        )}

        {/* Input Form */}
        <div className="flex gap-3 items-end">
          {/* File Upload Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex-shrink-0 bg-gray-100 hover:bg-gray-200 text-gray-700 p-2 rounded-full transition-colors"
            title="Upload symptom image"
          >
            <Upload size={20} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />

          {/* Text Input */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Describe your pet's symptoms..."
            className="flex-1 bg-gray-100 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            style={{ fontFamily: "var(--font-poppins)" }}
          />

          {/* Send Button */}
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="flex-shrink-0 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 text-white p-2 rounded-full transition-all active:scale-95"
            title="Send message"
          >
            <Send size={20} />
          </button>
        </div>

        {/* Helper Text */}
        <p className="text-xs text-gray-500 mt-3" style={{ fontFamily: "var(--font-poppins)" }}>
          💡 Tip: Describe symptoms in detail (e.g., "vomiting, lethargy, loss of appetite") for better urgency assessment
        </p>
      </div>

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
                <span
                  className={`text-xs font-bold transition-all ${isActive ? "text-blue-600 opacity-100" : "text-gray-600 opacity-0 group-hover:opacity-75"}`}
                  style={{ fontFamily: "var(--font-poppins)" }}
                >
                  {tab.label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </main>
  );
}
