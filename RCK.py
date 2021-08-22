import pygame, sys, random, time
from pygame.locals import *

FPS = 30 # 초당 프레임
WINDOWWIDTH = 759 # 윈도우의 너비 (이하 픽셀 단위)
WINDOWHEIGHT = 600 # 윈도우의 높이
BOARDHEIGHT = 512
CARDWIDTH = 77 # 카드의 너비
CARDHEIGHT = 108 # 카드의 높이
CARDGAPWIDTH = 32 #카드 사이의 가로 간격
LEFTCARDXPOS = 320 # 가장 왼쪽 카드의 X좌표
TOPCARDYPOS = 35 # 위 카드의 Y좌표
BOTCARDYPOS = 368 # 아래 카드의 Y좌표 
PIECEWIDTH = 39
PIECEHEIGHT = 54
PIECEGAPWIDTH = 27
PIECEGAPHEIGHT = 7
LEFTPIECEXPOS = [59, 25]
TOPPIECEYPOS = 45

#          R    G    B
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
BEIGE  = (255, 242, 204)
RED    = (255,   0,   0)
YELLOW = (255, 242,   0)

HIGHLIGHTCARDCOLOR = BLACK
BGCOLOR = BEIGE
HIGHLIGHTPIECECOLOR1 = RED
HIGHLIGHTPIECECOLOR2 = YELLOW

ROCK = 'rock'
SCISSOR = 'scissor'
PAPER = 'paper'
PLAYER1 = 0
PLAYER2 = 1

    
def main():
    global DISPLAYSURF, FPSCLOCK, BOARD, UNCLICKEDBUTTON, CLICKEDBUTTON
    global ROCKCARD, SCISSORCARD, PAPERCARD
    global ROCKPIECE_0, SCISSORPIECE_0, PAPERPIECE_0, ROCKPIECE_1, SCISSORPIECE_1, PAPERPIECE_1
    global PLAYER1WIN, PLAYER2WIN
    global HELPTEXT
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('R_C_K')

    STARTSCREEN = pygame.image.load('startScreen.png')
    BOARD = pygame.image.load('board.png')
    ROCKCARD = pygame.image.load('rockCard.png')
    SCISSORCARD = pygame.image.load('scissorCard.png')
    PAPERCARD = pygame.image.load('paperCard.png')
    UNCLICKEDBUTTON = pygame.image.load('okButton.png')
    CLICKEDBUTTON = pygame.image.load('okButtonClicked.png')
    ROCKPIECE_0 = pygame.image.load('rockPiece0.png')
    SCISSORPIECE_0 = pygame.image.load('scissorPiece0.png')
    PAPERPIECE_0 = pygame.image.load('paperPiece0.png')
    ROCKPIECE_1 = pygame.image.load('rockPiece1.png')
    SCISSORPIECE_1 = pygame.image.load('scissorPiece1.png')
    PAPERPIECE_1 = pygame.image.load('paperPiece1.png')    
    PLAYER1WIN = pygame.image.load('player1win.png')
    PLAYER2WIN = pygame.image.load('player2win.png')
    HELPTEXT10 = pygame.image.load('helptext10.png')
    HELPTEXT11 = pygame.image.load('helptext11.png')
    HELPTEXT2 = pygame.image.load('helptext2.png')
    
    HELPTEXT = [[HELPTEXT10, HELPTEXT11], HELPTEXT2]
    
    showScreen(STARTSCREEN)
    while True:
        showScreen(runGame())
    
    
def runGame():
    #
    global mainCards, mainPiece
    global PLAYER1WIN, PLAYER2WIN

    mainCards = getRandomizedCards() # 카드 정보(상대: [0][0:4], 자신: [1][0:4])
    mainPiece = pieceSetting() # 말 정보

    turn = random.choice([PLAYER1, PLAYER2])

    while True:
        if turn == PLAYER1:
            oneTurn(PLAYER1)
            if isWinner(mainPiece, PLAYER1):
                winningImg = PLAYER1WIN
                break
            turn = PLAYER2
        elif turn == PLAYER2:
            oneTurn(PLAYER2)
            if isWinner(mainPiece, PLAYER2):
                winningImg = PLAYER2WIN
                break
            turn = PLAYER1

    return winningImg
        
            

