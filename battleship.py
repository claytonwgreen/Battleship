import sys
import socket
import os

MAX_COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
MAX_ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
HOST = '127.0.0.1'
PORT = 11223
BOARD = {}
SHIP_SIZE = {
	'Carrier' :  5,
	'Battleship' : 4,
	'Destroyer' : 3,
	'Patrol Boat': 2
}
SHIPS = {}

# setup up game, whether joining game or creating new one
def setup_handler():
	# see if player is joining a game or starting a new one
	print("Will you be starting the game or joining someone else's game? (start/join)")
	response = sys.stdin.readline().strip('\n')

	# wait until user enters a valid response
	while response != 'start' and response != 'join':
		print("Sorry, you must specify either 'start' or 'join' to continue")
		response = sys.stdin.readline().strip('\n')

	os.system('clear')
	# if starting a new game
	if response == 'start':
		print("How many rows/columns would you like on the board? (10 is recommended, 20 is max, 7 is min)")
		num = int(sys.stdin.readline().strip('\n'))

		# wait until user enters valid number
		while num > 20 or num < 7:
			print("Sorry, your selection must be between 7 and 20")
			num = int(sys.stdin.readline().strip('\n'))

		# create arrays for rows/cols based on inputted value
		global COLUMNS 
		global ROWS
		global MAX_LENGTH
		COLUMNS = MAX_COLUMNS[:num]
		ROWS = MAX_ROWS[:num]
		MAX_LENGTH = num

	# if joining a game
	else:
		print("Please input the IP address of your opponent, then hit \"Enter\" (127.0.0.1 if playing on the same computer):")
		OPPONENT = sys.stdin.readline().strip('\n')
		print("opponent at {}".format(OPPONENT))

		if OPPONENT == '127.0.0.1':
			print("playing locally")
		else:
			print("playing nonlocally")

	os.system('clear')
	return

# initialize all places on board as empty
def initialize_board():
	for row in ROWS:
		BOARD[row] = {}
		for col in COLUMNS:
			BOARD[row][col] = ' '


# allow user to place their ships on the board
def place_ships():
	print_board()
	print("Choose where to place your first ship by typing in the boat name, location, and direction. \nAn example is \"Destroyer 2A down\"\n")
	print("Ships:\n\tCarrier: <===> \n\tBattleship: <==> \n\tDestroyer: <=> \n\tPatrol Boat: <>\n")
	location = sys.stdin.readline().strip('\n').split(' ')
	print(location)


# print out the current state of the board
def print_board():
	print('   ', end='| ')
	for column in COLUMNS:
		print("{}".format(column), end=' | ')
	print_sep()
	for row in ROWS:
		if len(row) == 1:
			print(' {} |'.format(row), end='')
		else:
			print('{} |'.format(row), end='')
		for col in COLUMNS:
			print(' {} |'.format(BOARD[row][col]), end='')
		print_sep()

# helper for print_board()
def print_sep():
	print('\n----', end='')
	for i in COLUMNS:
		print('----', end='')
	print('', end='\n')


def main():
	os.system('clear')
	setup_handler()
	initialize_board()
	place_ships()
	print_board()







	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	    s.bind((HOST, PORT))
	    s.listen()
	    conn, addr = s.accept()
	    with conn:
	        print('Connected by', addr)
	        while True:
	            data = conn.recv(1024)
	            if not data:
	                break
	            conn.sendall(data)

if __name__ == '__main__':
	main()