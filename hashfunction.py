import hashlib

#def createAccount(userName, password):
   #print('Hello, hello')
    #hashedpwd = hash(password)
    #print(hashedpwd)
    #add(userName, password)
    
#createAccount('Sonia', '123')

#userName = input('Input username: ')
#print('Username is ' + userName)
#password = input('Input password: ')


def createAccount(userName, password):
	userName = input('Input username: ')
	print('Username is ' + userName)
	password = input('Input password: ')
	hashedpwd = hash(password)
	input('Input password' + hashedpwd)
	createAccount.add(userName, hashedpwd)
	print('Password is ' + hashedpwd)

def verifyAccount(userName, password):
	account = createAccount.get(userName)
	if account == None:
		return False
	hashedpwd = hash(password)
	if account.value == hashedpwd:
		return True
	return False


