#!/usr/bin/python3
#######################################################################
# Python script to produce a weighted tic-tac-toe game tree and
# serialize it using pickle, if a serialized tree file does not
# already exist
#
# Given a player and game board, outputs the optimal next move for that
# player
# usage: player sq1 sq2 sq3 sq4 sq5 sq6 sq7 sq8 sq9
#
# 27.09.2017 G.S.C.
#######################################################################

import pickle
import sys

SERIALFNAME = 'tree'

player = int(sys.argv[1])
board = [int(sq) for sq in sys.argv[2:11]]

# possible paths for winning:
#   rows: (0 1 2) (3 4 5) (6 7 8)
#   columns: (0 3 6) (1 4 7) (2 5 8)
#   diagonals: (0 4 8) (2 4 6)
paths = ((0,1,2), (3,4,5), (6,7,8),
         (0,3,6), (1,4,7), (2,5,8),
         (0,4,8), (2,4,6)) 

playerMap = str.maketrans({'0': ' ', '1': 'X', '2': 'O'})

class Node:
    def __init__(self, board):
        self.board = board
        self.children = [None]*9
        self.weight = None

    def __repr__(self):
        board = (' {0} | {1} | {2} \n---+---+---\n {3} | {4} | {5} \n---+---+---\n' +
                 ' {6} | {7} | {8} ').format(*self.board)
        
        return board.translate(playerMap)

    # only include the node's weight and children in the serialization
    # note that this means that a deserialized node will not have a board and cannot be printed
    def __getstate__(self):
        return {'children': self.children, 'weight': self.weight}
        
# check whether board represents a finished game
def isFinished(board):
    for path in paths:
        if board[path[0]] and (board[path[0]] == board[path[1]] == board[path[2]]):
            return board[path[0]]

    # stalemate (no winner and board is full)
    if all(board):
        return -1

    return 0

# recursively build game tree
def buildTree(node, player):
    # examine each board square
    for sq in range(9):
        # square is unclaimed
        if not node.board[sq]:
            # create a new child node with an updated board
            board = node.board[:]
            board[sq] = player
            child = Node(board)

            winner = isFinished(board)
            
            # game is finished so insert leaf into tree
            if winner:
                # player 1 won
                if winner == 1:
                    child.weight = 1

                # player 2 won
                elif winner == 2:
                    child.weight = -1

                # stalemate
                elif winner == -1:
                    child.weight = 0

                node.children[sq] = child

            # build a subtree rooted at the child, and alternate the player                
            else:
                node.children[sq] = buildTree(child, 1 if player == 2 else 2)
                
    return node

# print the whole tree (no formatted as a tree)
def printTree(node):
    if (node):
        print(node)
        print('weight:', node.weight)
        print()
        
        # examine each board square
        for sq in range(9):
            printTree(node.children[sq])

# print only the leaves of the tree
def printLeaves(node):
    if (not node):
        return
    
    if (not any(node.children)):
        print(node)
        print('weight:', node.weight)
        print()
        
    else:
        for sq in range(9):
            printLeaves(node.children[sq])

def weightInnerNodes(node):
    if (not node):
        return 0
    
    # reached a leaf
    if (node.weight == None):
        node.weight = sum([weightInnerNodes(child) for child in node.children])

    return node.weight

def optimalNextMove(tree):
    # traverse the tree to find (a) node corresponding to the current board state
    start1 = 0
    start2 = 0
    while start1 < 9 or start2 < 9:
        try:
            next1 = board.index(1, start1) # get the next square containing a 1
            tree = tree.children[next1]
            start1 = next1 + 1
        except: # no 1s remaining
            start1 = 9
            
        try:
            next2 = board.index(2, start2) # get the next square containing a 2
            tree = tree.children[next2]
            start2 = next2 + 1
        except: # no 2s remaining
            start2 = 9

    # find the child node/move corresponding to the optimal next move
    optMove = board.index(0) # first unoccupied square
    maxWeight = tree.children[optMove].weight
    
    # first player, so maximize weight
    if player == 1:
        for sq in range(9):
            if tree.children[sq] and tree.children[sq].weight > maxWeight:
                maxWeight = tree.children[sq].weight
                optMove = sq
                
    # second player, so minimize weight
    else:
        for sq in range(9):
            if tree.children[sq] and tree.children[sq].weight < maxWeight:
                maxWeight = tree.children[sq].weight
                optMove = sq

    return optMove

# try to open an existing serial tree file
try:
    serialf = open(SERIALFNAME, 'rb')
    
except FileNotFoundError:
    tree = buildTree(Node([0]*9), 1)
    weightInnerNodes(tree)    
    print(optimalNextMove(tree))

    # serialize the new tree
    serialf = open(SERIALFNAME, 'wb')
    pickle.dump(tree, serialf)

# if a serial tree file already exists, deserialize it    
else:
    tree = pickle.load(serialf)
    print(optimalNextMove(tree))
