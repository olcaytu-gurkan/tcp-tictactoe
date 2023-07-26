import socket
import sys

def print_board(board):
    board_str = ''
    for row in board:
        board_str += '|'.join(row) + '\n'
    return board_str

def main():
    # Port number is required.
    if (len(sys.argv) < 2):
        print("Error! You should provide a port number.")
        exit()

    HOST = "localhost"
    PORT = int(sys.argv[1])
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("Connected to the game server.")
    print("How to play:")
    print("Wait for your turn, and when it is your turn input your move as x,y where x is the row and y is the column of your move. Note that 1 <= x, y <= 3")
    print("Waiting for other players to connect...")
    # Receive initial state.
    data = client.recv(1024).decode()
    current_player = data[0:1]
    our_symbol = data[1:2]

    id = 0 if our_symbol == 'X' else 1
    print("Retrieved symbol " + our_symbol + " and id = " + str(id))
    board = [list(row.split('|')) for row in data[2:].split('\n') if row]
    timer = 0 # Timer for wait notification.
    if our_symbol == 'O': # We decided in our game server that X starts first, can be changed as requirements of the project changes.
        print("Wait X to start!")
        print(print_board(board))

    while True:
        # Get board state.
        data = client.recv(1024).decode()
        current_player = data[0:1]
        our_symbol = data[1:2]
        board = [list(row.split('|')) for row in data[2:].split('\n') if row]

        if current_player == 'W': # Other player has won!
            print("State of the board:")
            print(print_board(board))
            print("You lost!")
            break
        if current_player == 'T': # Tie.
            print("State of the board:")
            print(print_board(board))
            print("It is a tie!")
            break
        if our_symbol == current_player: # Our turn to move.
            print("State of the board:")
            print(print_board(board))
            print("Turn information: Your turn!")
            move = input("Enter your move (row,col): ")
            client.sendall(str.encode(move))
            print("Wait for other player's turn.")
            data = client.recv(1024).decode() # Receive updated board.
        elif our_symbol != current_player:
            if timer % 100000 == 0:
                print("Turn information: Player " + current_player + "'s turn (Wait for their move).")
            timer += 1 
            continue
        

        # Parse the up to date received board state above.
        data = data.split(' ')
        moved_player = data[0]
        situation = data[1]
        board = [list(row.split('|')) for row in data[2].split('\n') if row]

        if situation == 'win':
            print("State of the board:")
            print(print_board(board))
            print("You won! Congrats!")
            break
        elif situation == 'tie':
            print("State of the board:")
            print(print_board(board))
            print("It's a tie!")
            break
        elif situation == 'resume':
            print("State of the board:")
            print(print_board(board))
            current_player = 'O' if moved_player == 'X' else 'X'
        else:
            if moved_player == our_symbol: # That means we made an illegal move.
                print("Played an invalid move.")
        
    # Close the client
    client.close()

if __name__ == "__main__":
    main()