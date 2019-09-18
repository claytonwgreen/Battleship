import sys
import socket
import pickle
import os
import time
import atexit


#################################################################################
############################## GLOBAL VARIABLES #################################
#################################################################################

MAX_COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
MAX_ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
MAX_LENGTH = None
DIRECTIONS = ['up', 'down', 'left', 'right']
HOST = '127.0.0.1'
PORT = 11223
STARTING = False
BOARD = {}
SHIPS = {
	# 'Carrier' :  {
	# 	'size': 5,
	# 	'location': []
	# },
	# 'Battleship' : {
	# 	'size': 4,
	# 	'location': []
	# },
	# 'Destroyer' : {
	# 	'size': 3,
	# 	'location': []
	# },
	'Patrol-Boat': {
		'size': 2,
		'location': []
	}
	#########################################################
	#### uncomment any of the below ships if you want #######
	#### to be able to place more ships on the board  #######
	#########################################################
	# 
	# ,'Carrier2' :  {
	# 	'size': 5,
	# 	'location': []
	# }
	# ,'Battleship2' : {
	# 	'size': 4,
	# 	'location': []
	# }
	# ,'Destroyer2' : {
	# 	'size': 3,
	# 	'location': []
	# }
	# ,'Patrol-Boat2': {
	# 	'size': 2,
	# 	'location': []
	# }
	# 
	# ,'Carrier3' :  {
	# 	'size': 5,
	# 	'location': []
	# }
	# ,'Battleship3' : {
	# 	'size': 4,
	# 	'location': []
	# }
	# ,'Destroyer3' : {
	# 	'size': 3,
	# 	'location': []
	# }
	# ,'Patrol-Boat3': {
	# 	'size': 2,
	# 	'location': []
	# }

}
OPPONENT_BOARD = None
TARGETTED_BOARD = {}
OPPONENT_SHIPS = {}
OPPONENT_IP = None
OPPONENT_PORT = 11223
PLAYER_NAME = None
OPPONENT_NAME = None

#################################################################################
################################ GAME SETUP #####################################
#################################################################################

# setup up game, whether joining game or creating new one
def setup_handler():
	os.system('clear')

	# see if player is joining a game or starting a new one
	print("Will you be starting the game or joining someone else's game? \n\n(start/join): ", end='')
	sys.stdout.flush()
	response = sys.stdin.readline().strip('\n').lower()

	# wait until user enters a valid response
	while response != 'start' and response != 'join':
		print("Sorry, you must specify either 'start' or 'join' to continue\n\n(start/join): ", end='')
		response = sys.stdin.readline().strip('\n').lower()

	os.system('clear')

	# have player enter their name
	print("Please enter your name\n\nPlayer name: ", end='')
	global PLAYER_NAME
	PLAYER_NAME = sys.stdin.readline().strip('\n')

	os.system('clear')

	# if starting a new game
	if response == 'start':
		starting_setup()

	# if joining a game
	else:
		joining_setup()

	os.system('clear')

	return

# handler if player is starting game
def starting_setup():
	global STARTING
	STARTING = True
	print("How many rows/columns would you like on the board? (10 is recommended, 20 is max, 7 is min)\n\nRows/Columns: ", end='')
	num = None
	while True:
		try:
			num = int(sys.stdin.readline().strip('\n'))
			break
		except ValueError:
			print("Sorry, you must input a number, such as \"10\"\n\nRows/Columns: ", end='')
			pass

	# wait until user enters valid number
	while num > 20 or num < 7:
		print("Sorry, your selection must be between 7 and 20\n\nRows/Columns: ", end='')
		num = int(sys.stdin.readline().strip('\n'))

	global MAX_LENGTH
	MAX_LENGTH = num

# handler if player is joining a game
def joining_setup():
	print("Please input the IP address of your opponent, if playing on the same computer just hit \"Enter\".\nIf they do not know their IP, \
they can simply type \"my ip\" into a browser to find it.\n\nIP address: ", end='')
	global OPPONENT_IP
	OPPONENT_IP = sys.stdin.readline().strip('\n')
	if OPPONENT_IP == '':
		OPPONENT_IP = '127.0.0.1'

# #################################################################################
# ############################## Initialization ###################################
# #################################################################################

