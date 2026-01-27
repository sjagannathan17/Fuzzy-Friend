"use client";
import { useState, useRef } from "react";
import { Paperclip } from "lucide-react";


export default function ChatbotModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [messages, setMessages] = useState([
    { type: "bot", text: "Hi! Please describe your pet's symptoms." },
  ]);
  const [input, setInput] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [imageUploading, setImageUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (!input.trim() && images.length === 0) return;
    if (input.trim()) {
      setMessages((msgs) => [...msgs, { type: "user", text: input }]);
    }
    if (images.length > 0) {
      setMessages((msgs) => [...msgs, ...images.map(img => ({ type: "user", text: "[Image]", image: img }))]);
      setImages([]);
    }
    setInput("");
    setTimeout(() => {
      setMessages((msgs) => [...msgs, { type: "bot", text: "I'm just a demo!" }]);
    }, 800);
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
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 relative">
        <button onClick={onClose} className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-xl">×</button>
        <h2 className="text-lg font-bold mb-4">Fuzzy Friend Chatbot</h2>
        <div className="h-64 overflow-y-auto mb-4 space-y-2">
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
        <div className="flex gap-2 items-end">
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
            className="flex-1 border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter") handleSend(); }}
            placeholder="Type your message..."
          />
          <button onClick={handleSend} className="bg-blue-500 text-white rounded-xl px-4 py-2 font-bold hover:bg-blue-600">Send</button>
        </div>
      </div>
    </div>
  );
}
