import socket
import sys
import time
from threading import Thread

board = [['_', '_', '_'],
         ['_', '_', '_'],
         ['_', '_', '_']] # TicTacToe board.

global current_player
current_player = 'X' # We only have X and O.

global win_situation
win_situation = "O" # O: Game is ongoing, W: A player won, T: Game is tied.


def main():
    # Port number is required.
    if (len(sys.argv) < 2):
        print("Error! You should provide a port number.")
        exit()

    # Setting up the server..
    HOST = "localhost"
    PORT = int(sys.argv[1])
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)

    print("Waiting for clients to connect...")
    players = []
    while len(players) < 2:
        conn = server.accept()[0]
        players.append(conn)
        symbol = ''
        if len(players) == 1:
            symbol = "X"
        else:
            symbol = "O"
        id = 0 if len(players) == 1 else 1 # X gets ID 1, O gets ID 0.
        print("A client is connected, and it is assigned with the symbol " +
              symbol + " and ID = " + str(id) + ".")

    print("The game is starting!")
    print("Initial state of the board:")
    print(print_board())
    print("X starts first!")

    # Start the client threads.
    threads = []
    for i in range(2):
        conn = players[i]
        symbol = "X" if i == 0 else "O" # Likewise, first player gets X, second one gets O.
        thread = Thread(target=client_thread, args=(conn, symbol))
        thread.start()
        threads.append(thread)

    # Terminate the connection after threads end, i.e. when the game finishes.
    server.close()


# Handle client threads.
def client_thread(conn, player):
    global current_player
    global win_situation
    conn.sendall(str.encode(current_player + player + print_board())) # Send the current state.
    while True:
        try:
            # We loop if it is not player's turn.
            if player == current_player:
                time.sleep(1)
                if win_situation == "O": # Game is ongoing!
                    conn.sendall(str.encode(current_player + player + print_board())) # Send the game's current data.
                    data = conn.recv(1024).decode() # Receive the move.
                    row, col = map(int, data.split(','))
                    # Boundary fitting (User sends 1,1 and we translate it to 0,0 to fit our board matrix).
                    row = row - 1
                    col = col - 1
                elif win_situation == "W": # Player with other symbol has won the game.
                    conn.sendall(str.encode(win_situation + player + print_board()))
                    break
                else: # It is a tie.
                    conn.sendall(str.encode(win_situation + player + print_board()))
                    break
    
                # Update board
                if row >= 0 and row <= 2 and col >= 0 and col <= 2 and board[row][col] == '_':
                    board[row][col] = player
                    print("Player " + player + " played " + player +
                        " to the " + str(row + 1) + "," + str(col + 1))
                    print("State of the board:")
                    print(print_board())

                    # Check for win or tie
                    if check_win(current_player):
                        conn.sendall(str.encode(current_player + ' win ' + print_board()))
                        print("Player " + player + " won!")
                        win_situation = "W"
                        break
                    elif check_tie():
                        conn.sendall(str.encode(current_player + " tie " + print_board()))
                        print("Game is tied!")
                        win_situation = "T"
                        break
                    else: # Game is resuming.
                        conn.sendall(str.encode(
                            current_player + " resume " + print_board()))

                    # Toggle the current player.
                    if current_player == 'X':
                        current_player = 'O'
                    else:
                        current_player = 'X'

                    print("Waiting for " + current_player + "'s turn...")
                else:
                    conn.sendall(str.encode(player + ' invalid ' + print_board()))
        except ValueError:
            conn.sendall(str.encode(player + ' invalid ' + print_board()))
        except IndexError:
            conn.sendall(str.encode(player + ' invalid ' + print_board()))

    # Close connection, and switch one last time.
    if current_player == 'X':
        current_player = 'O'
    else:
        current_player = 'X'
    conn.close()

def print_board():
    board_str = ''
    for row in board:
        board_str += '|'.join(row) + '\n'
    return board_str

# Check if a player has won.
def check_win(player):
    for i in range(3):
        # Row win condition
        if board[i][0] == board[i][1] == board[i][2] == player:
            return True
        # Column win condition.
        if board[0][i] == board[1][i] == board[2][i] == player:
            return True
    # Left to right diagonal win condition.
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    # Right to left diagonal win condition.
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False

# Check if the game is tied.
def check_tie():
    for row in board:
        if '_' in row: # If there is no space left to play.
            return False
    return True

if __name__ == "__main__":
    main()