def oneTurn(player):
    # 
    global DISPLAYSURF, FPSCLOCK, BOARD, UNCLICKEDBUTTON, CLICKEDBUTTON
    global HELPTEXT
    global mainCards, mainPiece

    mousex = 0 # 마우스 이벤트 발생 시 x좌표
    mousey = 0 # 마우스 이벤트 발생 시 y좌표
    
    usedCard = makeUsedCardData(False) # 해당 위치의 카드가 사용되었는지 확인
    clickedPiece = makeClickedPieceData(False) # 해당 위치의 말이 클릭되었는지 확인
    showedPiece = makeClickedPieceData(False) # 해당 위치의 말이 이동 가능한 경로인지 확인
    buttonPushed = False # '확인' 버튼의 눌러짐 여부
    firstSelection = None # 처음 고른 카드의 종류 = 움직일 말과 카드의 종류
    selectedCardNum = 0 # 고른 카드의 갯수 = 말 움직이기의 남은 횟수
    pieceClicked = False # 말의 클릭 여부
    beforeMovePiece = [0, 0] # 클릭 된 말의 이동 전 좌표
    BUTTON = UNCLICKEDBUTTON
    HELP = HELPTEXT[0][player]
                             
    while True: # 게임 루프        
        mouseClicked = False # 마우스 클릭 여부

        DISPLAYSURF.fill(WHITE)
        DISPLAYSURF.blit(BOARD, (0, 0))
        DISPLAYSURF.blit(BUTTON, (452, 213))
        DISPLAYSURF.blit(HELP, (0, 512))
        
        drawCard(mainCards)
        showUsedCard(usedCard)
        drawPiece(mainPiece)
        showShowedPiece(clickedPiece, mainPiece)
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        cardi, cardj = getCardAtPixel(mousex, mousey)
        # (사용: 카드를 클릭해서 하이라이트가 유지되는 상태, 선택: 마우스가 카드 위에 있으나 클릭은 하지 않은 상태)
        if cardi != None and cardj != None and cardi == player and not buttonPushed: # 마우스가 카드 위에 있고 확인 버튼이 클릭되지 않았을 때
            if not usedCard[cardi][cardj]: # 카드가 사용되지 않았을 때
                if firstSelection == None or mainCards[cardi][cardj] == firstSelection:
                    drawHighlightCard(cardi, cardj, HIGHLIGHTCARDCOLOR)
                if mouseClicked: # 카드가 사용되지 않았고 카드를 클릭했을 때
                    if firstSelection == None: # 처음 사용한 카드일 때
                        firstSelection = mainCards[cardi][cardj]
                        usedCard[cardi][cardj] = True
                        mouseClicked = False
                        selectedCardNum += 1
                    elif mainCards[cardi][cardj] == firstSelection: # 사용한 카드가 처음 사용한 카드와 같은 종류일 때
                        usedCard[cardi][cardj] = True
                        mouseClicked = False
                        selectedCardNum += 1
            if usedCard[cardi][cardj] and mouseClicked: # 선택된 카드가 사용되었고 카드를 클릭했을 때
                usedCard[cardi][cardj] = False
                selectedCardNum -= 1
                if selectedCardNum == 0: # 사용된 카드가 없을 때
                    firstSelection = None
        if isButtonPushed(mousex, mousey) and mouseClicked: # 확인 버튼이 클릭되었을 때
            buttonPushed = True
            BUTTON = CLICKEDBUTTON
            HELP = HELPTEXT[1]
        
        piecei, piecej = getPieceAtPixel(mousex, mousey)
        if piecei != None and piecej != None and mainPiece[piecei][piecej][1] == player and buttonPushed and mainPiece[piecei][piecej][0] == firstSelection and selectedCardNum > 0: # 마우스가 올바른 말 위에 있고 말이 이동 가능할 때
            if not clickedPiece[piecei][piecej] and not pieceClicked:
                drawHighlightPiece(piecei, piecej, HIGHLIGHTPIECECOLOR1)
                if mouseClicked:
                    clickedPiece[piecei][piecej] = True
                    pieceClicked = True
                    mouseClicked = False
                    showedPiece = getShowedPiece(mainPiece, piecei, piecej)
                    beforeMovePiece = [piecei, piecej]
        if pieceClicked and mouseClicked and buttonPushed:
            if not (piecei != None and piecej != None and showedPiece[piecei][piecej]):
                piecei = beforeMovePiece[0]
                piecej = beforeMovePiece[1]
                clickedPiece[piecei][piecej] = False
                pieceClicked = False
                showedPiece = makeClickedPieceData(False)
        if piecei != None and piecej != None and showedPiece[piecei][piecej] and buttonPushed and pieceClicked and mouseClicked:
            movePiece(mainPiece, beforeMovePiece[0], beforeMovePiece[1], piecei, piecej)
            showedPiece = makeClickedPieceData(False)
            clickedPiece = makeClickedPieceData(False)
            pieceClicked = False
            selectedCardNum -= 1
        if buttonPushed and selectedCardNum == 0:
            fillUsedCard(mainCards, usedCard)
            BUTTON = UNCLICKEDBUTTON
            break
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        

