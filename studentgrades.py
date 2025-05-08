from flask import Flask, request, jsonify
import sqlite3
import json
import time
import base64
import os
from hashfunction import decode_token, verify_token

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

def decode_token_with_verification(token):
    try:
        encoded_payload, signature = token.rsplit(".", 1)
        if verify_token(encoded_payload, signature):
            payload_json = base64.urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4)).decode("utf-8")
            return json.loads(payload_json)
        else:
            return None
    except Exception:
        return None

def check_token(request, required_permission):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False, {"error": "Missing authorization token"}

    token = auth_header.split(" ")[-1]  # Extract token from 'Bearer <token>'
    payload = decode_token_with_verification(token)
    if not payload:
        return False, {"error": "Invalid or tampered token"}

    if "exp" in payload and time.time() > payload["exp"]:
        return False, {"error": "Token expired"}

    if required_permission not in payload.get("permissions", []):
        return False, {"error": "Insufficient permissions"}

    return True, payload

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

#changeGrade("123456789", "History", "A")
#grade = getGrade("123456789", "History")
#print("Updated Grade:", grade) 



#changeGrade("123456789", "Math", "B")
#grade = getGrade("123456789", "Math")
#assert grade == "B", f"Expected 'B', but got {grade}"
#print("Test passed! Retrieved grade:", grade)


#just in case
@app.route('/grade', methods=['POST'])
def change_grade():
    authorized, response = check_token(request, "write")
    if not authorized:
        return jsonify(response), 403
    
    data = request.json
    studentId = data.get('studentId')
    className = data.get('className')
    newGrade = data.get('newGrade')

    if 'studentId' not in data or 'className' not in data or 'newGrade' not in data:
             return jsonify({"error": "Missing required fields"}), 400
    
    changeGrade(studentId, className, newGrade)
    return jsonify({"message": "Grade updated successfully"}), 200
    

@app.route('/grade', methods=['GET'])
def get_grade_endpoint():
    authorized, response = check_token(request, "read")
    if not authorized:
        return jsonify(response), 403
    
    studentId = request.args.get("studentId")
    className = request.args.get("className")
    
    if not studentId or not className:
        return jsonify({"error": "Missing required fields"}), 400
    
    grade = getGrade(studentId, className)
    if grade is not None:
        return jsonify({"grade": grade})
    else:
        return jsonify({"error": "Grade not found"}), 404
    

if __name__ == '__main__':
    app.run(debug=True)


#token used to get access to endpoint (to read and write grades) -->
#(keep the pwd secure in user acc as a feature) + authenticate and authorize user
#user verify acc to obtain token