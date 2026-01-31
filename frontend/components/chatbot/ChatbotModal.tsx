"use client";
import { useState, useRef, useState as useReactState, useEffect } from "react";
import { Paperclip } from "lucide-react";
import { useCameraCapture } from "./useCameraCapture";
import { useSymptomResultsNavigation } from "./useSymptomResultsNavigation";



interface ChatbotModalProps {
  open: boolean;
  onClose: () => void;
  ownerName?: string;
  petName?: string;
}

export default function ChatbotModal({ open, onClose, ownerName, petName }: ChatbotModalProps) {
  const symptomCategories = [
    "Toxic Ingestion & Poisoning: Poisoning, choking, foreign objects",
    "Stomach Upset: Diarrhea, bloating, vomiting",
    "Itching & Skin Issues: Dandruff, hair loss, bumps",
    "Injury & Bleeding: Blood loss, burns, open wounds",
    "Concerning Behaviour Changes: Not eating, seizures, limping",
    "Ears, Eyes, and Mouth: Infection, facial swelling, dental pain",
    "Breathing Issues: Wheezing, panting, sneezing",
    "Urinary & Genital: Straining, leaking, licking ",
    "Something Else: Not sure or not listed"
  ];
  const predefinedQuestions = [
    "My pet isnt eating and drinking normally?",
    "My pet vomited or had diarrhea?",
    "Is my pet breathing normally?",
    "My pet is limping or showing signs of pain?",
    "My pet had an injury?",
    "My pet's behavior is different than usual?"
  ];
  type ChatMessage = { type: string; text: string; image?: string };
  const [messages, setMessages] = useState<ChatMessage[]>([
    { type: "bot", text: `Hi${ownerName ? ` ${ownerName}` : ""}! Please select your pet's symptom category to get started.` },
  ]);
  const [categorySelected, setCategorySelected] = useState<string | null>(null);

  // Update greeting if ownerName or petName changes
  useEffect(() => {
    setMessages((msgs) => {
      if (msgs.length === 0 || msgs[0].type !== "bot") return msgs;
      const newGreeting = `Hi${ownerName ? ` ${ownerName}` : ""}! Describe ${petName && petName !== "your pet" ? petName : "your pet"}'s symptoms to get quick assessment.`;
      if (msgs[0].text === newGreeting) return msgs;
      const updated = [...msgs];
      updated[0] = { ...updated[0], text: newGreeting };
      return updated;
    });
  }, [ownerName, petName]);
  const [showPredefined, setShowPredefined] = useState(true);
  const [input, setInput] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [imageUploading, setImageUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [cameraOpen, setCameraOpen] = useReactState(false);
  const { videoRef, startCamera, stopCamera, capturePhoto } = useCameraCapture((dataUrl) => {
    setImages((prev) => [...prev, dataUrl]);
    setCameraOpen(false);
  });
  const { goToResults } = useSymptomResultsNavigation();

  const handleSend = () => {
    if (!categorySelected) return; // Prevent sending if no category selected
    if (!input.trim() && images.length === 0) return;
    if (input.trim()) {
      setMessages((msgs) => [...msgs, { type: "user", text: input }]);
    }
    if (images.length > 0) {
      setMessages((msgs) => [...msgs, ...images.map(img => ({ type: "user", text: "[Image]", image: img }))]);
      setImages([]);
    }
    setInput("");
    setShowPredefined(false);
    setTimeout(() => {
      setMessages((msgs) => [...msgs, { type: "bot", text: "I'm just a demo!" }]);
      // Navigate to results page after a short delay (simulate getting results)
      setTimeout(() => {
        goToResults();
        onClose();
      }, 1000);
    }, 800);
  };

  const handlePredefinedClick = (question: string) => {
    setMessages((msgs) => [...msgs, { type: "user", text: question }]);
    setShowPredefined(false);
    setTimeout(() => {
      setMessages((msgs) => [...msgs, { type: "bot", text: "Thank you! You can add more details or images if needed." }]);
    }, 500);
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setImageUploading(true);
      const readers: Promise<string>[] = [];
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        readers.push(new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result as string);
          reader.readAsDataURL(file);
        }));
      }
      Promise.all(readers).then((results) => {
        setImages((prev) => [...prev, ...results]);
        setImageUploading(false);
      });
    }
  };

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-xl p-0 relative flex flex-col" style={{ minHeight: '700px', minWidth: '420px', height: '80vh', maxHeight: '900px' }}>
        <button onClick={onClose} className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-xl z-10">×</button>
        <h2 className="text-lg font-bold mb-2 px-8 pt-8 pb-2 text-gray-900" style={{ color: '#1a1a1a' }}>What's happening to our Fuzzy Friend! </h2>
        {/* Mandatory Symptom Category Selection */}
        {!categorySelected && (
          <div className="px-8 pt-2 pb-4">
            <div className="font-bold mb-2" style={{ color: '#1d4ed8' }}>Hi{ownerName ? ` ${ownerName}` : ""}! Describe {petName && petName !== "your pet" ? petName : "your pet"}'s symptoms to get quick assessment.
Please select symptom category <span style={{ color: '#dc2626', fontWeight: 700 }}>*</span></div>
            <div className="flex flex-col gap-2">
              {symptomCategories.map((cat, idx) => (
                <button
                  key={idx}
                  className="bg-blue-50 text-blue-800 font-medium rounded-lg px-3 py-2 text-sm hover:bg-blue-100 border border-blue-100 transition text-left"
                  onClick={() => {
                    setCategorySelected(cat);
                    setMessages((msgs) => [
                      ...msgs,
                      { type: "user", text: cat },
                      { type: "bot", text: "Thank you for sharing. Do you have any pictures you want to upload?" }
                    ]);
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        )}
        {/* Chat and suggestions only after category selected */}
        {categorySelected && (
          <>
            <div className="flex-1 overflow-y-auto px-8 pb-2 space-y-2" style={{ minHeight: 0 }}>
              {messages.map((msg, i) => (
                <div key={i} className={msg.type === "user" ? "text-right" : "text-left"}>
                  {msg.image ? (
                    <img src={msg.image} alt="User upload" className="inline-block h-24 w-24 object-cover rounded-xl border-2 border-blue-200 mb-1" />
                  ) : null}
                  <span className={msg.type === "user" ? "inline-block bg-blue-100 text-blue-800 rounded-xl px-3 py-1" : "inline-block bg-gray-100 text-gray-800 rounded-xl px-3 py-1"}>
                    {msg.text}
                  </span>
                </div>
              ))}
            </div>
            {showPredefined && (
              <div className="px-8 pb-2">
                <div className="text-xs text-gray-500 mb-1">Suggestions:</div>
                <div className="flex flex-wrap gap-2">
                  {predefinedQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      className="bg-blue-50 text-blue-700 font-medium rounded-lg px-2 py-1 text-xs hover:bg-blue-100 border border-blue-100 transition"
                      onClick={() => handlePredefinedClick(q)}
                      style={{ minWidth: 'auto' }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
        <div className="px-8 pb-8 pt-2 bg-white flex gap-2 items-end border-t rounded-b-2xl">
          {/* Image upload button */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={handleImageUpload}
            disabled={imageUploading}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="bg-blue-100 text-blue-700 px-2 py-2 rounded-xl text-xs font-semibold hover:bg-blue-200 transition flex-shrink-0 flex items-center justify-center"
            disabled={imageUploading}
            title="Upload image(s)"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          {/* Camera capture button */}
          <button
            type="button"
            onClick={async () => {
              setCameraOpen(true);
              await startCamera();
            }}
            className="bg-blue-100 text-blue-700 px-2 py-2 rounded-xl text-xs font-semibold hover:bg-blue-200 transition flex-shrink-0 flex items-center justify-center"
            disabled={cameraOpen}
            title="Take a picture"
          >
            <span role="img" aria-label="camera" className="w-5 h-5">📷</span>
          </button>
          {/* Camera modal */}
          {cameraOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
              <div className="bg-white rounded-2xl shadow-xl p-6 flex flex-col items-center">
                <video ref={videoRef} autoPlay playsInline className="rounded-xl border mb-4 w-64 h-48 object-cover bg-black" />
                <div className="flex gap-3">
                  <button
                    onClick={capturePhoto}
                    className="bg-blue-600 text-white px-4 py-2 rounded-xl font-bold hover:bg-blue-700 transition"
                  >
                    Capture
                  </button>
                  <button
                    onClick={() => { stopCamera(); setCameraOpen(false); }}
                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded-xl font-bold hover:bg-gray-300 transition"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
          {/* Image previews */}
          {images.length > 0 && (
            <div className="flex gap-1 mr-2">
              {images.map((img, idx) => (
                <div key={idx} className="relative inline-block">
                  <img src={img} alt={`Preview ${idx + 1}`} className="h-10 w-10 object-cover rounded-lg border-2 border-blue-300" />
                  <button
                    onClick={() => setImages(images.filter((_, i) => i !== idx))}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors text-xs"
                    title="Remove image"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
          <input
            className="flex-1 border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder:font-semibold placeholder:text-gray-800"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
            placeholder="Describe symptoms or ask a question..."
            style={{ fontWeight: 600, color: '#222' }}
            disabled={!categorySelected}
          />
          <button onClick={handleSend} className="bg-blue-500 text-white rounded-xl px-4 py-2 font-bold hover:bg-blue-600" disabled={!categorySelected}>Send</button>
        </div>
      </div>
    </div>
  );
}
