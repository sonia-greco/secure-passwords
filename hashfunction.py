import sqlite3

# TO DO
# Remove hashmap in memory because it is not used anymore (we are using a database) 
# Build a function to change password, which first verifies if the old password is correct and, if correct, it actually change it to the new one. We reuse the existing function "verifyAccount" to check if the old password is correct.
# Use the new changePassword function in the main program to let the user actually update a password

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

#myMap = {}

def createAccount(userName, password):
	hashedpwd = str(hash(password))
#	dict2 = {userName: hashedpwd}
#	myMap.update(dict2)
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

def changePassword(userName, password, newPassword):
	accountExists = verifyAccount(userName, password)
	if accountExists:
		hashedpwd = str(hash(newPassword))
		cur.execute("UPDATE myusertable SET hash = ? WHERE userName = ?", (hashedpwd, userName))
		con.commit()
		return True
	else:
		return False

print('Please create an account')

for i in range(1):
	userName = input('Input username: ')
	password = input('Input password: ')
	createAccount(userName, password)

#print(myMap)

continueVerify = 'V'

while continueVerify == 'V':

	print('Please verify account:')

	checkUsername = input('Input USERNAME: ')
	checkPassword = input('Input PASSWORD: ')

	accountExists = verifyAccount(checkUsername, checkPassword)
	if accountExists == True:
		print('Account verified')
	else:
		print('Account not verified')

	continueVerify = input('Do you want to continue to verify or create a new password? \nV for verify or P password: ')

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

	createNewPwd = input('Do you want to change another password? \nP for yes and N for no: ')



