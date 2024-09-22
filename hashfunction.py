import sqlite3
import os

con = sqlite3.connect('hashedpotatoes.db')

cur = con.cursor()

# '''
# cur.execute('''
# DELETE FROM myusertable
# ''')
# '''

cur.execute('''
CREATE TABLE IF NOT EXISTS myusertable (
  username TEXT PRIMARY KEY, 
  hash TEXT NOT NULL
)
''')

myMap = {}

def createAccount(userName, password):
	hashedpwd = str(hash(password))
	dict2 = {userName: hashedpwd}
	myMap.update(dict2)
	cur.execute("INSERT INTO myusertable (username, hash) VALUES (?, ?)", (userName, hashedpwd))
	con.commit()
	print('Password is ' + str(hashedpwd))

def verifyAccount(userName, password):
	cur.execute("SELECT hash FROM myusertable WHERE username = ?", (userName,))
	rows = cur.fetchall()
	#toCheck = myMap.get(userName)
	if len(rows) == 0:
		print('Username not found')
		return False
	first_row = rows[0]
	hashInDB = first_row[0]
	if hashInDB == str(hash(password)):
		return True
	else:
		print('Password not found')
		return False

print('Input username and password: ')

for i in range(1):
	userName = input('Input username: ')
	password = input('Input password: ')
	createAccount(userName, password)

print(myMap)

continueVerify = 'Y'

while continueVerify == 'Y':

	checkUsername = input('Please input username to verify account: ')
	checkPassword = input('Please input password to verify account: ')

	accountExists = verifyAccount(checkUsername, checkPassword)
	if accountExists == True:
		print('Account verified')
	else:
		print('Account not verified')

	continueVerify = input('Do you want to continue? Y or N: ')