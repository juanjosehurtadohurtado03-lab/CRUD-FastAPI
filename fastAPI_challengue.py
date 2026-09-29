import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

def get_db():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_table():
    conn = sqlite3.connect('tasks.db')
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        complete INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

create_table()
app = FastAPI()

class Task(BaseModel):
    title: str
    complete: int = 0

@app.post('/task')
def create_task(task: Task, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (title, complete) VALUES (?, ?)", (task.title, task.complete))
    db.commit()
    id = cursor.lastrowid
    return {'id': id, 'title': task.title, 'complete': task.complete}

@app.get('/task')
def get_tasks(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute('SELECT id, title, complete FROM tasks')
    return cursor.fetchall()

@app.get('/task/{task_id}')
def get_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, title, complete FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tarea no encontrada'
        )
    return task

@app.put('/task/{task_id}')
def update_task(task_id: int, task: Task, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute('UPDATE tasks SET title = ?, complete = ? WHERE id = ?', (task_id, task.title, task.complete))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tarea no encontrada'
        )
    db.commit()
    return {'id': task_id, 'title': task.title, 'complete': task.complete}

@app.delete('/task/{task_id}')
def delete_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Tarea no encontrada'
            )
    db.commit()