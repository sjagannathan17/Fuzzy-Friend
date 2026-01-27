"use client";

import { Home, User, MessageCircle, Users, Settings, Bell, Trash2, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SettingsPage() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("settings");

  const tabs = [
    { id: "home", icon: Home, label: "Home", href: "/" },
    { id: "profile", icon: User, label: "Profile", href: "/profile" },
    { id: "chat", icon: MessageCircle, label: "Chat", href: "/symptom-assistant" },
    { id: "forum", icon: Users, label: "Forum", href: "/community-forum" },
    { id: "settings", icon: Settings, label: "Settings", href: "/settings" },
  ];

  const handleTabClick = (href: string) => {
    router.push(href);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 pb-24">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Settings & Information</h1>
          <p className="text-gray-600 mt-1">Manage your account and preferences</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        
        {/* Notifications Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-indigo-600" />
            Notifications
          </h2>
          
          {/* Toggle Row */}
          <div className="flex items-center justify-between py-4 border-b border-gray-200">
            <div className="flex-1">
              <p className="text-gray-900 font-medium">Push Notifications</p>
              <p className="text-sm text-gray-600 mt-1">Receive updates about your pet's health</p>
            </div>
            <button
              onClick={() => setNotificationsEnabled(!notificationsEnabled)}
              className={`ml-4 relative inline-flex h-8 w-14 items-center rounded-full transition-colors ${
                notificationsEnabled ? "bg-indigo-600" : "bg-gray-300"
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                  notificationsEnabled ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Privacy Policy Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Privacy Policy</h2>
          <div className="space-y-4">
            <p className="text-gray-700 leading-relaxed">
              Your privacy is important to us. We are committed to protecting your personal information and ensuring transparency in how we collect, use, and maintain your data.
            </p>
            <p className="text-gray-700 leading-relaxed">
              All information you provide to us is encrypted and stored securely. We do not share your data with third parties without your explicit consent. For detailed information about our privacy practices, please contact our support team.
            </p>
            <button className="text-indigo-600 hover:text-indigo-700 font-medium text-sm flex items-center gap-1 mt-4">
              Read Full Privacy Policy
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* About Us Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">About Us</h2>
          <div className="space-y-4">
            <p className="text-gray-700 leading-relaxed">
              Our mission is to reduce unnecessary emergency room visits for pets by providing accessible, timely guidance and support from qualified veterinarians.
            </p>
            <p className="text-gray-700 leading-relaxed">
              We believe that every pet owner should have access to expert veterinary advice when they need it most. Through our platform, we connect pet owners with knowledgeable professionals who can help determine the right level of care their pets need.
            </p>
            <div className="bg-indigo-50 border-l-4 border-indigo-600 p-4 mt-4 rounded">
              <p className="text-indigo-900 text-sm font-medium">Version 1.0.0</p>
            </div>
          </div>
        </div>

        {/* Contact Support Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Support</h2>
          <div className="space-y-4">
            <p className="text-gray-700">
              Have questions or need help? Our support team is here to assist you.
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Email</p>
              <p className="text-gray-900 font-medium mt-1">support@petshealth.com</p>
            </div>
            <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 rounded-lg transition-colors">
              Send us a Message
            </button>
          </div>
        </div>

        {/* Delete Data Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border-2 border-red-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Trash2 className="w-5 h-5 text-red-600" />
            Data Management
          </h2>
          <p className="text-gray-700 text-sm mb-4">
            Permanently delete your account and all associated data. This action cannot be undone.
          </p>
          <button className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2">
            <Trash2 className="w-5 h-5" />
            Delete My Data
          </button>
        </div>

      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex justify-around">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    handleTabClick(tab.href);
                  }}
                  className={`flex flex-col items-center justify-center py-3 px-4 transition-colors ${
                    activeTab === tab.id
                      ? "text-indigo-600 border-t-2 border-indigo-600"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  <Icon className="w-6 h-6" />
                  <span className="text-xs mt-1 font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
