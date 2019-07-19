import sys
import socket
import pickle
import os
import time

MAX_COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
MAX_ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
DIRECTIONS = ['up', 'down', 'left', 'right']
HOST = '127.0.0.1'
PORT = 11223
BOARD = {}
SHIPS = {
	'Carrier' :  {
		'size': 5
	},
	'Battleship' : {
		'size': 4
	},
	'Destroyer' : {
		'size': 3
	},
	'Patrol-Boat': {
		'size': 2
	}
}
OPPONENT = None
OPPONENT_PORT = None
PLAYER_NAME = None
OPPONENT_NAME = None

#################################################################################
################################ GAME SETUP #####################################
#################################################################################

# setup up game, whether joining game or creating new one
def setup_handler():
	os.system('clear')

	# see if player is joining a game or starting a new one
	print("Will you be starting the game or joining someone else's game? (start/join)")
	response = sys.stdin.readline().strip('\n')

	# wait until user enters a valid response
	while response != 'start' and response != 'join':
		print("Sorry, you must specify either 'start' or 'join' to continue")
		response = sys.stdin.readline().strip('\n')

	os.system('clear')

	# have player enter their name
	print("Please enter your name:")
	global PLAYER_NAME
	PLAYER_NAME = sys.stdin.readline().strip('\n')

	os.system('clear')

	# if starting a new game
	if response == 'start':
		print("How many rows/columns would you like on the board? (10 is recommended, 20 is max, 7 is min)")
		num = None
		while True:
			try:
				num = int(sys.stdin.readline().strip('\n'))
				break
			except ValueError:
				print("Sorry, you must input a number like \"10\"")
				pass

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
		global OPPONENT
		OPPONENT = sys.stdin.readline().strip('\n')

		if OPPONENT == '127.0.0.1':
			print("playing locally")
		else:
			print("playing nonlocally")

		print("Please input your opponents port number. If then did not enter one, enter \"Default\"")
		global OPPONENT_PORT
		OPPONENT_PORT = sys.stdin.readline().strip('\n')
		if OPPONENT_PORT == 'Default':
			OPPONENT_PORT = 11223

		print("opponent at {} port {}".format(OPPONENT, OPPONENT_PORT))


	os.system('clear')
	return

#################################################################################
############################## Initialization ###################################
#################################################################################

# initialize all places on board as empty
def initialize_board():
	for row in ROWS:
		BOARD[row] = {}
		for col in COLUMNS:
			BOARD[row][col] = '   '

#################################################################################
############################## SHIP PLACEMENT ###################################
#################################################################################

# allow user to place their ships on the board
def place_ships():
	available_ships = list(SHIPS.keys())
	os.system('clear')
	message = ''

	# allow player to place ships until they have run out
	while len(available_ships) != 0:
		print_current_state(available_ships)

		if message != '':
			print("ERROR: {}".format(message), end='\n\n')
		
		print("Input your placement: ", end='')
		sys.stdout.flush()
		message = ''
		location_array = sys.stdin.readline().strip('\n').split(' ')

		if len(location_array) == 1 and location_array[0] == 'clear':
			initialize_board()
			available_ships = list(SHIPS.keys())
			os.system('clear')
		elif len(location_array) != 3:
			os.system('clear')
			message = "Sorry, you must either pass in three values or \"clear\""
		elif location_array[0] not in available_ships:
			os.system('clear')
			message = "Sorry, {} is not a valid ship".format(location_array[0])
		elif not valid_location(location_array[1]):
			os.system('clear')
			message = "Sorry, {} is not a valid location".format(location_array[1])
		elif location_array[2] not in DIRECTIONS:
			os.system('clear')
			message = "Sorry, {} is not a valid direction".format(location_array[2])
		elif not ship_fits_on_board(location_array[0], location_array[1], location_array[2]):
			os.system('clear')
			message = "{} does not fit at {} with direction {}".format(location_array[0], location_array[1], location_array[2])
		else: 
			place_ship(location_array[0], location_array[1], location_array[2])
			available_ships.remove(location_array[0])
			os.system('clear')

# print for ship placement
def print_current_state(available_ships):
	# print curretn board
	print_board()

	# print instructions
	print('', end='\n')
	print("Choose a ship placement using the format SHIP ROW+COL DIRECTION")
	print("Example: \"Destroyer 2A down\"")
	print('', end='\n')

	# print list of ships player can still use
	print("Available ships:")
	for ship in available_ships:
		print("\t{} (size {})".format(ship, SHIPS[ship]['size']))
	print('', end='\n')

	# print directions ship can point
	print("Possible directions:")
	for direction in DIRECTIONS:
		print("\t{}".format(direction))
	print('', end='\n')

	# print clear option to restart
	print("Enter \"clear\" to clear your current placements", end='\n\n')

# ensure location string is valid position on board
def valid_location(location_string):
	index = len(location_string) - 1

	if location_string[index] not in COLUMNS:
		return False

	if location_string[:index] not in ROWS:
		return False

	return True

