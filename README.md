# LearnHub — Learning Resource Aggregator

> Full-stack learning platform that brings educational resources, roadmaps, bookmarks, notes, and progress tracking into one dashboard.

## Problem

Learning resources are spread across many platforms. LearnHub explores a unified workflow where users can search resources, organize learning paths, save useful material, and track progress.

## Features

- Resource search
- Learning roadmaps
- Courses and categories
- Bookmarks
- Personal notes
- Progress tracking
- Analytics dashboard
- JWT authentication
- PostgreSQL persistence

## Architecture

```
React + TypeScript
        |
     Axios/API
        v
FastAPI
        |
   SQLAlchemy
        |
   PostgreSQL
```

## Tech stack

**Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Axios, Framer Motion

**Backend:** FastAPI, SQLAlchemy, Pydantic, JWT authentication, repository/service layers

**Database:** PostgreSQL

## Run locally

Backend:

```bash
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Configure database, JWT, and external API credentials through local environment files. Never commit secrets.

## API areas

Authentication, search, categories, courses, roadmaps, bookmarks, notes, progress, and analytics.

## Author

**Lavanuru Aruna** · https://github.com/aruna-31