def selectRCK():
    # 가위 바위 보 중 랜덤으로 하나를 뽑는다.
    whichshape = random.randint(0, 2)
    if whichshape == 0:
        return ROCK
    elif whichshape == 1:
        return SCISSOR
    else:
        return PAPER

def getRandomizedCards():
    # 카드를 뽑아 리스트에 정보를 저장한다.
    cards = []
    for y in range(2):
        player = []
        for x in range(4):
            player.append(selectRCK())
        cards.append(player)
    return cards

def pieceSetting():
    # 게임판을 리스트로 만들고 말을 배치한다.
    piece = [[[0, 0] for width in range(4)] for height in range(7)]
    piece[0][0] = [ROCK, 0]
    piece[0][1] = [PAPER, 0]
    piece[0][2] = [ROCK, 0]
    piece[1][0] = [SCISSOR, 0]
    piece[1][3] = [SCISSOR, 0]
    piece[2][1] = [SCISSOR, 0]
    piece[6][0] = [ROCK, 1]
    piece[6][1] = [PAPER, 1]
    piece[6][2] = [ROCK, 1]
    piece[5][0] = [SCISSOR, 1]
    piece[5][3] = [SCISSOR, 1]
    piece[4][1] = [SCISSOR, 1]
    return piece

def drawHighlightCard(cardi, cardj, color):
    # 선택된 카드 주변에 지정된 색을 그린다.
    left, top = getPixelAtCard(cardi, cardj)
    pygame.draw.rect(DISPLAYSURF, color, (left-10, top-10, CARDWIDTH + 20, CARDHEIGHT + 20), 4)

def makeUsedCardData(val):
    # 전달된 값을 2*4 리스트에 저장한다.
    usedCard = []
    for i in range(2):        usedCard.append([val] * 4)
    return usedCard

def makeClickedPieceData(val):
    # 전달된 값을 7*4 리스트에 저장한다.
    clickedPiece = []
    for i in range(7):
        clickedPiece.append([val] * 4)
    return clickedPiece
    
def drawRCKCard(whichcard, left, top):
    # 카드를 그린다.
    global DISPLAYSURF, ROCKCARD, SCISSORCARD, PAPERCARD

    if whichcard == ROCK:
        DISPLAYSURF.blit(ROCKCARD, (left, top))
    elif whichcard == SCISSOR:
        DISPLAYSURF.blit(SCISSORCARD, (left, top))
    elif whichcard == PAPER:
        DISPLAYSURF.blit(PAPERCARD, (left, top))

