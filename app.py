from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'honoG-secret-key-123'

def init_db():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            course TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        sample_data = [
            ('Aline Uwimana', 20, 'uwalice@example.rw', 'Computer Science'),
            ('Jack Mukiza', 22, 'Jackmu@example.rw', 'History'),
            ('Davis Shema', 21, 'Shemada@example.rw', 'Management')
        ]
        cur.executemany("INSERT INTO students (name, age, email, course) VALUES (?, ?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        course = request.form['course']

        conn = get_db_connection()
        conn.execute('INSERT INTO students (name, age, email, course) VALUES (?, ?, ?, ?)',
                    (name, age, email, course))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_student.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        course = request.form['course']

        conn.execute('UPDATE students SET name = ?, age = ?, email = ?, course = ? WHERE id = ?',
                    (name, age, email, course, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()

    if student is None:
        return redirect(url_for('index'))

    return render_template('edit_student.html', student=student)

@app.route('/view/<int:id>')
def view_student(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()

    if student is None:
        return redirect(url_for('index'))

    return render_template('view_student.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/api/students')
def api_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students ORDER BY created_at DESC').fetchall()
    conn.close()

    students_list = []
    for student in students:
        students_list.append({
            'id': student['id'],
            'name': student['name'],
            'age': student['age'],
            'email': student['email'],
            'course': student['course']
        })

    return jsonify(students_list)

if __name__ == '__main__':
    app.run(debug=True)
