from easyAI import TwoPlayerGame, AI_Player, Negamax
from easyAI.Player import Human_Player

# Define a class that contains all the ways to control the game.
class GameController(TwoPlayerGame):

    # First of all, the definition of what a game needs.
    def __init__(self, players):
        # Define the players
        self.players = players

        # Define who starts the game
        self.current_player = 2

        # Define the board to use for the game.
        self.board = [0] * 9

    # Defines all possible movements on the board.
    def possible_moves(self):
        return [str(a + 1) for a, b in enumerate(self.board) if b == 0]

    # Define how to update the board after the player moves. 
    def make_move(self, move):
        self.board[int(move) - 1] = self.current_player

    # Define how to determine if there is a loser in the game.
    def loss_condition(self):
        # Check if the opponent fills three in a line(horizontal, vertical, and diagonal).
        possible_combinations = [[0, 1, 2], [3, 4, 5], [6, 7, 8],  # horiz
                                 [0, 3, 6], [1, 4, 7], [2, 5, 8],  # vertical
                                 [0, 4, 8], [2, 4, 6]]  # diagonal

        return any([all([(self.board[i] == self.opponent_index)
                         for i in combination]) for combination in possible_combinations])

    # Check if the game is over
    def is_over(self):
        return (self.possible_moves() == []) or self.loss_condition()

    # Shows the current status of the board.
    def show(self):
        print('\n' + '\n'.join([' '.join([['.', 'O', 'X'][self.board[3 * j + i]]
                                          for i in range(3)]) for j in range(3)]))

    # Compute the score (using the loss_condition method)
    def scoring(self):
        return -100 if self.loss_condition() else 0

    # Unmake move to support AI evaluation.
    def unmake_move(self, move):
        self.board[int(move) - 1] = 0

    # Switch the current player after each move
    def switch_player(self):
        self.current_player = 3 - self.current_player  # This toggles between 1 and 2

# The process of starting the game.
# 1. Define the main function
if __name__ == "__main__":
    # 2. Define the algorithm (Use Negamax algorithm here.)
    algorithm = Negamax(7)

    # 3. Start the game
    GameController([Human_Player(), AI_Player(algorithm)]).play()
