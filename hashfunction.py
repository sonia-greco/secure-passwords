from flask import Flask, request, jsonify
import sqlite3
import json
import time
import base64
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

#Constants
ISSUER = "https://auth.sonia.com"
AUDIENCE = "https://api.sonia.com"
PERMISSIONS = ["read", "write"]
TOKEN_EXPIRATION_TIME = 3600

# Load RSA keys
with open("keys/private_key.pem", "rb") as key_file:
    PRIVATE_KEY = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

with open("keys/public_key.pem", "rb") as key_file:
    PUBLIC_KEY = serialization.load_pem_public_key(key_file.read())

def sign_token(payload):
    """
    Signs the token using the private key.

    Args:
        payload (str): The payload to be signed (JSON string).

    Returns:
        str: The signed token (Base64 encoded).
    """
    signature = PRIVATE_KEY.sign(
        payload.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.urlsafe_b64encode(signature).decode("utf-8")

def verify_token(payload, signature):
    """
    Verifies the token using the public key.

    Args:
        payload (str): The payload to verify (JSON string).
        signature (str): The Base64-encoded signature.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        PUBLIC_KEY.verify(
            base64.urlsafe_b64decode(signature),
            payload.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False

def encode_token(payload):
    payload_json = json.dumps(payload)
    encoded_payload = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    signature = sign_token(encoded_payload)
    return f"{encoded_payload}.{signature}"

def decode_token(token):
    try:
        encoded_payload, signature = token.rsplit(".", 1)
        if verify_token(encoded_payload, signature):
            payload_json = base64.urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4)).decode("utf-8")
            return json.loads(payload_json)
        else:
            return None
    except Exception:
        return None

#Initialize Flask app
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('hashedpotatoes.db', check_same_thread=False)
    return conn


#Clear data table
def empty_db():
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute('''
	DELETE FROM myusertable
	''')
	conn.commit()
	cur.close()
	conn.close()

def delete_tables():
    """
    Deletes all tables in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    for table_name in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table_name[0]}")
    conn.commit()
    cur.close()
    conn.close()
    print("All tables deleted successfully.")

# delete_tables()
# empty_db()

conn = get_db_connection()
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS myusertable (
  username TEXT PRIMARY KEY, 
  hash TEXT NOT NULL,
  readperm INTEGER DEFAULT 0,
  writeperm INTEGER DEFAULT 0
)
''')
conn.commit()
cur.close()
conn.close()

def createAccount(userName, password, readPerm=0, writePerm=0):
	hashedpwd = str(hash(password))
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("INSERT INTO myusertable (username, hash, readperm, writeperm) VALUES (?, ?, ?, ?)", (userName, hashedpwd, readPerm, writePerm))
	conn.commit()
	cur.close()
	conn.close()
	print('Password is ' + str(hashedpwd))


def verifyAccount(userName, password):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("SELECT hash,readperm,writeperm FROM myusertable WHERE username = ?", (userName,))
	rows = cur.fetchall()
	if len(rows) == 0:
		print('Username not found')
		return False
	first_row = rows[0]
	hashInDB, readperm, writeperm = first_row
	conn.commit()
	cur.close()
	conn.close()
	if hashInDB == str(hash(password)):
		iat = int(time.time())  # Issue timestamp
		exp = iat + TOKEN_EXPIRATION_TIME  # Expiration timestamp
	
		payload = {
			"sub": userName,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "iat": iat,
            "exp": exp,
            "permissions": {
				"read": bool(readperm),
				"write": bool(writeperm)
			}
		}

		return payload
	else:
		print('Password not found')
		return None

def changePassword(userName, password, newPassword):
	accountExists = verifyAccount(userName, password)
	conn = get_db_connection()
	cur = conn.cursor()
	if accountExists:
		hashedpwd = str(hash(newPassword))
		cur.execute("UPDATE myusertable SET hash = ? WHERE userName = ?", (hashedpwd, userName))
		conn.commit()
		cur.close()
		conn.close()
		return True
	else:
		return False
	

"""
print('Please create an account')

for i in range(1):
	userName = input('Input username: ')
	password = input('Input password: ')
	createAccount(userName, password)

continueVerify = 'V'

while continueVerify == 'V':

	print('Please verify your account:')

	checkUsername = input('Input USERNAME: ')
	checkPassword = input('Input PASSWORD: ')

	accountExists = verifyAccount(checkUsername, checkPassword)
	if accountExists == True:
		print('Account verified')
	else:
		print('Account not verified')

	continueVerify = input('Do you want to continue to verify or create a new password? \nV for verify or P for password: ')

createNewPwd = 'P'

while createNewPwd == 'P':

	currentuser = input('Input USERNAME: ')
	currentpwd = input('Input CURRENT PASSWORD: ')

	accountExists = verifyAccount(currentuser, currentpwd)
	if accountExists == True:
		newPassword = input('Please input new password: ')
		passwordChanged = changePassword(currentuser, currentpwd, newPassword)
	else:
		print('Account not found')

	createNewPwd = input('Do you want to change another password? \nY for yes and N for no: ')
"""

#API endpoint to create an account
@app.route('/createAccount', methods=['POST'])
def create_account():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    readperm = data.get('readperm', 0)
    writeperm = data.get('writeperm', 0)

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username or password are required'}), 400
    else: 
        createAccount(username, password, readperm, writeperm)
        return jsonify({'message': 'Account created successfully'}), 201

#API endpoint to verify an account
@app.route('/verifyAccount', methods=['POST'])
def verify_account():
	data = request.json
	username = data.get('username')
	password = data.get('password')

	if 'username' not in data or 'password' not in data:
		return jsonify({'error': 'Incorrect username or password'}), 400
	
	token = verifyAccount(username, password)

	if token == None:
		return jsonify({'error': 'Account not verified'}), 401
	else:
		payload = {
			"token": encode_token(token)
		}
		return jsonify(payload), 200

#API endpoint to change a password
@app.route('/changePassword', methods=['POST'])
def change_password():
	data = request.json
	username = data.get('username')
	password = data.get('password')
	newpwd = data.get('newPassword')

	if 'username' not in data or 'password' not in data or 'newPassword' not in data:
		return jsonify({'error': 'Missing username, password, or new password'}), 400
	
	changedpwd = changePassword(username, password, newpwd)
	
	if changedpwd == True:
		return jsonify({'message': 'Password changed successfully'}), 200
	else:
		return jsonify({'error': 'Password not changed successfully'}), 401

#Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)