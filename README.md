# 🎓 LearnHub – Open Learning Aggregator

LearnHub is a full-stack learning platform that aggregates high-quality educational resources from multiple sources into a single dashboard. Users can search learning topics, follow roadmaps, bookmark resources, track progress, and manage their learning journey.

---

## 🚀 Features

- 🔍 Search learning resources
- 📚 Learning roadmaps
- 📖 Courses and categories
- ⭐ Bookmark resources
- 📝 Personal notes
- 📈 Progress tracking
- 📊 Analytics dashboard
- 🔐 JWT Authentication
- 💾 PostgreSQL database
- ⚡ FastAPI backend
- ⚛️ React + TypeScript frontend

---

## 🛠 Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Axios
- Framer Motion

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Pydantic
- Repository Pattern
- Service Layer Architecture

---

## 📂 Project Structure

```
learn_hub/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/aruna-31/learning_hub.git
cd learning_hub
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs at

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---

## Environment Variables

### Backend

Create `backend/.env`

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

GITHUB_TOKEN=your_github_token
YOUTUBE_API_KEY=your_youtube_api_key
```

### Frontend

Create `frontend/.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

---

## 📌 API Features

- Authentication
- Search
- Dashboard
- Categories
- Courses
- Roadmaps
- Bookmarks
- Notes
- Progress Tracking
- Analytics

---

## Future Enhancements

- Google Books API
- GitHub API
- YouTube API
- Stack Exchange API
- HuggingFace Datasets
- AI-powered recommendations
- Docker Deployment
- CI/CD Pipeline

---

## 🤝 Contributing

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes
```bash
git commit -m "Add feature"
```
4. Push
```bash
git push origin feature-name
```
5. Create a Pull Request


## 👨‍💻 Author

**Lavanuru Aruna**

GitHub:
https://github.com/aruna-31

LinkedIn:
https://www.linkedin.com/in/lavanuru-aruna-700243335/