# initialize all places on board as empty
def initialize_board():
	# create arrays for rows/cols based on inputted value
	global COLUMNS 
	global ROWS
	COLUMNS = MAX_COLUMNS[:MAX_LENGTH]
	ROWS = MAX_ROWS[:MAX_LENGTH]
	clear_main_board()
	clear_opp_board()

# set all entries on board to empty
def clear_main_board():
	for row in ROWS:
		BOARD[row] = {}
		for col in COLUMNS:
			BOARD[row][col] = '   '
	for ship in SHIPS:
		SHIPS[ship]['location'] = []

# set all entries on target board to empty
def clear_opp_board():
	for row in ROWS:
		TARGETTED_BOARD[row] = {}
		for col in COLUMNS:
			TARGETTED_BOARD[row][col] = '   '

#################################################################################
############################## SHIP PLACEMENT ###################################
#################################################################################

# allow user to place their ships on the board
def place_ships():
	available_ships = list(SHIPS.keys())
	os.system('clear')
	message = ''

	# allow player to place ships until they have placed all 
	while len(available_ships) != 0:
		# print current state of the board
		print_current_state(available_ships)

		# print message from previous input, if any 
		if message != '':
			print("ERROR: {}".format(message), end='\n\n')
		print("Input your placement: ", end='')
		sys.stdout.flush()
		message = ''
		location_array = sys.stdin.readline().strip('\n').split(' ')

		# reset board
		if len(location_array) == 1 and location_array[0] == 'clear':
			clear_main_board()
			available_ships = list(SHIPS.keys())
			os.system('clear')
		# invalid input sequence
		elif len(location_array) != 3:
			os.system('clear')
			message = "Sorry, you must either pass in three values or \"clear\""
		# invalid ship name
		elif location_array[0] not in available_ships:
			os.system('clear')
			message = "Sorry, {} is not a valid ship".format(location_array[0])
		# invalid baord location
		elif not valid_location(location_array[1]):
			os.system('clear')
			message = "Sorry, {} is not a valid location".format(location_array[1])
		# invalid direction
		elif location_array[2] not in DIRECTIONS:
			os.system('clear')
			message = "Sorry, {} is not a valid direction".format(location_array[2])
		# ship does not fit
		elif not ship_fits_on_board(location_array[0], location_array[1], location_array[2]):
			os.system('clear')
			message = "{} does not fit at {} with direction {}".format(location_array[0], location_array[1], location_array[2])
		# valid input, insert ship
		else: 
			place_ship(location_array[0], location_array[1], location_array[2])
			available_ships.remove(location_array[0])
			os.system('clear')

	print_board()

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

	# ensure valid column input
	if location_string[index] not in COLUMNS:
		return False

	# ensure valid row input
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

		# check if rest of ship will be off the board
		if direction == 'down':
			end_row = start_row + diff
		else:
			end_row = start_row - diff
		if end_row > MAX_LENGTH or end_row < 1:
			print("return 1")
			return False

		# check if there is a ship already in any of the positions
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

		# check if rest of ship will be off the board
		if direction == 'right':
			end_col = start_col + diff
		else:
			end_col = start_col - diff
		if end_col >= MAX_LENGTH or end_col < 0:
			return False

		# check if there is a ship already in any of the positions
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
				save_location(ROWS[row + i] + COLUMNS[col], ship_type)
			elif i == size - 1:
				BOARD[ROWS[row + i]][COLUMNS[col]] = ' V '
				save_location(ROWS[row + i] + COLUMNS[col], ship_type)
			else:
				BOARD[ROWS[row + i]][COLUMNS[col]] = ' ‖ '
				save_location(ROWS[row + i] + COLUMNS[col], ship_type)
		elif direction == 'up':
			if i == 0:
				BOARD[ROWS[row - i]][COLUMNS[col]] = ' V '
				save_location(ROWS[row - i] + COLUMNS[col], ship_type)
			elif i == size - 1:
				BOARD[ROWS[row - i]][COLUMNS[col]] = ' Λ '
				save_location(ROWS[row - i] + COLUMNS[col], ship_type)
			else:
				BOARD[ROWS[row - i]][COLUMNS[col]] = ' ‖ '
				save_location(ROWS[row - i] + COLUMNS[col], ship_type)
		elif direction == 'right':
			if i == 0:
				BOARD[ROWS[row]][COLUMNS[col + i]] = ' <='
				save_location(ROWS[row] + COLUMNS[col + i], ship_type)
			elif i == size - 1:
				BOARD[ROWS[row]][COLUMNS[col + i]] = '=> '
				save_location(ROWS[row] + COLUMNS[col + i], ship_type)
			else:
				BOARD[ROWS[row]][COLUMNS[col + i]] = '==='
				save_location(ROWS[row] + COLUMNS[col + i], ship_type)
		else:
			if i == 0:
				BOARD[ROWS[row]][COLUMNS[col - i]] = '=> '
				save_location(ROWS[row] + COLUMNS[col - i], ship_type)
			elif i == size - 1:
				BOARD[ROWS[row]][COLUMNS[col - i]] = ' <='
				save_location(ROWS[row] + COLUMNS[col - i], ship_type)
			else:
				BOARD[ROWS[row]][COLUMNS[col - i]] = '==='
				save_location(ROWS[row] + COLUMNS[col - i], ship_type)

