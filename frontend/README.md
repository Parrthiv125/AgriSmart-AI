# 🌱 AgriSmart AI – Frontend

AgriSmart AI is a farmer-focused plant disease detection application designed to help users identify plant diseases from leaf images and receive useful disease information and recommendations.

This repository contains the **frontend application** of AgriSmart AI, built with React, TypeScript, and Vite.

The frontend is designed to work with mock services during development and can later be connected to the FastAPI backend and ML Model 1.

---

## ✨ Features

- 🌱 Farmer-friendly user interface
- 🏠 Home / Landing page
- 🔐 Login and Register pages
- 📊 Dashboard
- 📷 Plant image upload
- 📸 Camera capture
- 🖼️ Image preview
- 🔄 Remove / retake image
- 🔍 Plant analysis workflow
- ⏳ Loading / analysis state
- 📋 Prediction result
- 📈 Confidence score display
- ⚠️ Low-confidence handling
- 🦠 Disease details
- 💊 Treatment and recommendations
- 📜 Scan history
- ❓ Help page
- ℹ️ About page
- 📱 Responsive mobile, tablet, and desktop design
- 🌐 English language support
- ગુજરાતી Gujarati language support
- हिन्दी Hindi language support
- ⚡ Instant language switching without page reload
- 💾 Language preference persistence

---

## 🌐 Supported Languages

AgriSmart AI currently supports three languages:

| Language | Code | Default |
|----------|------|---------|
| English | `en` | ✅ Yes |
| Gujarati | `gu` | No |
| Hindi | `hi` | No |

English is the default language.

The selected language is stored in the browser using:

```text
agrismart_language

🛠️ Tech Stack

The frontend uses:

React
TypeScript
Vite
React Router
Tailwind CSS
Lucide React
Oxlint

🏗️ Architecture

The frontend follows a service-based architecture so that the UI can work with mock services during development and later connect to the real backend.

Current / Planned Architecture
┌─────────────────────────┐
│     React Frontend      │
│   AgriSmart AI UI       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Service / API Layer   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   FastAPI Backend       │
│     (Future)            │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       ML Model 1        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Prediction Response   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Frontend Result UI   │
└─────────────────────────┘

FastAPI and ML inference are not part of this repository.

The frontend currently uses mock services where applicable so that frontend development does not depend on the backend or ML model being available.

Important directories
src/components/

Contains reusable UI components used throughout the application.

src/pages/

Contains the main application screens such as:

Home
Login
Register
Dashboard
Scan
Result
Disease Details
History
Help
About
src/services/

Contains the frontend service/API abstraction.

This separates application logic from UI components and allows mock services to be used during development.

src/i18n/

Contains the multilingual configuration and translations for:

English
Gujarati
Hindi
src/data/

Contains application-specific data such as disease information and recommendations where applicable.

src/types/

Contains shared TypeScript types used throughout the application.

📋 Prerequisites

Before running the project, make sure you have:

Node.js
npm
Git

Check your installed versions:

node --version
npm --version
git --version
📥 Clone the Repository

Clone the frontend repository:

git clone https://github.com/aeshvi2008/AgriSmart-AI-Frontend.git

Move into the project directory:

cd AgriSmart-AI-Frontend
📦 Install Dependencies

Install all required dependencies:

npm install
Windows PowerShell

If PowerShell blocks the npm.ps1 command because of the execution policy, use:

npm.cmd install
⚙️ Environment Configuration

The project supports environment-based frontend configuration.

Create your local .env file using .env.example as the reference.

Example:

VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_API=true
VITE_API_BASE_URL

Defines the base URL for the future FastAPI backend.

Example:

VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_API

Controls mock/API service usage where supported.

For frontend development without the backend:

VITE_USE_MOCK_API=true

This allows the frontend to be developed and tested without requiring FastAPI or the ML model.

Do not commit private or environment-specific secrets to the repository.

▶️ Run the Development Server

Start the Vite development server:

npm run dev

On Windows PowerShell, you can also use:

npm.cmd run dev

Vite will display a local URL, normally similar to:

http://localhost:5173/

Open the displayed URL in your browser.

📱 Run on a Phone or Another Device

To make the development server accessible from other devices on the same local network:

npm run dev -- --host 0.0.0.0

On Windows PowerShell:

npm.cmd run dev -- --host 0.0.0.0

Vite will display a Network URL.

For example:

Network: http://192.168.x.x:5173/

Open the Network URL from your phone.

Requirements
Your phone and computer must be connected to the same Wi-Fi network.
Windows Firewall must allow the connection if required.
Your Wi-Fi network must allow devices to communicate with each other.