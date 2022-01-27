#Storing game state and handling user input

import pygame as p
from pygame.constants import KEYDOWN
import ChessEngine
import ChessAI

p.init()
WIDTH = HEIGHT = 800
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
HIGHLIGHT = True
ANIMATION = False
IMAGES = {}

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        
def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess Engine")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    playerOne = True #If a human is playing white, then this is True
    playerTwo = False #If a human is playing black, then this is True
    promoteValue = ""

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    while running:
        humanTurn = playerOne if gs.whiteToMove else playerTwo
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #move handling
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): #unselect the square if double clicked
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    if move.isPawnPromotion:
                                        print("Enter promotion Value: Q for Queen, R for Rook, B for Bishop, or N for Knight: ") #Make GUI for this
                                        while promoteValue == "":    
                                            for e in p.event.get():
                                                if e.type == KEYDOWN:
                                                    if e.key == p.K_q:
                                                        promoteValue = "Q"
                                                    elif e.key == p.K_r:
                                                        promoteValue = "R"
                                                    elif e.key == p.K_b:
                                                        promoteValue = "B"
                                                    elif e.key == p.K_n or e.key == p.K_k:
                                                        promoteValue = "N"
                                        gs.makeMove(validMoves[i], promoteValue=promoteValue)
                                        print(validMoves[i].getChessNotation(promoteValue=promoteValue))
                                        promoteValue = ""
                                    else:
                                        gs.makeMove(validMoves[i])
                                        print(validMoves[i].getChessNotation())
                                    moveMade = True
                                    animate = True
                                    sqSelected = ()
                                    playerClicks = []
                        if not moveMade:        
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z and (humanTurn or gameOver): #'z' key
                    gs.undoMove()
                    gs.undoMove()
                    animate = False
                    moveMade = True
                    sqSelected = ()
                    playerClicks = []
                if e.key == p.K_r and (gs.checkMate or gs.staleMate):
                    gs = ChessEngine.GameState()
                    print("New Game:")
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        #AI move finder
        if not gameOver and not humanTurn:
            
            AIMove, score = ChessAI.findBestMove(gs, validMoves)
            score = score * -1 if not gs.whiteToMove else score
            if AIMove is None:
                AIMove = ChessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove) if not AIMove.isPawnPromotion else gs.makeMove(AIMove, promoteValue="Q")
            print(AIMove.getChessNotation(), score) if not AIMove.isPawnPromotion else print(AIMove.getChessNotation(promoteValue="Q"), score)
            moveMade = True
            animate = True
            score = 0            

        if moveMade:
            if animate and ANIMATION: animateMove(gs.moveLog[-1], screen, gs.board, clock)
            animate = False
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")

        if gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")

        if not gs.staleMate and not gs.checkMate:
            gameOver = False

        clock.tick(MAX_FPS)
        p.display.flip()
    p.quit()

#highlight square selected and possible moves for selected piece
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    if HIGHLIGHT: highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

#draws the squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#draws the pieces on the board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 #frames for one square of the move
    frameCount = max(abs(dR), abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH//2 - textObject.get_width()//2, HEIGHT//2 - textObject.get_height()//2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == '__main__':
    main()