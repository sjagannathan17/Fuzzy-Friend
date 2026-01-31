"use client";

import { Send, Upload, Home, User, MessageCircle, Users, Settings, X, ArrowLeft, AlertTriangle, CheckCircle, Clock, MapPin } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import {
  submitTriage,
  TriageResponse,
  RiskLevel,
  SymptomCategory,
  SYMPTOM_CATEGORIES,
  getRiskLevelColor,
  getRiskLevelLabel,
  imageToBase64,
  getCurrentLocation,
} from "@/lib/api";

interface Message {
  id: string;
  type: "user" | "ai";
  content: string;
  triageResponse?: TriageResponse;
  timestamp: Date;
}

// Risk level styling
const getRiskBadgeStyle = (riskLevel: RiskLevel) => {
  switch (riskLevel) {
    case "ER":
      return "bg-red-100 text-red-800 border-red-300";
    case "TODAY":
      return "bg-orange-100 text-orange-800 border-orange-300";
    case "SOON":
      return "bg-yellow-100 text-yellow-800 border-yellow-300";
    case "MONITOR":
      return "bg-green-100 text-green-800 border-green-300";
    default:
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
};

const getRiskIcon = (riskLevel: RiskLevel) => {
  switch (riskLevel) {
    case "ER":
      return <AlertTriangle className="text-red-600" size={20} />;
    case "TODAY":
      return <Clock className="text-orange-600" size={20} />;
    case "SOON":
      return <Clock className="text-yellow-600" size={20} />;
    case "MONITOR":
      return <CheckCircle className="text-green-600" size={20} />;
    default:
      return null;
  }
};

export default function SymptomAssistant() {
  const [activeTab, setActiveTab] = useState("triage");
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "ai",
      content: "Hello! 👋 I'm your AI Symptom Assistant. Tell me about your pet's symptoms and I'll help assess the urgency. Please select a symptom category below and describe what's happening.",
      timestamp: new Date(Date.now() - 5 * 60000),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<SymptomCategory>("Something Else");
  const [selectedSpecies, setSelectedSpecies] = useState<"dog" | "cat">("dog");
  const [showCategoryPicker, setShowCategoryPicker] = useState(true);
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const tabs = [
    { id: "home", icon: Home, label: "Home", href: "/" },
    { id: "triage", icon: AlertTriangle, label: "Triage", href: "/symptom-assistant" },
    { id: "chat", icon: MessageCircle, label: "Chat", href: "/chat" },
    { id: "forum", icon: Users, label: "Forum", href: "/community-forum" },
    { id: "profile", icon: User, label: "Profile", href: "/profile" },
  ];

  // Try to get user location on mount
  useEffect(() => {
    getCurrentLocation()
      .then((loc) => setUserLocation(loc))
      .catch(() => {
        // Location not available, that's okay
        console.log("Location not available");
      });
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    setApiError(null);

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
    setShowCategoryPicker(false);

    try {
      // Prepare image if uploaded
      let imageData: { base64: string; type: string } | null = null;
      if (imageFile) {
        imageData = await imageToBase64(imageFile);
      }

      // Call the real API
      const response = await submitTriage({
        species: selectedSpecies,
        category: selectedCategory,
        user_description: inputValue,
        structured_fields: {},
        image_base64: imageData?.base64,
        image_type: imageData?.type,
        latitude: userLocation?.latitude,
        longitude: userLocation?.longitude,
      });

      // Clear uploaded image after sending
      setUploadedImage(null);
      setImageFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      if (response.success && response.data) {
        const triageData = response.data;
        
        // Build response message
        let responseContent = "";
        
        if (triageData.risk_level === "ER") {
          responseContent = `🚨 **EMERGENCY - Seek immediate veterinary care!**\n\n`;
        } else if (triageData.risk_level === "TODAY") {
          responseContent = `⚠️ **Urgent - Your pet should see a vet today.**\n\n`;
        } else if (triageData.risk_level === "SOON") {
          responseContent = `📅 **Schedule a vet visit within 24-48 hours.**\n\n`;
        } else {
          responseContent = `✅ **Safe to monitor at home for now.**\n\n`;
        }

        if (triageData.red_flags && triageData.red_flags.length > 0) {
          responseContent += `**Red Flags Detected:**\n${triageData.red_flags.map(f => `• ${f}`).join('\n')}\n\n`;
        }

        responseContent += `**What to do:**\n${triageData.recommended_actions.map(a => `• ${a}`).join('\n')}\n\n`;

        if (triageData.what_to_monitor && triageData.what_to_monitor.length > 0) {
          responseContent += `**Watch for:**\n${triageData.what_to_monitor.map(m => `• ${m}`).join('\n')}\n\n`;
        }

        responseContent += `\n_${triageData.disclaimer}_`;

        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "ai",
          content: responseContent,
          triageResponse: triageData,
          timestamp: new Date(),
        };
        
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        // API returned error
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "ai",
          content: `I apologize, but I encountered an issue: ${response.error_message || "Unknown error"}. Please try again or contact your veterinarian directly if you have urgent concerns.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("API Error:", error);
      setApiError("Unable to connect to the AI service. Make sure the backend is running.");
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: "I'm sorry, I couldn't connect to the AI service right now. Please make sure the backend server is running (run `uvicorn api:app --reload` in the pet_triage folder), or try again later. If your pet has urgent symptoms, please contact your veterinarian directly.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }

    setIsLoading(false);
    scrollToBottom();
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setUploadedImage(null);
    setImageFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
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
          
          {/* API Status Indicator */}
          {apiError && (
            <div className="mt-3 bg-red-500/20 border border-red-300/30 rounded-lg px-3 py-2 text-sm">
              ⚠️ {apiError}
            </div>
          )}
        </div>
      </header>

      {/* Species & Category Selector */}
      {showCategoryPicker && (
        <div className="px-4 py-4 max-w-2xl mx-auto w-full space-y-4 bg-white/80 backdrop-blur border-b">
          {/* Species Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedSpecies("dog")}
              className={`flex-1 py-2 px-4 rounded-full font-semibold text-sm transition-all ${
                selectedSpecies === "dog"
                  ? "bg-blue-500 text-white shadow-md"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              🐕 Dog
            </button>
            <button
              onClick={() => setSelectedSpecies("cat")}
              className={`flex-1 py-2 px-4 rounded-full font-semibold text-sm transition-all ${
                selectedSpecies === "cat"
                  ? "bg-blue-500 text-white shadow-md"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              🐱 Cat
            </button>
          </div>

          {/* Category Pills */}
          <div className="flex flex-wrap gap-2">
            {SYMPTOM_CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
                  selectedCategory === cat.id
                    ? "bg-blue-500 text-white shadow-md"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {cat.icon} {cat.label}
              </button>
            ))}
          </div>
        </div>
      )}

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
              <div 
                className="text-sm font-medium leading-relaxed whitespace-pre-wrap" 
                style={{ fontFamily: "var(--font-poppins)" }}
              >
                {message.content}
              </div>

              {/* Triage Response Card */}
              {message.type === "ai" && message.triageResponse && (
                <div className="mt-4 space-y-3">
                  {/* Risk Level Badge */}
                  <div className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${getRiskBadgeStyle(message.triageResponse.risk_level)}`}>
                    {getRiskIcon(message.triageResponse.risk_level)}
                    <span className="font-bold text-sm">
                      {getRiskLevelLabel(message.triageResponse.risk_level)}
                    </span>
                  </div>

                  {/* Nearby Vets (if ER and available) */}
                  {message.triageResponse.risk_level === "ER" && message.triageResponse.nearby_vets && message.triageResponse.nearby_vets.length > 0 && (
                    <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                      <p className="font-bold text-red-800 text-sm mb-2 flex items-center gap-1">
                        <MapPin size={16} /> Nearby Emergency Vets:
                      </p>
                      {message.triageResponse.nearby_vets.slice(0, 2).map((vet, idx) => (
                        <div key={idx} className="text-xs text-red-700 mb-1">
                          • {vet.name} {vet.distance_km && `(${vet.distance_km} km)`}
                          {vet.phone && ` - ${vet.phone}`}
                        </div>
                      ))}
                    </div>
                  )}
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
              <div className="flex gap-2 items-center">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                <span className="text-sm text-gray-500 ml-2">Analyzing symptoms...</span>
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
            onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSendMessage()}
            placeholder="Describe your pet's symptoms..."
            disabled={isLoading}
            className="flex-1 bg-gray-100 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500 disabled:opacity-50"
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
        <div className="flex items-center justify-between mt-3">
          <p className="text-xs text-gray-500" style={{ fontFamily: "var(--font-poppins)" }}>
            💡 Be specific: "vomiting 3 times, won't eat, lethargic"
          </p>
          {userLocation && (
            <span className="text-xs text-green-600 flex items-center gap-1">
              <MapPin size={12} /> Location enabled
            </span>
          )}
        </div>
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
