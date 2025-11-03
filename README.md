# Chat-Toner: Your AI-Powered Communication Assistant
<img width="1432" height="611" alt="image" src="https://github.com/user-attachments/assets/60b67dfb-be5c-4ec8-aaab-d5dbae453720" />

<img width="1697" height="892" alt="image" src="https://github.com/user-attachments/assets/73fab338-d302-41d8-8794-cc670b1ede58" />


**Chat-Toner** is an intelligent text conversion and analysis service designed to refine your communication. It helps you adjust the tone and style of your writing, ensures quality and consistency, and provides a knowledge base for company-specific communication protocols.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-repo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 👋 Team Introduction

| Name       | Role                                                       | Email                |
| ---------- | ---------------------------------------------------------- | -------------------- |
| Yoon Jiwon | Project Lead                                               | jiwon@example.com    |
| Ha Jimin   | Frontend, UI/UX Research & Design                          | jimin@example.com    |
| Jung Jieun | Infrastructure & Architecture Orchestration                | jieun@example.com    |
| Kim Jimin  | RAG Construction, Langchain Agentic Flow & Learning System | ha.jimin@example.com |

---

## ✨ Demo

[![](https://img.shields.io/badge/Watch-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=your-video-id)

> [Placeholder for a GIF demonstrating the core text conversion feature]

## 🚀 Key Features

### 1. Intelligent Text Conversion

- **Tone & Style Adjustment:** Easily convert your text between different communication styles (e.g., formal, friendly, direct).
- **Profile-Based Conversion:** The system learns your preferences from surveys and feedback to provide personalized conversions.

> [Placeholder for a screenshot of the text conversion interface]

### 2. Advanced Quality Analysis

- **Comprehensive Scoring:** Get scores for your text based on **Grammar**, **Formality**, **Readability**, and **Protocol Compliance**.
- **Actionable Suggestions:** Receive concrete suggestions for improving your text.
- **RAG-Powered Justification:** Understand _why_ you received a certain score. The system uses its knowledge base to provide clear justifications for its analysis.

> [Placeholder for a screenshot of the quality analysis results with justifications]

### 3. RAG-Powered Knowledge Base

- **Document Ingestion:** Build a company-specific knowledge base by uploading documents (PDFs, etc.).
- **Contextual Q&A:** Ask questions and get answers based on the ingested documents, ensuring everyone follows the same guidelines.

### 4. Company & User Profiles

- **Onboarding Surveys:** Quickly set up company-wide communication styles and protocols through a simple survey.
- **Personalized Experience:** User-specific profiles store preferences and feedback, making the tool more effective over time.

## 🛠️ Tech Stack

| Category           | Technology                                            |
| ------------------ | ----------------------------------------------------- |
| **Frontend**       | React, TypeScript, Vite, Tailwind CSS, TanStack Query |
| **API Gateway**    | NestJS, TypeScript                                    |
| **Backend (Core)** | Python, FastAPI                                       |
| **AI & ML**        | LangChain, OpenAI (GPT-4), PGVector                   |
| **Database**       | PostgreSQL (with PGVector extension)                  |
| **DevOps**         | Docker, Docker Compose, GitHub Actions                |
| **Testing**        | Jest, Pytest                                          |
| **Code Quality**   | ESLint, Prettier, Ruff                                |

## 🏛️ Architecture

The Chat-Toner service is built on a microservices architecture, with a React frontend, a NestJS API gateway, and a Python backend for core AI/ML and business logic.

> [Placeholder for the RAG Architecture Diagram]

## 📂 Directory Structure

```
.
├── packages/
│   ├── client/          # React Frontend
│   ├── nestjs-gateway/  # NestJS API Gateway
│   └── python_backend/  # FastAPI Backend (Core Logic & RAG)
├── database/            # Database migration scripts
├── infra/               # Infrastructure configs (e.g., task definitions)
├── docker-compose.yml   # Local development setup
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- Docker & Docker Compose

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/2025-CHATTONER-Server.git
    cd 2025-CHATTONER-Server
    ```

2.  **Set up environment variables:**
    Create a `.env.local` file in the root directory and add the necessary environment variables. You can use `.env.example` as a template.

    ```bash
    cp .env.example .env.local
    ```

    Key variables to set:
    - `OPENAI_API_KEY`: Your OpenAI API key.
    - `DATABASE_URL`: The connection string for your PostgreSQL database.

3.  **Install dependencies for all packages:**
    _This project uses `npm` workspaces. Run the command from the root directory._
    ```bash
    npm install
    ```
    This will install dependencies for the `client`, `nestjs-gateway`, and set up the Python environment for `python_backend`.

### Running the Application

You can run all services together using Docker Compose.

```bash
docker-compose up --build
```

The services will be available at:

- **Frontend:** `http://localhost:3000`
- **API Gateway:** `http://localhost:8080`
- **Backend:** `http://localhost:8000`

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

- Follow the commit conventions (e.g., `feat:`, `fix:`, `docs:`).
- Ensure all tests and linting checks pass before submitting a PR.
- Update the `README.md` and any other relevant documentation if you make significant changes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

---