def drawRCKPiece(whichpiece, whosepiece, left, top):
    # 말을 그린다.
    global DISPLAYSURF, ROCKPIECE_0, SCISSORPIECE_0, PAPERPIECE_0, ROCKPIECE_1, SCISSORPIECE_1, PAPERPIECE_1

    if whichpiece == ROCK and whosepiece == 0:
        DISPLAYSURF.blit(ROCKPIECE_0, (left, top))
    elif whichpiece == SCISSOR and whosepiece == 0:
        DISPLAYSURF.blit(SCISSORPIECE_0, (left, top))
    elif whichpiece == PAPER and whosepiece == 0:
        DISPLAYSURF.blit(PAPERPIECE_0, (left, top))
    if whichpiece == ROCK and whosepiece == 1:
        DISPLAYSURF.blit(ROCKPIECE_1, (left, top))
    elif whichpiece == SCISSOR and whosepiece == 1:
        DISPLAYSURF.blit(SCISSORPIECE_1, (left, top))
    elif whichpiece == PAPER and whosepiece == 1:
        DISPLAYSURF.blit(PAPERPIECE_1, (left, top))

def fillUsedCard(cards, usedCard):
    # 사용한 카드를 확인하고 새로 채워 넣는다.
    for cardi in range(2):
        for cardj in range(4):
            if usedCard[cardi][cardj]:
                cards[cardi][cardj] = selectRCK()
                drawCard(cards)
                usedCard[cardi][cardj] = 0
        

def drawCard(cards):
    # 저장된 카드정보를 그리기 함수에 전달한다.
    left = LEFTCARDXPOS
    top = TOPCARDYPOS
    for cardi in range(2):
        for cardj in range(4):
            drawRCKCard(cards[cardi][cardj], left, top)
            left += (CARDWIDTH + CARDGAPWIDTH)
        left = LEFTCARDXPOS
        top = BOTCARDYPOS

def drawPiece(piece):
    # 저장된 말판정보를 그리기 함수에 전달한다.
    left = LEFTPIECEXPOS[0]
    top = TOPPIECEYPOS
    for piecei in range(7):
        left = LEFTPIECEXPOS[piecei % 2]
        piecewidth = 3 + piecei % 2
        for piecej in range(piecewidth):
            drawRCKPiece(piece[piecei][piecej][0], piece[piecei][piecej][1], left, top)
            left += (PIECEWIDTH + PIECEGAPWIDTH)
        top += (PIECEHEIGHT + PIECEGAPHEIGHT)
        
            

def showUsedCard(usedCard):
    # 사용된 카드에 하이라이트를 그린다.
    for cardi in range(2):
        for cardj in range(4):
            if usedCard[cardi][cardj]:
                drawHighlightCard(cardi, cardj, HIGHLIGHTCARDCOLOR)

def showShowedPiece(clickedPiece, piece):
    # 클릭된 말의 이동 가능 경로를 보여준다.
    for piecei in range(7):
        for piecej in range(4):
            if clickedPiece[piecei][piecej]:
                showPossibleWay(piece, piecei, piecej)

def getCardAtPixel(x, y):
    # 픽셀 좌표계를 카드의 좌표계로 변환한다.
    for cardi in range(2):
        for cardj in range(4):
            left, top = getPixelAtCard(cardi, cardj)
            cardRect = pygame.Rect(left, top, CARDWIDTH, CARDHEIGHT)
            if cardRect.collidepoint(x, y):
                return (cardi, cardj)
    return (None, None)

def getPixelAtCard(cardi, cardj):
    # 카드의 좌표계를 픽셀 좌표계로 변환한다.
    left = LEFTCARDXPOS + cardj * (CARDWIDTH + CARDGAPWIDTH)
    top = TOPCARDYPOS + cardi * (BOTCARDYPOS - TOPCARDYPOS)
    return (left, top)

