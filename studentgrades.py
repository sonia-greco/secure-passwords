from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db2_connection():
    conn = sqlite3.connect('studentgrades.db', check_same_thread=False)
    return conn

def empty_db():
    conn = get_db2_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM gradestable")
    conn.commit()
    cur.close()
    conn.close()

conn = get_db2_connection()
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS gradestable (
    studentId TEXT,
    className TEXT,
    grade TEXT,
    PRIMARY KEY (studentId, className)
)
''')

conn.commit()
cur.close()
conn.close()

def changeGrade(studentId, className, newGrade):
    conn = get_db2_connection()
    cur = conn.cursor()

    cur.execute("SELECT grade FROM gradestable WHERE studentId = ? AND className = ?", (studentId, className))
    row = cur.fetchone()

    if row:
        cur.execute("UPDATE gradestable SET grade = ? WHERE studentId = ? AND className = ?", (newGrade, studentId, className))
    else:
        cur.execute("INSERT INTO gradestable (studentId, className, grade) VALUES (?, ?, ?)", (studentId, className, newGrade))

    conn.commit()
    cur.close()
    conn.close()
    print("Grade updated successfully")

def getGrade(studentId, className):
    conn = get_db2_connection()
    cur = conn.cursor()
    cur.execute("SELECT grade FROM gradestable WHERE studentId = ? AND className = ?", (studentId, className))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return row[0]
    else:
        print("Grade not found")
        return None

# Test case: Updating grade for an existing student-class pair
changeGrade("123456789", "History", "A")

# Verify the update
grade = getGrade("123456789", "History")
print("Updated Grade:", grade)  # Expected output: "Updated Grade: A"



# Setup: Insert a test grade
changeGrade("123456789", "Math", "B")

# Test: Retrieve the grade
grade = getGrade("123456789", "Math")

# Check if the result matches the expected grade
assert grade == "B", f"Expected 'B', but got {grade}"

print("Test passed! Retrieved grade:", grade)