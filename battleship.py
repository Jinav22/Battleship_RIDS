import random
import os
import time
from tkinter import *
from tkinter import font
from tkinter import messagebox
from functools import partial
from util_for_saving_data import *

TOKEN = os.environ["GITHUB_TOKEN"]
file_path = "Jinav22/Battleship_RIDS"
file_name = "data.txt"

frames = []
BOARD_SIZE = 8

data1 = ''
data2 = ''
human_ship_pos = []
bot_ship_pos = []
moves_h = []
moves_b = []


class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.position = {}
        self.sunk = False


class Player:
    def __init__(self, parent, name, auto=False, text=''):
        self.parent = parent
        self.name = name
        self.text = text
        self.auto = auto
        self.label = None
        self.status = None
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.reset()

    def reset(self):
        global frames
        self.initShips()
        self.sunk = 0
        self.board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.valid = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.valid += [[i, j]]
        self.turn = 0
        if len(frames) > 2:
            frames[-2].grid_forget()
            frames[-1].grid_forget()
            self.boardReset()

    # self.initShipPositions()

    def initShips(self):
        self.ships = []
        self.ships += [Ship("Carrier", 5)]
        self.ships += [Ship("Battleship", 4)]
        self.ships += [Ship("Submarine", 3)]
        self.ships += [Ship("Cruiser", 3)]
        self.ships += [Ship("Destroyer", 2)]
    #
    # def win(self):
    #     self.wins += 1
    #
    # def loss(self):
    #     self.losses += 1
    #
    # def tie(self):
    #     self.ties += 1
    #
    # def stats(self):
    #     return [self.wins, self.ties, self.losses]

    # Randomly place the ships on the board.  Searches for a valid location.
    # A valid location is a location where the ship fits completely on the board.
    # Also the ship must be in a location that is not already occupied by another ship
    def initShipPositions(self):
        for currentShip, ship in enumerate(self.ships):
            found = False
            while not found:
                ship.position = {}
                i = random.randint(0, len(self.valid) - 1)
                t = self.valid[i]
                x = t[0]
                y = t[1]
                # Try to place the ship horizontally or vertically
                # Trying horizontal or vertical placement first is random
                j = random.randint(0, 1)
                for k in range(2):
                    count = 1
                    x1 = x
                    y1 = y
                    ship.position = {}
                    found = True
                    for i in range(ship.size):
                        if j % 2 == 0:
                            x1 = x + i
                        else:
                            y1 = y + i
                        if [x1, y1] not in self.valid:
                            found = False
                            break
                        # Check to see if a ship already exists in this position
                        for foundShips in range(currentShip):
                            if (x1, y1) in self.ships[foundShips].position:
                                found = False
                                break
                        if not found:
                            break
                        ship.position[(x1, y1)] = 1
                    if found:
                        break
                    j += 1
            print(f"{ship.name} is in {ship.position}")
            bot_ship_pos.append(list(ship.position.keys()))
        self.printBoard()

    def printBoard(self):
        for i in range(BOARD_SIZE):
            print(self.board[i])
            #pass

    # Check our list of valid remaining moves to see if the move is valid
    def checkMove(self, x, y):
        if [x, y] in self.valid:
            moves_h.append([x, y])
            return True
        return False

    # Resets the GUI board for the player
    def boardReset(self):
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                self.buttons[x][y].configure(image=game.blank, compound="left")
        self.status.configure(text="Setup", fg="blue", bg="white")

    # Creates the GUI board for the player
    def boardInit(self):
        self.buttons = []
        for x in range(BOARD_SIZE):
            self.buttons += [[]]
            for y in range(BOARD_SIZE):
                if self.auto:
                    self.buttons[x] += [Button(frames[-1], text="", image=game.blank, borderwidth=1,
                                               command=partial(self.parent.tkplaceships, x, y, root))]
                else:
                    self.buttons[x] += [Button(frames[-1], text="", image=game.blank, borderwidth=1,
                                               command=partial(self.parent.tkmove, x, y, root))]
                self.buttons[x][y].grid(row=x, column=y)

    # Prompts user in the GUI.  Returns True if the user wants to play again, otherwise False
    def playAgain(self):
        return messagebox.askyesno("Game Over",
                                   f"{self.name} wins!  All ships were sunk in {self.turn} turns.  Would you like to play again?")


    # Display appropriate messages
    # If all ships were sunk, ask if the player wants to play again
    # Reset the game if the player wants to play again
    # Take action to end the game if the player does not want to play again
    # If ships still remain, inform the player that the ship was sunk.
    def shipWasSunkMessages(self, ship):
        global data1
        global data2

        print(f"{ship.name} was sunk!!")
        if self.sunk == 5:
            repository = github_setup(TOKEN, file_path)
            for i in human_ship_pos:
                data1 += ('\"' + ','.join([str(j) for j in i]) + '\"' + ',')

            data1 += ('\"' + ','.join([str(i) for i in moves_h]) + '\"' + ',')
            data1 += 'Human'

            print(data1)
            update_data, commit_message = update_github_file(repository, file_name, data1)
            print(update_data)
            push(repository, file_name, commit_message, update_data)

            #repository = github_setup(TOKEN, file_path)
            for i in bot_ship_pos:
                data2 += '\"' + ','.join([str(j) for j in i]) + '\"' + ','

            data2 += ('\"' + ','.join([str(i) for i in moves_b]) + '\"' + ',')

            data2 += 'Bot'

            data, commit_message = update_github_file(repository, file_name, data2)
            push(repository, file_name, commit_message, data)

            if self.playAgain():
                self.parent.reset()
                self.boardReset()
            else:
                self.parent.status = 'Over'
                root.destroy()
        else:
            self.status.configure(text=f"{ship.name} was sunk!", bg="white", fg="red")
        return True

    # Returns False if the ship was already sunk or if unhit sections of the ship remain
    # Returns True if the ship was sunk
    def isSunk(self, ship):
        if ship.sunk:
            return False
        for k in ship.position.keys():
            if list(k) in self.valid:
                return False
        ship.sunk = True
        self.sunk += 1
        return True

    def move(self, x, y, s):
        self.board[x][y] = s
        self.valid.pop(self.valid.index([x, y]))
        self.turn += 1
        foundHit = False
        for ship in self.ships:
            if ship.sunk == False and (x, y) in ship.position:
                self.buttons[x][y].configure(image=self.parent.hit, compound="left")
                self.status.configure(text=f"{ship.name} was hit!", bg="white", fg="red")
                foundHit = True
                if self.isSunk(ship):
                    self.shipWasSunkMessages(ship)
                break
        if not foundHit:
            self.buttons[x][y].configure(image=self.parent.miss, compound="left")
            self.status.configure(text=f"Miss.", bg="white", fg="blue")
        # print(self.board)

    # The computer's moves are random right now.  Some intelligence in the future would be nice.
    def autoMove(self):
        x = self.valid[random.randint(0, len(self.valid) - 1)]
        moves_b.append(x)
        return x

    # Returns True if we've placed the last ship, otherwise False
    def donePlacingShips(self, holdi):
        for x1, y1 in self.ships[holdi].position.keys():
            self.buttons[x1][y1].configure(image=self.parent.ship1, compound="left")
        if holdi == len(self.ships) - 1:
            return True
        return False

    # Returns False if the x,y position is already taken by another ship
    # Otherwise, the position is open, so True is returned
    def positionEmpty(self, x, y):
        for ship in self.ships:
            if (x, y) in ship.position:
                return False
        return True

    # Allows the player to place ships on their board wherever they choose
    # Uses the board GUI in order to place the ships
    # Will only allow legal placement of the ships
    def placeShips(self, x, y):
        found = False
        holdi = -1
        for i, ship in enumerate(self.ships):
            if len(ship.position) < ship.size:
                if len(ship.position) == 0:
                    found = True
                elif len(ship.position) == 1:
                    x1, y1 = list(ship.position.keys())[0]
                    if (x == x1 and (y == y1 + 1 or y == y1 - 1)) or \
                            (y == y1 and (x == x1 + 1 or x == x1 - 1)):
                        found = True
                else:
                    a = sorted(ship.position.keys())
                    xdif = a[1][0] - a[0][0]
                    ydif = a[1][1] - a[0][1]
                    if (x + xdif == a[0][0] and y + ydif == a[0][1]) or \
                            (x - xdif == a[-1][0] and y - ydif == a[-1][1]):
                        found = True
                holdi = i
                break
        if found and self.positionEmpty(x, y):
            self.ships[holdi].position[(x, y)] = 1
            self.buttons[x][y].configure(image=self.parent.ship, compound="left")
        else:
            for x1, y1 in self.ships[holdi].position.keys():
                self.buttons[x1][y1].configure(image=self.parent.blank, compound="left")
            self.ships[holdi].position = {}
            return False
        if self.ships[holdi].size == len(self.ships[holdi].position):
            human_ship_pos.append(list(ship.position.keys()))
            return self.donePlacingShips(holdi)
        return False


