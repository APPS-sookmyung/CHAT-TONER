# Chat-Toner: Your AI-Powered Communication Assistant

<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/36d5fe89-d9f6-4241-ae18-7fd3b0ccb371" alt="Desktop - 61" style="max-width: 48%; height: auto;" />
  <img src="https://github.com/user-attachments/assets/31a550b8-2e2d-4a59-a725-a7e73b34b50a" alt="Desktop - 60" style="max-width: 48%; height: auto;" />
</div>

**Chat-Toner** is an intelligent text conversion and analysis service designed to refine your communication. It helps you adjust the tone and style of your writing, ensures quality and consistency, and provides a knowledge base for company-specific communication protocols.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-repo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react)
![NestJS](https://img.shields.io/badge/nestjs-E0234E?style=for-the-badge&logo=nestjs&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=langchain&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

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


## 🚀 Key Features

### 1. Intelligent Text Conversion

- **Tone & Style Adjustment:** Easily convert your text between different communication styles (e.g., formal, friendly, direct).
- **Profile-Based Conversion:** The system learns your preferences from surveys and feedback to provide personalized conversions.

![KakaoTalk_Video_2025-11-03-15-08-15](https://github.com/user-attachments/assets/4e2f8314-b65c-4c89-9faf-e78278a3cc5f)




### 2. Advanced Quality Analysis
<img width="1479" height="816" alt="image" src="https://github.com/user-attachments/assets/1e89bf07-3563-460f-8bad-6f40a0c8df38" />

- **Comprehensive Scoring:** Get scores for your text based on **Grammar**, **Formality**, **Readability**, and **Protocol Compliance**.
- **Actionable Suggestions:** Receive concrete suggestions for improving your text.
- **RAG-Powered Justification:** Understand _why_ you received a certain score. The system uses its knowledge base to provide clear justifications for its analysis.

> [Placeholder for a screenshot of the quality analysis results with justifications]

### 3. RAG-Powered Knowledge Base

| Ingestion UI | RAG Q&A UI |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/f2432139-16a1-42ce-b018-851548024682" alt="image" width="400"> | <img src="https://github.com/user-attachments/assets/52e3a1f0-b85b-4ce3-9e63-7db7354c5209" alt="image" width="400"> |

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
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/0dc24cbe-94c9-4f78-b355-fde2682c7b1e" />


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

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

- Follow the commit conventions (e.g., `feat:`, `fix:`, `docs:`).
- Ensure all tests and linting checks pass before submitting a PR.
- Update the `README.md` and any other relevant documentation if you make significant changes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

---
