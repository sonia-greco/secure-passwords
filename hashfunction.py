from flask import Flask, request, jsonify
import sqlite3

# Initialize Flask app
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('hashedpotatoes.db', check_same_thread=False)
    return conn

# '''
# cur.execute('''
# DELETE FROM myusertable
# ''')
# '''

conn = get_db_connection()
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS myusertable (
  username TEXT PRIMARY KEY, 
  hash TEXT NOT NULL
)
''')
conn.commit()
cur.close()
conn.close()

def createAccount(userName, password):
	hashedpwd = str(hash(password))
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("INSERT INTO myusertable (username, hash) VALUES (?, ?)", (userName, hashedpwd))
	conn.commit()
	cur.close()
	conn.close()
	print('Password is ' + str(hashedpwd))


def verifyAccount(userName, password):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("SELECT hash FROM myusertable WHERE username = ?", (userName,))
	rows = cur.fetchall()
	if len(rows) == 0:
		print('Username not found')
		return False
	first_row = rows[0]
	hashInDB = first_row[0]
	conn.commit()
	cur.close()
	conn.close()
	if hashInDB == str(hash(password)):
		return True
	else:
		print('Password not found')
		return False

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

    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username or password are required'}), 400
    else: 
        createAccount(username, password)
        return jsonify({'message': 'Account created successfully'}), 201

#API endpoint to verify an account
@app.route('/verifyAccount', methods=['POST'])
def verify_account():
	data = request.json
	username = data.get('username')
	password = data.get('password')

	if 'username' not in data or 'password' not in data:
		return jsonify({'error': 'Incorrect username or password'}), 400
	
	validAccount = verifyAccount(username, password)

	if validAccount == True:
		return jsonify({'message': 'Account is verified'}), 200
	else:
		return jsonify({'error': 'Account not verified'}), 401

#API endpoint to change a password
@app.route('/changePassword', methods=['POST'])
def change_password():
	data = request.json
	username = data.get('username')
	password = data.get('password')
	newpwd = data.get('newPassword')

	if 'username' not in data or 'password' not in data or 'newpwd' not in data:
		return jsonify({'error': 'Missing username, password, or new password'}), 400
	
	changedpwd = changePassword(username, password, newpwd)

	if changedpwd == True:
		return jsonify({'message': 'Password changed successfully'}), 200
	else:
		return jsonify({'error': 'Password not changed successfully'}), 401
	#problem is that when you try to verify an account after changing its pwd successfully, it returns account not verified

#Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