class Game:
    def reset(self):
        self.player.reset()
        self.computer.reset()
        self.status = 'Setup'

    def __init__(self):
        self.player = Player(self, "Player")
        self.computer = Player(self, "Computer", True)
        self.hit = PhotoImage(file="hit.gif").subsample(4, 4)
        self.miss = PhotoImage(file="miss.gif").subsample(4, 4)
        self.blank = PhotoImage(file="blank.gif").subsample(4, 4)
        self.ship = PhotoImage(file="ship.gif").subsample(4, 4)
        self.ship1 = PhotoImage(file="ship1.gif").subsample(4, 4)
        self.reset()

    # A move was made from our GUI
    def tkmove(self, x, y, root):
        # print(self.turn, self.player.text, x, y)
        if self.player.checkMove(x, y):
            self.player.move(x, y, 'X')
            if self.status == 'GamePlay':
                if self.computer.auto:
                    x, y = self.computer.autoMove()
                    # if self.player.sunk < 5:
                    self.computer.move(x, y, 'X')

    # Called when clicking on the player's board.  This is used to place the player's ships on their board.
    def tkplaceships(self, x, y, root):
        if self.status == 'Setup':
            if self.computer.placeShips(x, y):
                completeBoard(self, root)
                self.status = 'GamePlay'
        # print(self.computer.ships[0].position)