# ensure valid placement of ship
def ship_fits_on_board(ship_type, location_string, direction):
	index = len(location_string) - 1
	start_row = int(location_string[:index])
	start_col = COLUMNS.index(location_string[index])
	diff = SHIPS[ship_type]['size'] - 1

	if direction == 'down' or direction == 'up':
		end_row = None
		if direction == 'down':
			end_row = start_row + diff
		else:
			end_row = start_row - diff
		if end_row > MAX_LENGTH or end_row < 1:
			print("return 1")
			return False

		for i in range(diff + 1):
			if direction == 'down':
				if BOARD[ROWS[start_row - 1 + i]][COLUMNS[start_col]] != '   ':
					return False
			else:
				if BOARD[ROWS[start_row - 1 - i]][COLUMNS[start_col]] != '   ':
					return False

	# direction == 'left' or 'right'
	else: 
		end_col = None
		if direction == 'right':
			end_col = start_col + diff
		else:
			end_col = start_col - diff
		if end_col >= MAX_LENGTH or end_col < 0:
			return False

		for i in range(diff + 1):
			if direction == 'right':
				if BOARD[ROWS[start_row - 1]][COLUMNS[start_col + i]] != '   ':
					return False
			else:
				if BOARD[ROWS[start_row - 1]][COLUMNS[start_col - i]] != '   ':
					return False


	return True

# once verified as a valid placement, update the board
def place_ship(ship_type, location_string, direction):
	index = len(location_string) - 1
	row = ROWS.index(location_string[:index])
	col = COLUMNS.index(location_string[index])
	size = SHIPS[ship_type]['size']

	for i in range(size):
		if direction == 'down':
			if i == 0:
				BOARD[ROWS[row + i]][COLUMNS[col]] = ' Λ '
			elif i == size - 1:
				BOARD[ROWS[row + i]][COLUMNS[col]] = ' V '
			else:
				BOARD[ROWS[row + i]][COLUMNS[col]] = ' ‖ '
		elif direction == 'up':
			if i == 0:
				BOARD[ROWS[row - i]][COLUMNS[col]] = ' V '
			elif i == size - 1:
				BOARD[ROWS[row - i]][COLUMNS[col]] = ' Λ '
			else:
				BOARD[ROWS[row - i]][COLUMNS[col]] = ' ‖ '
		elif direction == 'right':
			if i == 0:
				BOARD[ROWS[row]][COLUMNS[col + i]] = ' <='
			elif i == size - 1:
				BOARD[ROWS[row]][COLUMNS[col + i]] = '=> '
			else:
				BOARD[ROWS[row]][COLUMNS[col + i]] = '==='
		else:
			if i == 0:
				BOARD[ROWS[row]][COLUMNS[col - i]] = '=> '
			elif i == size - 1:
				BOARD[ROWS[row]][COLUMNS[col - i]] = ' <='
			else:
				BOARD[ROWS[row]][COLUMNS[col - i]] = '==='

#################################################################################
############################## PRINTING BOARD ###################################
#################################################################################

# print out the current state of the board
def print_board():
	print('   ', end='|')
	for column in COLUMNS:
		print(" {} ".format(column), end='|')
	print_sep()
	for row in ROWS:
		if len(row) == 1:
			print(' {} |'.format(row), end='')
		else:
			print('{} |'.format(row), end='')
		for col in COLUMNS:
			if COLUMNS.index(col) == MAX_LENGTH - 1:
				print('{}|'.format(BOARD[row][col]), end='')
			else:
				print('{}:'.format(BOARD[row][col]), end='')
		print_sep()

# helper for print_board()
def print_sep():
	print('\n----', end='')
	for i in COLUMNS:
		print(' - -', end='')
	print('', end='\n')


#################################################################################
################################### MAIN ########################################
#################################################################################

def main():
	# setup game
	setup_handler()

	# set up socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	global OPPONENT_NAME

	# connect or wait for opponent to connect
	if OPPONENT == None:
		s.bind((HOST, PORT))
		print("binding to {} at port {}".format(HOST, PORT))
		s.listen()
		conn, addr = s.accept()
		print('Connected by', addr)
		OPPONENT_NAME = conn.recv(1024).decode()
		print("playing against {}".format(OPPONENT_NAME))
		hello_msg = PLAYER_NAME.encode()
		conn.sendall(hello_msg)
		conn.sendall("12".encode())
		time.sleep(10)

	else:
		print("Trying to connect to {} at port {}".format(OPPONENT, OPPONENT_PORT))
		sys.stdout.flush()
		s.connect((OPPONENT, OPPONENT_PORT))
		hello_msg = PLAYER_NAME.encode()
		s.sendall(hello_msg)
		OPPONENT_NAME = s.recv(1024).decode()
		print("playing against {}".format(OPPONENT_NAME))
		global MAX_LENGTH
		MAX_LENGTH = int(s.recv(1024).decode())
		print("max length is {}".format(MAX_LENGTH))
		time.sleep(10)

	# allow player to place thier ships
	initialize_board()
	place_ships()

	








	# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	#     s.bind((HOST, PORT))
	#     s.listen()
	#     conn, addr = s.accept()
	#     with conn:
	#         print('Connected by', addr)
	#         while True:
	#             data = conn.recv(1024)
	#             if not data:
	#                 break
	#             conn.sendall(data)

if __name__ == '__main__':
	main()