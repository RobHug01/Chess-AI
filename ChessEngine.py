#This class is responsible for storing all the information about the current state of a chess game and determine valid moves

import copy


class GameState():
    def __init__(self):
        #board is 8x8 2d list, each element of the list has two characters
        #first character is piece color, second character is type of piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp" for i in range(8)],
            ["--" for i in range(8)],
            ["--" for i in range(8)],
            ["--" for i in range(8)],
            ["--" for i in range(8)],
            ["wp" for i in range(8)],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'B': self.getBishopMoves, 
                              'N': self.getKnightMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        self.boardLog = [copy.deepcopy(self.board)]
        self.counter = 0
        self.counterLog = []
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        #list of square where en-passant is possible
        self.enpassantPossible = [()]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move, promoteValue=""):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log move to display history and undo moves
        self.boardLog.append(copy.deepcopy(self.board))
        self.whiteToMove = not self.whiteToMove

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promoteValue

        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #Capturing the pawn

        #update enpassant possible square
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible.append(((move.startRow + move.endRow)//2, move.startCol))
        else:
            self.enpassantPossible.append(())

        #castle move
        if move.isCastle:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        #update Castle Rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        self.counterLog.append(self.counter)
        if move.pieceCaptured != "--" or move.pieceMoved[1] == "p":
            self.counter = 0
        else:
            self.counter = self.counter + 1
            
    
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.board[move.endRow][move.endCol] = "--"

            self.enpassantPossible.pop()
            self.castleRightsLog.pop()
            self.boardLog.pop()
            self.counter = self.counterLog.pop()
            self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks, self.castleRightsLog[-1].wqs, self.castleRightsLog[-1].bqs)

            if move.isCastle:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"

            self.checkMate = False
            self.staleMate = False

    #updates castle rights on a given move
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    #All moves concidering checks
    def getValidMoves(self):
        #1 generate all possible moves
        moves = self.getAllPossibleMoves()
        #2 for each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            #3 generate all possible opponent moves
            #4 for each of your opponents moves see if they attack king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                #5 if they attack king then its not a vliad move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                return moves
            else:
                self.staleMate = True
                return moves
        
        if self.counter == 100:
            self.staleMate = True
            return moves

        if self.boardLog.count(self.board) == 3:
            self.staleMate = True
            return moves
        
        bcounter = 0
        wcounter = 0
        for r in range(8):
            for c in range(8):
                if self.board[r][c] not in ["wK", "bK", "--", "wB", "wN", "bB", "bN"]:
                    return moves
                else:
                    if self.board[r][c] in ["wB", "wN"]:
                        wcounter = wcounter + 1
                    elif self.board[r][c] in ["bB", "bN"]:
                        bcounter = bcounter + 1
                    if wcounter == 2 or bcounter == 2:
                        return moves
                    
        self.staleMate = True
        print("1/2-1/2")
        return moves

    #old inCheck algorithm (slower)
    
    #def inCheck(self):   
        #if self.whiteToMove:
        #    return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        #else:
        #    return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    #new inCheck algorithm (faster)
    def inCheck(self):
        loc = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        return self.squareUnderAttack(*loc)
        
       
    def squareUnderAttack(self, r, c):
        revMoves = []
        enemy = "b" if self.whiteToMove else "w"
        loc = (r, c)
        var = 1 if self.whiteToMove else -1

        self.getQueenMoves(*loc, revMoves)
        for move in revMoves:
            if move.pieceCaptured == enemy + "Q":           
                return True
        revMoves = []
        self.getRookMoves(*loc, revMoves)
        for move in revMoves:
            if move.pieceCaptured == enemy + "R":               
                return True
        revMoves = []
        self.getKnightMoves(*loc, revMoves)
        for move in revMoves:
            if move.pieceCaptured == enemy + "N":               
                return True
        revMoves = []
        self.getBishopMoves(*loc, revMoves)
        for move in revMoves:
            if move.pieceCaptured == enemy + "B":                
                return True
        revMoves = []
        self.getKingMoves(*loc, revMoves, castle=False)
        for move in revMoves:
            if move.pieceCaptured == enemy + "K":
                return True
        revMoves = []
        if (loc[0] > 0 if enemy == "b" else loc[0] < 7):
            if loc[1] >= 1:
                if self.board[loc[0] - var][loc[1] - 1] == enemy + "p":               
                    return True
            if loc[1] <= 6:
                if self.board[loc[0] - var][loc[1] + 1] == enemy + "p":
                    return True

    #All moves without concidering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #num of rows
            for c in range(len(self.board[r])): #num of cols in each row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls move function for appropriate piece
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--": #one square ahead
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #two squares ahead if not moved
                  moves.append(Move((r, c), (r-2, c), self.board))
            if c >= 1:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible[-1]:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c <= 6:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible[-1]:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))
        else:
            if self.board[r+1][c] == "--": #one square ahead
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #two squares ahead if not moved
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c >= 1:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible[-1]:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c <= 6:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible[-1]:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))


    def getRookMoves(self, r, c, moves):
        enemyColor = 'b' if self.whiteToMove else 'w'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        enemyColor = 'b' if self.whiteToMove else 'w'
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        allyColor = 'w' if self.whiteToMove else 'b'
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves, castle=True):
        allyColor = 'w' if self.whiteToMove else 'b'
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
        
        if castle == True:
            self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):
        if self.inCheck():
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)
    
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastle=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastle=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filestoCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filestoCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastle = False):
        self.isEnpassantMove = isEnpassantMove
        self.isCastle = isCastle
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.startRow][self.endCol] if isEnpassantMove else board[self.endRow][self.endCol]
        
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self, promoteValue=""):
        #make this like real chess notation
        if self.isPawnPromotion:
            return self.getRankFile(self.endRow, self.endCol) + "=" + promoteValue
        elif self.isCastle:
            return "O-O-O" if self.endCol < self.startCol else "O-O"
        elif self.pieceCaptured != "--" and self.pieceMoved != "wp" and self.pieceMoved != "bp":
            return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        elif self.pieceCaptured != "--":
            return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol)
        elif self.pieceMoved == "bp" or self.pieceMoved == "wp":
            return self.getRankFile(self.endRow, self.endCol)
        else:
            return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]