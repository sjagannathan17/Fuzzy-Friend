# 🐾 Fuzzy Friend – Pet Health AI (GenAI Group Project)

Fuzzy Friend is a **mobile-first pet health application** designed to help pet owners assess **symptom urgency**, make informed decisions about veterinary care, and reduce unnecessary emergency room visits while identifying truly urgent cases.

This project is part of a **Generative AI group assignment**, focusing on **frontend UI/UX design** with future integration of **LLMs, RAG, and LangChain**.

---

## 🚀 Project Overview

Pet owners often struggle to decide whether a symptom requires immediate veterinary attention.  
**Fuzzy Friend** addresses this gap by providing:

- A friendly, mobile-style interface
- Clear symptom urgency guidance
- AI-assisted conversational assessment
- Community support and educational resources

---

## 📱 Application Structure (Frontend)

The app follows a **5-tab mobile navigation design**:

1. **Home**  
   - Landing page with app name, tagline, about us, and “Get Started”
2. **Profile**  
   - Pet information (name, age, breed, etc.)  
   - Medical/case history  
   - Metrics and recent assessments
3. **AI Chatbot**  
   - Conversational symptom assessment  
   - Displays urgency level  
   - (Planned) Shows nearest ER vet when urgency is high
4. **Community / Forum**  
   - Pet owner discussions and shared experiences
5. **Settings**  
   - Privacy policy  
   - About us  
   - Customer support information

---

## 🛠️ Tech Stack

### Frontend
- **Next.js (App Router)**
- **TypeScript**
- **Tailwind CSS**
- **Poppins font** (modern, friendly mobile UI)
- **GitHub Codespaces** (development environment)



## 📁 Project Structure

genai_group_project/
│
├── frontend/                     # Frontend application (Next.js)
│   │
│   ├── app/                      # App Router pages (screens / tabs)
│   │   ├── page.tsx              # Home (Landing page – default tab)
│   │   ├── profile/
│   │   │   └── page.tsx          # Profile tab (pet info, medical history, metrics)
│   │   ├── onboarding/
│   │   │   └── page.tsx          # Symptom check / onboarding flow
│   │   ├── chat/
│   │   │   └── page.tsx          # AI chatbot interface
│   │   ├── forum/
│   │   │   └── page.tsx          # Community / forum page
│   │   ├── settings/
│   │   │   └── page.tsx          # Settings, privacy, about us, support
│   │   └── layout.tsx            # Global layout (fonts, sticky bottom navigation)
│   │
│   ├── components/               # Reusable UI components
│   │   └── TopNav.tsx            # Mobile-style sticky bottom navigation (5 tabs)
│   │
│   ├── public/                   # Static assets
│   │   └── fuzzy-friend-logo.png # Application logo
│   │
│   ├── styles/                   # Global styles (if extended later)
│   │
│   ├── package.json              # Project dependencies & scripts
│   └── tailwind.config.js        # Tailwind CSS configuration
│
├── README.md                     # Project documentation
└── .gitignore                    # Git ignored files


## 🧑‍💻 How to Run the App (No Local Setup Needed)

### Using GitHub Codespaces (Recommended)

1. Open this repository on GitHub
2. Click **Code → Codespaces → Create Codespace**
3. In the terminal, run:
   ```bash
   cd frontend
   npm run dev
