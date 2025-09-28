# ChatToner  

**Personalized Tone Transformation System**  
Chat-toner is a service that transforms communication style according to the situation and audience.  
It continuously improves recommendations and coaching based on user feedback.  

Deployment URL: https://client-184664486594.asia-northeast3.run.app

---

## Project Overview  

Chat-toner goes beyond simple tone conversion by recommending personalized styles based on conversation goals, situations, and audiences.  
It gradually evolves into a highly personalized tone transformation system by learning users’ unique speech habits.  

---

## Key Features  

- **Tone Suggestions by Situation**  
  - Automatically suggests tones suited for contexts such as work, friends, and formal conversations  
- **Audience and Goal-Based Style Recommendations**  
- **Sentence Transformation & Real-Time Feedback**  
  - Provides multiple transformed versions of a sentence with selection options  
  - Real-time feedback/editing UI  
- **Personalized Habit Learning**  
  - LoRA-based user tone modeling  
  - Continuous personalization through user selections and feedback  

---

## Tech Stack  

| Category      | Stack/Library                                | Purpose                              |
| :------------ | :------------------------------------------- | :----------------------------------- |
| **Frontend**  | React.js, TypeScript, Zustand                | Interface, type safety, state management |
| **Backend**   | Flask, FastAPI, Express.js                   | ML API, proxy, static files          |
| **ML**        | LoRA, KoGPT, KoAlpaca, HuggingFace Transformers | Style transformation, text generation |
| **Database**  | PostgreSQL, FAISS, Redis                     | Data storage, vector search, caching |

---

## Project Structure  

chattoner/
├── client/
│ └── ... (React frontend)
├── server/
│ └── ... (Express proxy)
├── python_backend/
│ ├── app/
│ ├── ml/
│ └── requirements.txt
├── docker-compose.yml
└── README.md

---

## Installation & Setup  

1. **Clone the Project**  

   ```bash
   git clone https://github.com/your-username/chat-toner.git
   cd chat-toner
   
2. **Install Dependencies**

npm install              # Node.js
cd client && npm install # Client
cd ../python_backend && pip install -r requirements.txt

3. **Database & Environment Variables**
   
createdb chattoner
cp .env.example .env
# Update DB connection info in .env

4. **Run the Project**
   
npm run dev          # Run all services in dev mode
# Or run separately
npm run client       # React
npm run server       # Express
npm run python       # Flask

---

## Usage  

- Input text → Select context (Work/Friends/Formal) → Choose transformation option → Provide feedback on results  

---

## Development Strategy  

- **MVP**: Start with prompt-based core features  
- **Model Development**: Enhance personalization with LoRA  
- **Integration**: Optimize RAG and vector search  
- **Performance/UX Optimization**  

---

## Evaluation  

- Manual evaluation of appropriateness, user O/X satisfaction survey  
- A/B testing with different algorithms  

---

## Contributing  

1. Fork this repo  
2. Create a feature branch (`git checkout -b feature/NewFeature`)  
3. Commit changes (`git commit -m 'Add ...'`)  
4. Push to branch (`git push origin feature/NewFeature`)  
5. Submit a Pull Request  

---

## Team  

| Name         | Role        | Responsibilities               | Contact                  |
| :----------- | :---------- | :----------------------------- | :----------------------- |
| **Yoon Ji-won** | PM          | Project planning & management  | geenieeyoon@gmail.com    |
| **Kwon Yu-jin** | Development | Full-stack, ML model support  | thinz0083@daum.net       |
| **Kim Ji-min**  | Development | Fine-tuning, RAG implementation | onlypotato637@gmail.com |
| **Jeong Ji-eun** | Development | Model development, fine-tuning | jje49jieun@gmail.com    |
| **Ha Ji-min**   | Development | Frontend design & implementation, API integration | tracygkwlals@gmail.com |

> **APPS (App/Web Development Society)**  
> This project is carried out as a research project by the APPS academic society of the Department of Software at Sookmyung Women’s University.  

---

## Contact  

- Email: [APPS Society Email]  
- GitHub: [https://github.com/APPS-sookmyung/2025-CHATTONER-Server]  