# save location to ships
def save_location(location_string, ship_type):
	SHIPS[ship_type]['location'].append(location_string)

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

# print out the current state of the board
def print_opp_board():
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
				print('{}|'.format(OPPONENT_BOARD[row][col]), end='')
			else:
				print('{}:'.format(OPPONENT_BOARD[row][col]), end='')
		print_sep()

def print_targ_board():
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
				print('{}|'.format(TARGETTED_BOARD[row][col]), end='')
			else:
				print('{}:'.format(TARGETTED_BOARD[row][col]), end='')
		print_sep()

# helper for print_board()
def print_sep():
	print('\n----', end='')
	for i in COLUMNS:
		print(' - -', end='')
	print('', end='\n')

# print target and own board during play
def print_both_boards():
	# print names
	for i in range(MAX_LENGTH // 2 - 1):
		print('    ', end='')
	print("Your board", end='')
	for i in range(MAX_LENGTH // 2 - 1):
		print('    ', end='')
	print('\t||\t', end='')
	for i in range(MAX_LENGTH // 2 - 1):
		print('    ', end='')
	print("{}'s board".format(OPPONENT_NAME), end='')
	for i in range(MAX_LENGTH // 2 - 1):
		print('    ', end='')
	print('', end='\n')
	for i in range(MAX_LENGTH):
		print('    ', end='')
	print("\t||\t", end='')

	# print boards
	print('\n   ', end='|')
	for column in COLUMNS:
		print(" {} ".format(column), end='|')
	print('\t||\t   ', end='|')
	for column in COLUMNS:
		print(" {} ".format(column), end='|')
	print_both_sep()
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
		print('\t||\t', end='')
		if len(row) == 1:
			print(' {} |'.format(row), end='')
		else:
			print('{} |'.format(row), end='')
		for col in COLUMNS:
			if COLUMNS.index(col) == MAX_LENGTH - 1:
				print('{}|'.format(TARGETTED_BOARD[row][col]), end='')
			else:
				print('{}:'.format(TARGETTED_BOARD[row][col]), end='')
		print_both_sep()

# helper for printing both boards
def print_both_sep():
	print('\n----', end='')
	for i in COLUMNS:
		print(' - -', end='')
	print('\t||\t', end='')
	print('----', end='')
	for i in COLUMNS:
		print(' - -', end='')
	print('', end='\n')

# helper for printing when there is a hit
def print_hit():
	print(" __     __   ________   ________    _   _   _ ")
	print("|  |   |  | |__    __| |__    __|  | | | | | |")
	print("|  |___|  |    |  |       |  |     | | | | | |")
	print("|   ___   |    |  |       |  |     |_| |_| |_|")
	print("|  |   |  |  __|  |__     |  |      _   _   _ ")
	print("|__|   |__| |________|    |__|     (_) (_) (_)")

# helper for printing when there is a miss
def print_miss():
	print("                                        _")
	print(" __  __   ___   ____    ____       _   / /")
	print("|  \\/  | |_ _| / ___|  / ___|     (_) | | ")
	print("| |\\/| |  | |  \\___ \\  \\___ \\      _  | | ")
	print("| |  | |  | |   ___) |  ___) |    (_) | | ")
	print("|_|  |_| |___| |____/  |____/          \\_\\")

# helper for prining when player wins
def print_win():
	print("__   __   ___    _   _    __        __   ___    _   _   _   _   _ ")
	print("\\ \\ / /  / _ \\  | | | |   \\ \\      / /  / _ \\  | \\ | | | | | | | |")
	print(" \\ V /  | | | | | | | |    \\ \\ /\\ / /  | | | | |  \\| | | | | | | |")
	print("  | |   | |_| | | |_| |     \\ V  V /   | |_| | | |\\  | |_| |_| |_|")
	print("  |_|    \\___/   \\___/       \\_/\\_/     \\___/  |_| \\_| (_) (_) (_)")

def print_lost():
	print(" __   __   ___    _   _     _        ___    ____    _____          __")
	print(" \\ \\ / /  / _ \\  | | | |   | |      / _ \\  / ___|  |_   _|    _   / /")
	print("  \\ V /  | | | | | | | |   | |     | | | | \\___ \\    | |     (_) | | ")
	print("   | |   | |_| | | |_| |   | |___  | |_| |  ___) |   | |      _  | | ")
	print("   |_|    \\___/   \\___/    |_____|  \\___/  |____/    |_|     (_) | | ")
	print("                                                                  \\_\\")
                                                                   
#################################################################################
################################## MOVES ########################################
#################################################################################

# send a move
def play_game(connection, my_turn):

	if my_turn:
		print("Please input your attack location\nAn example would be \"7B\"\n\nLocation: ", end='')
		Input = sys.stdin.readline().strip()
		if Input == "IAMACHEATER":
			os.system('clear')
			print("{}'s board, you really shouldn't be cheating ;)\n".format(OPPONENT_NAME))
			print_opp_board()
			time.sleep(5)
			os.system('clear')
			print_both_boards()
			return play_game(connection, my_turn)

		valid_input = valid_location(Input)

		while not valid_input:
			print("Sorry, \"{}\" is not a valid location on the board\n\nLocation: ".format(Input), end='')
			Input = sys.stdin.readline().strip()
			valid_input = valid_location(Input)

		index = len(Input) - 1
		row = Input[:index]
		col = Input[index]
		hit = False
		sunk = False
		game_over = False
		if OPPONENT_BOARD[row][col] != '   ':
			hit = True
			TARGETTED_BOARD[row][col] = ' X '
			for ship in SHIPS:
				print(ship)
				print(type(OPPONENT_SHIPS))
				print(type(OPPONENT_SHIPS[ship]))
				if (row + col) in OPPONENT_SHIPS[ship]['location']:
					OPPONENT_SHIPS[ship]['location'].remove(row + col)
					if len(OPPONENT_SHIPS[ship]['location']) == 0:
						sunk = ship
						game_over = True
						for ship in SHIPS:
							if len(OPPONENT_SHIPS[ship]['location']) != 0:
								game_over = False
		else:
			TARGETTED_BOARD[row][col] = ' o '

		connection.sendall(Input.encode())

		os.system('clear')

		print_both_boards()

		if hit:
			print_hit()
			if sunk:
				print("\nYou sunk {}'s {}!!!".format(OPPONENT_NAME, sunk))
				if game_over:
					print_win()
					time.sleep(3)
					return replay(connection, my_turn)
		else:
			print_miss()

		print("\nWaiting for {}'s move".format(OPPONENT_NAME))

		play_game(connection, my_turn=False)


	else:
		opponent_move = connection.recv(1024).decode()
		index = len(opponent_move) - 1
		row = opponent_move[:index]
		col = opponent_move[index]
		hit = False
		sunk = False
		game_over = False
		if BOARD[row][col] != '   ':
			hit = True
			BOARD[row][col] = ' X '
			for ship in SHIPS:
				if (row + col) in SHIPS[ship]['location']:
					SHIPS[ship]['location'].remove(row + col)
					if len(SHIPS[ship]['location']) == 0:
						sunk = ship
						game_over = True
						for ship in SHIPS:
							if len(SHIPS[ship]['location']) != 0:
								game_over = False


		os.system('clear')

		print_both_boards()

		if hit:
			print("\n{} hit your ship at row {} col {}\n".format(OPPONENT_NAME, row, col))
			if sunk:
				print("{} sunk your {}\n".format(OPPONENT_NAME, sunk))
				if game_over:
					print_lost()
					time.sleep(3)
					return replay(connection, my_turn)

		else:
			print("\n{} missed at at row {} col {}\n".format(OPPONENT_NAME, row, col))

		play_game(connection, my_turn=True)

def replay(conn, my_turn):
	print("\nWould you like to play again? \n(yes/no):", end='')
	Input = sys.stdin.readline().strip().lower()
	while Input != 'y' and Input != 'n' and Input != 'yes' and Input != 'no':
		os.system('clear')
		print("Sorry, you must say yes or no")
		Input = sys.stdin.readline().strip().lower()

	if Input == 'y' or Input == 'yes':
		global OPPONENT_BOARD
		global OPPONENT_SHIPS

		# tell other player you want to replay
		conn.sendall("yes".encode())
		os.system('clear')
		print("Waitng for {} to respond\n".format(OPPONENT_NAME))

		# get opponents response
		resp = conn.recv(32).decode()

		if resp == "no":
			os.system('clear')
			print("Sorry, {} quit\n\nGoodbye".format(OPPONENT_NAME))
			time.sleep(3)
			return

		# place ships on board
		initialize_board()
		place_ships()

		# send board to opponent once finished
		conn.sendall(pickle.dumps(BOARD, -1))

		# load opponents board
		OPPONENT_BOARD = pickle.loads(conn.recv(4096))

		# send ships to opponent
		conn.sendall(pickle.dumps(SHIPS, -1))

		# load opponents ships
		OPPONENT_SHIPS = pickle.loads(conn.recv(4096))

		os.system('clear')
		print_both_boards()

		play_game(connection=conn, my_turn=my_turn)

	else:
		conn.sendall("no".encode())
		print("\nGoodbye")
		return



#################################################################################
################################# SHUTDOWN ######################################
#################################################################################
def shutdown(socket):
	socket.close()

#################################################################################
################################### MAIN ########################################
#################################################################################

def main():
	# setup game
	setup_handler()

	# set up socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	global OPPONENT_NAME
	global MAX_LENGTH
	global OPPONENT_BOARD
	global OPPONENT_SHIPS

	# close socket at exit
	atexit.register(shutdown, socket=s)

	# if this player started game
	if STARTING == True:
		# create socket and wait for connection
		s.bind((HOST, PORT))
		s.listen()
		print("Waiting for opponent to connect")
		conn, addr = s.accept()

		# receive opponents name once connected
		OPPONENT_NAME = conn.recv(1024).decode().upper()
		os.system('clear')
		print("Connected to {}!\n".format(OPPONENT_NAME))

		# send name and board length to opponent
		hello_msg = (PLAYER_NAME + ':::' + str(MAX_LENGTH))
		hello_msg = hello_msg.encode()
		conn.sendall(hello_msg)
		time.sleep(1)
		print("You will now place your ships on the board")
		time.sleep(2)

		# place ships on board
		initialize_board()
		place_ships()

		# send board to opponent once finished
		conn.sendall(pickle.dumps(BOARD, -1))

		# load opponents board
		OPPONENT_BOARD = pickle.loads(conn.recv(4096))

		# send ships to opponent
		conn.sendall(pickle.dumps(SHIPS, -1))

		# load opponents ships
		OPPONENT_SHIPS = pickle.loads(conn.recv(4096))

		os.system('clear')
		print_both_boards()

		play_game(connection=conn, my_turn=True)



	# if this player is joining a game
	else:
		# try to connect to game
		try:
			s.connect((OPPONENT_IP, OPPONENT_PORT))
		except:
			print("Sorry, couldn't connect to {}, please restart".format(OPPONENT_IP))
			return

		# send player name
		hello_msg = PLAYER_NAME.encode()
		s.sendall(hello_msg)

		# receive opponent name and size of board
		received = s.recv(1024).decode()
		received = received.split(':::')
		OPPONENT_NAME = received[0].upper()
		MAX_LENGTH = int(received[1])
		print("Connected to {}!\n".format(OPPONENT_NAME))
		time.sleep(1)
		print("You will now place your ships on the board")
		time.sleep(2)

		# place ships on board
		initialize_board()
		place_ships()

		# send board to opponent once finished
		s.sendall(pickle.dumps(BOARD, -1))

		# load opponents board
		OPPONENT_BOARD = pickle.loads(s.recv(4096))

		# send ships to opponent
		s.sendall(pickle.dumps(SHIPS, -1))

		# load opponents ships
		OPPONENT_SHIPS = pickle.loads(s.recv(4096))

		os.system('clear')
		print_both_boards()
		print("\nWaiting for {}'s move".format(OPPONENT_NAME))

		play_game(connection=s, my_turn=False)

if __name__ == '__main__':
	main()