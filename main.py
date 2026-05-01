from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from database import engine, get_db
import models, schemas, auth
import logging
import sys

# ── LOGGING SETUP ─────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("taskflow.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root(): return FileResponse("static/index.html")

# ── AUTH ──────────────────────────────────────────
@app.post("/api/signup")
def signup(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(400, "Email already exists")
    user = models.User(name=data.name, email=data.email, role=data.role,
                       password_hash=auth.hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return schemas.UserOut(id=user.id, name=user.name, email=user.email,
                           role=user.role, token=auth.create_token({"sub": str(user.id)}))

@app.post("/api/login")
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=data.email).first()
    
    logger.info(f"Login attempt for email: {data.email}")
    if user:
        logger.info("Found user in DB.")
    else:
        logger.error(f"FAILED: User {data.email} not found in DB!")

    if not user or not auth.verify_password(data.password, user.password_hash):
        logger.error(f"FAILED: Invalid password for {data.email}")
        raise HTTPException(401, "Invalid credentials")
        
    return schemas.UserOut(id=user.id, name=user.name, email=user.email,
                           role=user.role, token=auth.create_token({"sub": str(user.id)}))

@app.get("/api/me")
def me(u=Depends(auth.get_current_user)):
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role}

# ── USERS ─────────────────────────────────────────
@app.get("/api/users")
def users(db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    return [{"id": x.id, "name": x.name, "email": x.email, "role": x.role}
            for x in db.query(models.User).all()]

# ── PROJECTS ──────────────────────────────────────
@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role == "admin":
        projects = db.query(models.Project).all()
    else:
        ids = [m.project_id for m in db.query(models.ProjectMember).filter_by(user_id=u.id)]
        projects = db.query(models.Project).filter(models.Project.id.in_(ids)).all()
    return [_proj(p, db) for p in projects]

@app.get("/api/projects/{pid}")
def get_project(pid: int, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    p = db.query(models.Project).filter_by(id=pid).first()
    if not p: raise HTTPException(404, "Not found")
    
    if u.role != "admin":
        m = db.query(models.ProjectMember).filter_by(project_id=pid, user_id=u.id).first()
        if not m: raise HTTPException(403, "Access denied")
            
    return _proj(p, db)

@app.post("/api/projects")
def create_project(data: schemas.ProjectCreate, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role != "admin": raise HTTPException(403, "Admins only")
    p = models.Project(name=data.name, description=data.description, owner_id=u.id)
    db.add(p); db.commit(); db.refresh(p)
    db.add(models.ProjectMember(project_id=p.id, user_id=u.id)); db.commit()
    return _proj(p, db)

@app.delete("/api/projects/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role != "admin": raise HTTPException(403, "Admins only")
    p = db.query(models.Project).filter_by(id=pid).first()
    if not p: raise HTTPException(404, "Not found")
    db.delete(p); db.commit()
    return {"ok": True}

@app.post("/api/projects/{pid}/members")
def add_member(pid: int, data: dict, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role != "admin": raise HTTPException(403, "Admins only")
    db.add(models.ProjectMember(project_id=pid, user_id=data["user_id"])); db.commit()
    return {"ok": True}

@app.delete("/api/projects/{pid}/members/{uid}")
def remove_member(pid: int, uid: int, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role != "admin": raise HTTPException(403, "Admins only")
    m = db.query(models.ProjectMember).filter_by(project_id=pid, user_id=uid).first()
    if m: db.delete(m); db.commit()
    return {"ok": True}

# ── TASKS ─────────────────────────────────────────
@app.get("/api/projects/{pid}/tasks")
def list_tasks(pid: int, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    return [_task(t, db) for t in db.query(models.Task).filter_by(project_id=pid).all()]

@app.post("/api/projects/{pid}/tasks")
def create_task(pid: int, data: schemas.TaskCreate, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role != "admin": raise HTTPException(403, "Admins only")
    
    t = models.Task(title=data.title, description=data.description, status=data.status,
                    priority=data.priority, due_date=data.due_date,
                    project_id=pid, created_by=u.id, assigned_to=data.assigned_to)
    db.add(t); db.commit(); db.refresh(t)
    return _task(t, db)

@app.put("/api/tasks/{tid}")
def update_task(tid: int, data: schemas.TaskUpdate, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    t = db.query(models.Task).filter_by(id=tid).first()
    if not t: raise HTTPException(404, "Not found")

    if u.role != "admin":
        if t.assigned_to != u.id:
            logger.warning(f"User {u.id} tried to edit unassigned task {tid}")
            raise HTTPException(403, "You can only update tasks assigned to you")
        # Only allow status updates for non-admins
        if data.status:
            t.status = data.status
            logger.info(f"User {u.id} updated status of task {tid} to {data.status}")
    else:
        for field, val in data.model_dump(exclude_none=True).items():
            setattr(t, field, val)

    db.commit(); db.refresh(t)
    return _task(t, db)

@app.delete("/api/tasks/{tid}")
def delete_task(tid: int, db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role != "admin": raise HTTPException(403, "Admins only")
    t = db.query(models.Task).filter_by(id=tid).first()
    if t: db.delete(t); db.commit()
    return {"ok": True}

# ── DASHBOARD ─────────────────────────────────────
@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), u=Depends(auth.get_current_user)):
    if u.role == "admin":
        tasks = db.query(models.Task).all()
    else:
        # Get all project IDs this member belongs to
        proj_ids = [m.project_id for m in db.query(models.ProjectMember).filter_by(user_id=u.id)]
        # Grab all tasks from those projects, regardless of who they are assigned to
        tasks = db.query(models.Task).filter(models.Task.project_id.in_(proj_ids)).all()
        
    now = datetime.utcnow()
    
    # Grab the 5 most recently created tasks
    recent_tasks = sorted(tasks, key=lambda x: x.id, reverse=True)[:5]
    
    return {
        "total_tasks": len(tasks),
        "todo":        sum(1 for t in tasks if t.status == "todo"),
        "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
        "done":        sum(1 for t in tasks if t.status == "done"),
        "overdue":     [_task(t, db) for t in tasks if t.due_date and t.due_date < now and t.status != "done"],
        "recent":      [_task(t, db) for t in recent_tasks]
    }
# ── HELPERS ───────────────────────────────────────
def _proj(p, db):
    members = db.query(models.User).join(models.ProjectMember, models.User.id == models.ProjectMember.user_id)\
                .filter(models.ProjectMember.project_id == p.id).all()
    tasks = db.query(models.Task).filter_by(project_id=p.id).all()
    return {"id": p.id, "name": p.name, "description": p.description, "owner_id": p.owner_id,
            "members": [{"id": m.id, "name": m.name, "role": m.role} for m in members],
            "task_count": len(tasks), "done_count": sum(1 for t in tasks if t.status == "done")}

def _task(t, db):
    assignee = db.query(models.User).filter_by(id=t.assigned_to).first() if t.assigned_to else None
    proj = db.query(models.Project).filter_by(id=t.project_id).first()
    return {"id": t.id, "title": t.title, "description": t.description, "status": t.status,
            "priority": t.priority, "due_date": t.due_date, "project_id": t.project_id,
            "project_name": proj.name if proj else "", "assigned_to": t.assigned_to,
            "assignee_name": assignee.name if assignee else None,
            "is_overdue": bool(t.due_date and t.due_date < datetime.utcnow() and t.status != "done")}