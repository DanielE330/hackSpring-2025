from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# Модель данных для задачи
class Task(BaseModel):
    id: int
    title: str
    description: str
    image: Optional[str] = None
    assignee: str
    priority: str
    status: str
    date: str

# Модель данных для создания/обновления задачи
class TaskCreate(BaseModel):
    title: str
    description: str
    image: Optional[str] = None
    assignee: str
    priority: str

# Временное хранилище данных (в реальном проекте используйте базу данных)
tasks_db = []
history_db = []

# Получить все задачи
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks_db

# Получить задачу по ID
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    task = next((t for t in tasks_db if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

# Создать новую задачу
@app.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate):
    new_id = len(tasks_db) + 1
    new_task = Task(
        id=new_id,
        title=task_data.title,
        description=task_data.description,
        image=task_data.image,
        assignee=task_data.assignee,
        priority=task_data.priority,
        status="current",
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    tasks_db.append(new_task)
    history_db.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": "Пользователь",  # В реальном проекте используйте аутентификацию
        "task_title": task_data.title,
        "event": "Создание"
    })
    return new_task

# Обновить существующую задачу
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_data: TaskCreate):
    task = next((t for t in tasks_db if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task.title = task_data.title
    task.description = task_data.description
    task.image = task_data.image
    task.assignee = task_data.assignee
    task.priority = task_data.priority
    task.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history_db.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": "Пользователь",  # В реальном проекте используйте аутентификацию
        "task_title": task.title,
        "event": "Изменение"
    })
    return task

# Удалить задачу
@app.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int):
    global tasks_db
    task = next((t for t in tasks_db if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    tasks_db = [t for t in tasks_db if t.id != task_id]

    history_db.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": "Пользователь",  # В реальном проекте используйте аутентификацию
        "task_title": task.title,
        "event": "Удаление"
    })
    return {"message": "Задача успешно удалена"}

# Изменить статус задачи
@app.patch("/tasks/{task_id}/status", response_model=Task)
async def change_status(task_id: int, status: str):
    task = next((t for t in tasks_db if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task.status = status
    task.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history_db.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": "Пользователь",  # В реальном проекте используйте аутентификацию
        "task_title": task.title,
        "event": f"Изменение статуса на {status}"
    })
    return task

# Получить историю изменений
@app.get("/history", response_model=List[dict])
async def get_history():
    return history_db