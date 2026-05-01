# 📋 Team Task Manager

> A full-stack, role-based Team Task Manager built with **FastAPI**, **SQLite**, and **Vanilla JS**.

---

## 🌐 Live Demo

🔗 **[Live App on Railway](https://taskmanager-production-d537.up.railway.app/)**
📁 **[GitHub Repository](https://github.com/kartikeya-0211/task_manager)**

---

## 📌 Overview

Team Task Manager is a collaborative task management web application where users can create projects, manage teams, assign tasks, and track progress — all with role-based access control differentiating **Admins** from **Members**.

---

## 🚀 Features

### 🔐 Authentication
- Secure user **Signup & Login** with hashed passwords (bcrypt)
- JWT-based stateless authentication
- Token expiry and protected routes

### 👥 Role-Based Access Control
- **First user to register** is automatically assigned the **Admin** role
- All subsequent signups are assigned the **Member** role by default
- **Admin**: Create projects, manage team members, assign tasks, promote/demote users
- **Member**: View assigned projects, update status of their own tasks only
- Admins can promote any Member to Admin (or demote) via the User Management panel
- Role assignment is enforced entirely on the backend — cannot be manipulated from the frontend

### 👤 User Management (Admin only)
- Dedicated **Users** page visible only to Admins
- Admins can promote Members to Admin or demote Admins to Members with one click
- Admins cannot change their own role

### 📁 Project Management
- Create and manage multiple projects
- Add/remove team members per project
- Each project has an owner and a description
- Members only see projects they have been explicitly added to

### ✅ Task Management
- Create tasks with title, description, priority, and due date
- Assign tasks to specific team members
- Track task status: `Todo` → `In Progress` → `Done`
- Set priority levels: `Low`, `Medium`, `High`

### 📊 Dashboard
- Overview of all tasks and their statuses
- Overdue task highlighting
- Recent tasks feed
- Admin sees all tasks; Members see only tasks within their projects

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) |
| **Database** | SQLite via SQLAlchemy ORM |
| **Authentication** | JWT (python-jose) + bcrypt |
| **Frontend** | Vanilla JavaScript, HTML, CSS |
| **Validation** | Pydantic v2 |
| **Server** | Uvicorn (ASGI) |
| **Deployment** | Railway |

---

## ⚙️ Local Setup

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

## 🔑 How Roles Work

| Action | Admin | Member |
|--------|-------|--------|
| First signup auto-assigned | ✅ Admin | — |
| All subsequent signups | — | ✅ Member |
| Create / delete projects | ✅ | ❌ |
| Add / remove project members | ✅ | ❌ |
| Create / delete tasks | ✅ | ❌ |
| Assign tasks to users | ✅ | ❌ |
| Update status of assigned tasks | ✅ | ✅ |
| Promote / demote users | ✅ | ❌ |
| View User Management panel | ✅ | ❌ |

---

## 🔒 Security

- Passwords hashed using **bcrypt** — never stored in plain text
- All protected routes require a valid **JWT Bearer token**
- Role checks enforced at the **API layer** — UI restrictions alone are never trusted
- Pydantic schemas validate and sanitize all incoming request data
- Users cannot self-assign the Admin role at signup

---

## 👤 Author

**Kartikeya**
[GitHub](https://github.com/kartikeya-0211)

---

## 📄 License

This project is built as part of a full-stack assignment submission.