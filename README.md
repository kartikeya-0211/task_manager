# 📋 TaskFlow — Team Task Manager
 
> A full-stack, role-based Team Task Manager built with **FastAPI**, **SQLite**, and **Vanilla JS**.
 
---
 
## 🌐 Live Demo
 
🔗 **[Live App on Railway](https://taskmanager-production-d537.up.railway.app/)** 
📁 **[GitHub Repository](https://github.com/kartikeya-0211/task_manager)**
 
---
 
## 📌 Overview
 
TaskFlow is a collaborative task management web application where users can create projects, manage teams, assign tasks, and track progress — all with role-based access control differentiating **Admins** from **Members**.
 
---
 
## 🚀 Features
 
### 🔐 Authentication
- Secure user **Signup & Login** with hashed passwords (bcrypt)
- JWT-based stateless authentication
- Token expiry and protected routes
### 👥 Role-Based Access Control
- **Admin**: Create/delete projects, manage team members, assign tasks to anyone
- **Member**: View assigned projects, update their own task statuses
### 📁 Project Management
- Create and manage multiple projects
- Add/remove team members per project
- Each project has an owner and a description
### ✅ Task Management
- Create tasks with title, description, priority, and due date
- Assign tasks to specific team members
- Track task status: `Todo` → `In Progress` → `Done`
- Set priority levels: `Low`, `Medium`, `High`
### 📊 Dashboard
- Overview of all tasks and their statuses
- Overdue task highlighting
- Tasks grouped by project and status
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) |
| **Database** | SQLite via SQLAlchemy ORM |
| **Authentication** | JWT (python-jose) + bcrypt (passlib) |
| **Frontend** | Vanilla JavaScript, HTML, CSS |
| **Validation** | Pydantic v2 |
| **Server** | Uvicorn (ASGI) |
| **Deployment** | Railway |
 
---

### Prerequisites
- Python 3.10+
### 1. Clone the repository
```bash
git clone https://github.com/kartikeya-0211/task_manager.git
cd task_manager
```
 
### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```
 
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
 
### 4. Run the application
```bash
uvicorn main:app --reload
```
 
### 5. Open in browser
```
http://localhost:8000
```
 
---
## 🔒 Security
 
- Passwords are hashed using **bcrypt** before storage — never stored in plain text
- All protected routes require a valid **JWT Bearer token**
- Role checks are enforced at the API layer for Admin-only operations
- Pydantic schemas validate and sanitize all incoming request data
---
 
## 👤 Author
 
**Kartikeya**
[GitHub](https://github.com/kartikeya-0211)
 
---
 
## 📄 License
 
This project is built as part of a full-stack assignment submission.
