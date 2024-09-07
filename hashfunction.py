myMap = {}

def createAccount(userName, password):
	hashedpwd = hash(password)
	dict2 = {userName: hashedpwd}
	myMap.update(dict2)
	print('Password is ' + str(hashedpwd))

def verifyAccount(userName, password):
	toCheck = myMap.get(userName)
	if toCheck == None:
		print('Username not found')
		return False
	if toCheck == hash(password):
		return True
	print('Password not found')
	return False

print('Input username and password three times: ')

for i in range(3):
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