def startBoard(game, root):
    global frames
    frames += [Frame(root,  bg="blue", height=70, width=232)]
    frames[-1].pack_propagate(False)
    game.player.label = Label(frames[-1], text=f"{game.player.name}'s Board", fg="white", bg="blue",
                              font="Verdana 12 bold", anchor="center", justify="center")
    game.player.label.pack()
    game.computer.status = Label(frames[-1], text="Setup", fg="blue", bg="white", font="Verdana 16 bold",
                                 anchor="center", justify="center")
    game.computer.status.pack()
    frames[-1].grid(column=0, row=0, sticky="n")
    frames += [Frame(root, bg="blue")]
    frames[-1].pack_propagate(False)
    frames[-1].grid(sticky="n")
    game.computer.boardInit()
    return


def completeBoard(game,  root):
    global frames
    frames += [Frame(root, bg="blue", width=10)]
    frames[-1].grid(column=1, row=0, sticky="n")
    frames[-1] = Frame(root, bg="blue", height=70, width=232)
    frames[-1].pack_propagate(False)
    game.computer.label = Label(frames[-1], text=f"{game.computer.name}'s Board", fg="white", bg="blue",
                                font="Verdana 12 bold", anchor="center", justify="center")
    game.computer.label.pack()
    game.player.status = Label(frames[-1], text=f"You go first.", fg="blue", bg="white", font="Verdana 16 bold",
                               anchor="center", justify="center")
    game.player.status.pack()
    frames[-1].grid(column=2, row=0, sticky="n")
    frames += [Frame(root, bg="blue")]
    frames[-1].pack_propagate(False)
    frames[-1].grid(column=2, row=1, sticky="n")
    game.player.boardInit()
    game.player.initShipPositions()
    return


if __name__ == '__main__':
    root = Tk()
    root.title("Battleship Game")
    game = Game()
    startBoard(game, root)
    root.mainloop()
