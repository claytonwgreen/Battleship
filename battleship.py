import sys
import socket

MAX_COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
MAX_ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
HOST = '127.0.0.1'
PORT = 11223

def setup_handler():
	print("Will you be starting the game or joining someone else's game? (start/join)")
	response = sys.stdin.readline().strip('\n')
	if response == 'start':
		print("Game Setup:")
		print("How many rows/columns would you like on the board? (10 is reccomended, 20 is max)")
		num = int(sys.stdin.readline().strip('\n'))
		global COLUMNS 
		global ROWS
		COLUMNS = MAX_COLUMNS[:num]
		ROWS = MAX_ROWS[:num]
		print(COLUMNS)
		print(ROWS)

	else:
		print("Please input the IP address of your opponent, then hit \"Enter\" (127.0.0.1 if playing on the same computer):")
		OPPONENT = sys.stdin.readline().strip('\n')
		print("opponent at {}".format(OPPONENT))

		if OPPONENT == '127.0.0.1':
			print("playing locally")
		else:
			print("playing nonlocally")

def main():
	setup_handler()







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