def getPieceAtPixel(x, y):
    # 픽셀 좌표계를 말의 좌표계로 변환한다.
    for piecei in range(7):
        piecewidth = 3 + piecei % 2
        for piecej in range(piecewidth):
            left, top = getPixelAtPiece(piecei, piecej)
            pieceRect = pygame.Rect(left, top, PIECEWIDTH, PIECEHEIGHT)
            if pieceRect.collidepoint(x, y):
                return (piecei, piecej)
    return (None, None)

def getPixelAtPiece(piecei, piecej):
    # 말의 좌표계를 픽셀 좌표계로 변환한다.
    left = LEFTPIECEXPOS[piecei % 2] + piecej * (PIECEWIDTH + PIECEGAPWIDTH)
    top = TOPPIECEYPOS + piecei * (PIECEHEIGHT + PIECEGAPHEIGHT)
    return (left, top)

def isButtonPushed(x, y):
    # 마우스가 버튼 위에 있으면 1, 없으면 0을 반환한다.
    button = pygame.Rect(452, 213, 140, 84)
    if button.collidepoint(x, y):
        return True
    else:
        return False

def myPieceWin(mypiece, yourpiece):
    # 두 말을 비교해 전자가 이기면 1, 아니면 0을 전달한다.
    if mypiece[1] == yourpiece[1]:
        return 0                       
    elif mypiece[0] == ROCK:
        if yourpiece[0] == SCISSOR:
            return 1
        else:
            return 0
    elif mypiece[0] == SCISSOR:
        if yourpiece[0] == PAPER:
            return 1
        else:
            return 0
    elif mypiece[0] == PAPER:
        if yourpiece[0] == ROCK:
            return 1
        else:
            return 0

def drawHighlightPiece(piecei, piecej, color):
    # 선택된 말 주변에 지정된 색을 그린다.
    left, top = getPixelAtPiece(piecei, piecej)
    pygame.draw.rect(DISPLAYSURF, color, (left - 0.5, top - 0.5, PIECEWIDTH + 2, PIECEHEIGHT + 2), 3)

def showPossibleWay(piece, piecei, piecej):
    # 한 말을 주변으로 이동 가능한 경로를 계산하고 맞으면 하이라이트를 그린다.
    jdiffstart = (piecei % 2) * (-1)
    for idiff in range(-1, 2, 2):
        for jdiff in range(jdiffstart, jdiffstart + 2):
            showi = piecei + idiff
            showj = piecej + jdiff
            if showi >= 7 or showi < 0 or showj < 0 or showj >= (3 + showi % 2):
                continue
            if piece[showi][showj] == [0, 0] or myPieceWin(piece[piecei][piecej], piece[showi][showj]):
                drawHighlightPiece(showi, showj, HIGHLIGHTPIECECOLOR2)

def getShowedPiece(piece, piecei, piecej):
    # showedPiece 리스트를 생성한다.
    showedPiece = makeClickedPieceData(False)
    jdiffstart = (piecei % 2) * (-1)
    for idiff in range(-1, 2, 2):
        for jdiff in range(jdiffstart, jdiffstart + 2):
            showi = piecei + idiff
            showj = piecej + jdiff
            if showi >= 7 or showi < 0 or showj < 0 or showj >= (3 + showi % 2):
                continue
            if piece[showi][showj] == [0, 0] or myPieceWin(piece[piecei][piecej], piece[showi][showj]):
                showedPiece[showi][showj] = True
    return showedPiece

def movePiece(piece, beforepiecei, beforepiecej, afterpiecei, afterpiecej):
    # 말을 움직인다.
    piece[afterpiecei][afterpiecej] = piece[beforepiecei][beforepiecej]
    piece[beforepiecei][beforepiecej] = [0, 0]

def isWinner(piece, player):
    # 게임 종료를 확인한다.
    oppenentpaper = 0
    for cardi in range(7):
        for cardj in range(4):
            if piece[cardi][cardj] == [PAPER, not player]:
                oppenentpaper = 1
    if not oppenentpaper:
        return True

def showScreen(screen):
    global DISPLAYSURF

    DISPLAYSURF.blit(screen, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                return

        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()    
