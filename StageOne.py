#IMPORTS
import pygame
import pygame.freetype
import sys
import random
import math
from pygame.locals import*

#INIT
pygame.init()

#WINDOW DIMENSIONS/TITLE
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Galaga v0.4"

#SCREEN WINDOW SETUP
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

#FPS
FPS = 30
FPS_CLOCK = pygame.time.Clock()

#FONT
GAME_SCORE_FONT = pygame.freetype.Font("./fonts/ARCADEPI.TTF")

#SOUNDS
INTRO_MUSIC = pygame.mixer.Sound("./sounds/Galaga_Theme_Song.wav")
ENEMY_EXPLODE = pygame.mixer.Sound("./sounds/Enemy_Explode.wav")
PLAYER_FIRE = pygame.mixer.Sound("./sounds/Player_Fire.wav")
INTRO_MUSIC.set_volume(.2)
ENEMY_EXPLODE.set_volume(.2)
PLAYER_FIRE.set_volume(.2)

#EVENTS
BLINKEVENT = pygame.USEREVENT + 1
pygame.time.set_timer(BLINKEVENT, 800) 
STAGE_COOLDOWN = pygame.USEREVENT + 2
pygame.time.set_timer(STAGE_COOLDOWN, 500)
STAGE_START = pygame.USEREVENT + 3
pygame.time.set_timer(STAGE_START, 3000)
ENEM_STAGGER = pygame.USEREVENT + 4
pygame.time.set_timer(ENEM_STAGGER, 900)
SHOOT_COOLDOWN = pygame.USEREVENT + 5
pygame.time.set_timer(SHOOT_COOLDOWN, 350)
ENEM_DIVE = pygame.USEREVENT + 6
pygame.time.set_timer(ENEM_DIVE, 2500)
NET_ANIMATION = pygame.USEREVENT + 7
pygame.time.set_timer(NET_ANIMATION, 500)
GALAGA_ANIMATION = pygame.USEREVENT + 8
pygame.time.set_timer(GALAGA_ANIMATION, 100)
COMBINE_ANIMATION = pygame.USEREVENT + 9
pygame.time.set_timer(COMBINE_ANIMATION, 100)
ENEMY_FRAME_ANIMATION = pygame.USEREVENT + 10
pygame.time.set_timer(ENEMY_FRAME_ANIMATION, 500)
EXPLOSION_ANIMATION = pygame.USEREVENT + 11
pygame.time.set_timer(EXPLOSION_ANIMATION, 30)

#FAST IMAGE LOAD
def load(imageName, with_alpha = True):
    imageLink = pygame.image.load(f"./assets/{imageName}.png")
    if with_alpha:
        return imageLink.convert_alpha()
    else:
        return imageLink.convert()
    
#STAR CLASS------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Star():
    def __init__(self, offset = 0):
        self.x = random.randint(1+offset, SCREEN_WIDTH-offset) #
        self.y = random.randint(1+offset, SCREEN_HEIGHT-offset)
        self.color = (255, 255, 255)
        self.xSize = 2
        self.ySize = 1
#PLAYER CLASS-----------------------------------------------------------------------------------------------------------------------------------------------------------------
class Player():
    def __init__(self):
        self.model = load("sonoToori")
        self.twinModel = load("donoToori")
        self.rect = self.model.get_rect()
        self.size = self.rect.size
        self.x = SCREEN_WIDTH/2  - 20 #position
        self.y = SCREEN_HEIGHT - 150
        self.lives = 3
        self.lazerList = []
        self.angle = 0 #angle of sprite
        self.mode = "free"
        self.modelRotate = load("sonoToori") #used to blit rotated versions of the sprite (separate variable saves memory)
            
    #moves the player left and right with user inputs, IF the model isn't in a cutscene
    def move(self):
        if (self.mode != "locked"):
            if (pygame.key.get_pressed()[K_a] or pygame.key.get_pressed()[K_LEFT]) and self.x > 12:
                self.x-=12
            if (self.mode == "twin"):
                if (pygame.key.get_pressed()[K_d] or pygame.key.get_pressed()[K_RIGHT]) and self.x < SCREEN_WIDTH-90:
                    self.x+=12
            else:        
                if (pygame.key.get_pressed()[K_d] or pygame.key.get_pressed()[K_RIGHT]) and self.x < SCREEN_WIDTH-45:
                    self.x+=12
        self.blit()      
    
    #blits the current, appropriate model to the screen (handles all cases)        
    def blit(self):
        if (self.model == self.modelRotate):        
            SCREEN.blit(self.model,(self.x, self.y))  
        elif (self.mode == "twin"):
            SCREEN.blit(self.twinModel,(self.x, self.y))    
        else:
            SCREEN.blit(self.modelRotate,(self.x, self.y))
     
    #if the ship isn't in a cutscene, lazers are spawned at the cannon part of the sprite                       
    def shoot(self):
        if (self.mode != "locked"):
            if (self.mode == "twin"):
                PLAYER_FIRE.play()
                PLAYER_FIRE.play()
                self.lazerList.append(Lazer(self.x+18, self.y, -1))
                self.lazerList.append(Lazer(self.x+63, self.y, -1))
            else: 
                PLAYER_FIRE.play()   
                self.lazerList.append(Lazer(self.x+18, self.y, -1))
                
    #blits all of the lazers spawned by the ship           
    def lazerBlit(self):
        if (len(self.lazerList)!=0):
            for lazer in self.lazerList:
                lazer.blit()
                
    #moves all of the lazers spawned by the ship and removes them when they're offscreen            
    def lazerTravel(self):
        if (len(self.lazerList)!=0):
            for lazer in self.lazerList:
                lazY = lazer.move()
                if (lazY < -20):
                    self.lazerList.remove(lazer)
                        
#LAZER CLASS-----------------------------------------------------------------------------------------------------------------------------------------------------------------
class Lazer():
    def __init__(self, x, y, dir, xVel = 0):
        self.sprite = load("shotB")    
        self.x = x
        self.y = y
        self.xVelocity = xVel
        self.yVelocity = 5
        self.direction = dir
        self.rect = self.sprite.get_rect()
        self.size = self.rect.size
    
    #changes the lazer's x and y depending on the parameters it received when spawned
    def move(self):
        self.y += self.yVelocity * self.direction
        self.x += self.xVelocity * self.direction    
        return self.y
    
    #blits the lazer onscreen           
    def blit(self):
        SCREEN.blit(self.sprite, (self.x, self.y))  
            
#ENEMY CLASS------------------------------------------------------------------------------------------------------------------------------------------------------------------
class Enemy():
    def __init__(self, x, y, stableX, stableY):
        #moving position
        self.x = x
        self.y = y
        #cluster position
        self.stableX = stableX
        self.stableY = stableY
        #enemy hp (default is one)
        self.hp = 1
        #animation frames
        self.frames = None
        self.frameNum = None
        #movement stage
        self.stage = 1
        #distance (for loopdeloop)
        self.distance = 0
        #direction (for loopdeloop)
        self.dir = 1
        #for easier sprite access
        self.sprite = None
        #number for easy animation coordination
        self.number = None
        #for coordinated diving
        self.vertex = []
        #enemy sprite angle
        self.angle = 0
        #more precise return-position tracking for when enemies return after diving
        self.robot = []
        
    #cycles through an enemies animation frames
    def increaseFrame(self):
        self.frameNum += 1
        if (self.frameNum >= len(self.frames)):
            self.frameNum = 0
        
    #returns the hitbox of an enemy (NOT PRECISE, BEST FIT RECTANGLE)   
    def rect(self, sway = False):  
        rect = self.sprite.get_rect()
        if (sway):
            return Rect((self.stableX, self.stableY), rect.size)
        return Rect((self.x, self.y), rect.size) 
    
    #blits an enemy according to the situation    
    def blit(self, dontSkip = True):
        if (dontSkip): 
            self.sprite = self.frames[self.frameNum]
        else:
            self.y -= 50 #this is to blit the 'fighter-captured Galaga' sprite correctly   
        
        if (self.angle == -2): #just free positions
            SCREEN.blit(self.sprite, (self.x, self.y))
        elif (self.angle == -1 or self.x == self.stableX or self.y == self.stableY): #either stable or free positions depending on the situation
            if (self.stage != 0):
                SCREEN.blit(self.sprite, (self.x, self.y))    
            else:
                SCREEN.blit(self.sprite, (self.stableX, self.stableY))   
        else:                                                             #free positions with properly angled sprites
            tempSprite = pygame.transform.rotate(self.sprite, self.angle)    
            SCREEN.blit(tempSprite, (self.x, self.y))   
            
        if (dontSkip == False): #readjust back once 'fighter-captured Galaga' is properly implemented 
            self.y += 50              
    
    #enemy travels in an upside down heart shape starting top left then heading right towards the 'middle of the heart'    
    def rtlLoop(self):
        saveX = self.x #these two variables are for calculating the angle
        saveY = self.y
        if (self.stage == 1):
            self.x -= 10
            x = (self.x) * (1/2)  #scalar  
            self.y = ((math.sqrt(15000 - (((x - 129)**2))) * -1) + ((((x - 129)**2) * 100) ** (1/3)) + 40)/ (1/2.5)
            if (self.x <= 15):
                self.stage = 2   
        elif (self.stage == 2):
            if (self.x <= 35):
                self.x += 5
            else:    
                self.x += 10
            x = (self.x) * (1/2)  #scalar    
            self.y = ((math.sqrt(15000 - (((x - 129)**2))) * 1) + ((((x - 129)**2) * 100) ** (1/3)) + 40)/ (1/2.5)
            if (self.x >= 250):
                self.stage = 3
        elif (self.stage == 3):
            self.zero()   #reset to stable position
            
        if (self.stage!=0): #returns the correct angle of the sprite
            return self.getAngle(saveX, saveY)
        else:
            return -1    
    
    #enemy travels in an upside down heart shape starting top right then heading left towards the 'middle of the heart'          
    def ltrLoop(self):
        saveX = self.x
        saveY = self.y
        if (self.stage == 1):
            self.x += 10
            x = (self.x) * (1/2)  #scalar  
            self.y = ((math.sqrt(15000 - (((x - 163)**2))) * -1) + ((((x - 163)**2) * 100) ** (1/3)) + 60)/ (1/2.5)
            if (self.x >= 570):
                self.stage = 2   
        elif (self.stage == 2):
            if (self.x >= 550):
                self.x -= 5
            self.x -= 10
            x = (self.x) * (1/2)  #scalar    
            self.y = ((math.sqrt(15000 - (((x - 161)**2))) * 1) + ((((x - 161)**2) * 100) ** (1/3)) + 60)/ (1/2.5)
            if (self.x <= 330):
                self.stage = 3
        elif (self.stage == 3):
            self.zero()  
                
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1  
    
    #starts top right then heads left towards a loop de loop which leads to its stable position
    def rLoopdeLoop(self):
        saveX = self.x
        saveY = self.y
        if (self.stage == 1):
            self.x -= 10
            self.y = ((self.x-575.1) ** 2)  * ((-1)/767) + 550
            if (self.x <= 333):
                self.stage = 2
        elif (self.stage == 2):
            self.distance += 1
            self.x -= (10*self.dir)  
            self.y = math.sqrt((75 ** 2) - ((self.x - 375) ** 2)) * self.dir + 411.4
            if (self.x >= 450):
                self.dir = 1
            elif (self.x <= 300):
                self.dir = -1  
            if (self.distance >= (35)): 
                self.stage = 3
        elif (self.stage == 3):
            self.zero() 
                
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1       
    
    #starts top left then heads right towards a loop de loop which leads to its stable position                    
    def lLoopdeLoop(self):
        saveX = self.x
        saveY = self.y
        if (self.stage == 1):
            self.x += 10
            self.y = (self.x ** 2)  * ((-1)/767) + 550
            if (self.x >= 240):
                self.stage = 2
        elif (self.stage == 2):
            self.distance += 1
            self.x += (10*self.dir)
            self.y = math.sqrt((75 ** 2) - ((self.x - 205) ** 2)) * self.dir + 411.4
            if (self.x >= 275):
                self.dir = -1
            elif (self.x <= 130):
                self.dir = 1   
            if (self.distance >= (35)): #diameter * pi = circumference
                self.stage = 3
        elif (self.stage == 3):
            self.zero() 
                      
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1      
    
    #starts top left then does an oval-like arc towards its stable position    
    def rSwerve(self):
        saveX = self.x
        saveY = self.y
        if (self.stage == 1):
            self.x += 10
            self.y = (-1/200) * ((self.x-850)**2) + 900
            if (self.x >= 570):
                self.stage = 2
        elif (self.stage == 2):
            self.x -= 10
            self.y = (((100**2) - ((self.x - 470) ** 2))**(1/2)) * 1 + 508
            if (self.x <= 400):
                self.stage = 3
        elif (self.stage == 3):
            self.zero() 
            
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1 
            
    #starts top right then does an oval-like arc towards its stable position         
    def lSwerve(self):
        saveX = self.x
        saveY = self.y
        if (self.stage == 1):
            self.x -= 10
            self.y = (-1/200) * ((self.x+210)**2) + 900
            if (self.x <= 70):
                self.stage = 2
        elif (self.stage == 2):
            self.x += 10
            self.y = (((100**2) - ((self.x - 170) ** 2))**(1/2)) * 1 + 508
            if (self.x >= 240):
                self.stage = 3
        elif (self.stage == 3):
            self.zero()      
            
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1    
    
    #brings an enemy directly towards its stable position quickly    
    def zero(self):
        xCheck = False
        yCheck = False
        if (self.x < self.stableX):
            self.x += 20
            if (self.x >= self.stableX):
                self.x = self.stableX
        elif (self.x > self.stableX):
            self.x -= 20
            if (self.x <= self.stableX):
                self.x = self.stableX
        else:
            xCheck = True
        if (self.y < self.stableY):
            self.y += 25
            if (self.y >= self.stableY):
                self.y = self.stableY
        elif (self.y > self.stableY):
            self.y -= 25
            if (self.y <= self.stableY):
                self.y = self.stableY
        else:
            yCheck = True
            
        if (xCheck and yCheck):
            self.stage = 0      
    
    #brings an enemy directly towards its 'robot' position quickly (see init for def of robot)        
    def zeroRobot(self):
        xCheck = False
        yCheck = False
        for i in range(20):
            if (self.x < self.robot[0]):
                self.x += 1
            elif (self.x > self.robot[0]):
                self.x -= 1
            else:
                xCheck = True  
        self.y = round(self.y)        
        for i in range(25):
            if (self.y < self.robot[1]):
                self.y += 1
            elif (self.y > self.robot[1]):
                self.y -= 1
            else:
                yCheck = True        
        if (xCheck and yCheck):
            self.stage = 0               
    
    #calculates what angle the sprite should be                                           
    def getAngle(self, oldX, oldY):
        xDif = self.x - oldX
        yDif = self.y - oldY  
        if (isinstance(self.y, complex)):
            return
        angle = math.atan2(yDif, xDif) 
        self.angle = 180 - math.degrees(angle) + 90 
  
#GOEI subCLASS------------------------------------------------------------------------------------------------------------------------------------------------------------------              
class Goei(Enemy):
    def __init__(self, x, y, stableX, stableY):
        super().__init__(x, y, stableX, stableY)
        self.frames = [load("goei"), load("goei2")]
        self.frameNum = 0
    
    #travels a horizontal arc either towards the left or right, goes offscreen, and then resets to its robot position    
    def diveG(self, playX):
        saveX = self.x
        saveY = self.y
        if (len(self.vertex) < 3):
            if (playX > self.x):
                self.vertex.append(SCREEN_WIDTH/2 - self.stableX) 
            else:
                self.vertex.append(SCREEN_WIDTH/2 + self.stableX)
            self.vertex.append((SCREEN_HEIGHT/2)+60)
            self.vertex.append(1 + random.randint(1, 10)/10)
        if (self.stage == 1):
            if (len(self.vertex) < 4 and self.y > self.vertex[1]):
                self.vertex.append(-1)      
            self.y+=15
            a = (self.stableX - self.vertex[0]) / ((self.stableY - self.vertex[1])**3) 
            if (len(self.vertex) == 4):
                self.x = self.vertex[3] * (self.vertex[2]) * (a) * ((self.y - self.vertex[1]) ** 3) +  self.vertex[0] 
            else:    
                self.x = (a) * (self.vertex[2]) * ((self.y - self.vertex[1]) ** 3) +  self.vertex[0]
            if (self.y > SCREEN_HEIGHT + 100):
                self.stage = 2
                self.y = -50
                if (len(self.robot) > 0):
                    self.x = self.robot[0]
                else:
                    self.x = self.stableX    
        elif (self.stage == 2):
            if (len(self.robot)==0):
                if (self.y < self.stableY):
                    self.y += 15   
                else:
                    self.y = self.stableY
                    self.vertex.clear()
                    self.stage = 0  
            else:   
                if (self.y < self.robot[1]):
                    self.y += 15   
                else:
                    self.y = self.robot[1]
                    self.vertex.clear()
                    self.stage = 0     
                                          
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1     
#ZAKO subCLASS------------------------------------------------------------------------------------------------------------------------------------------------------------------       
class Zako(Enemy):
    def __init__(self, x, y, stableX, stableY):
        super().__init__(x, y, stableX, stableY)
        self.frames = [load("zako"), load("zako2")]
        self.frameNum = 0
    
    #travels an open, rounded rectangle then resets to its robot position   
    def diveZ(self, centerLine): 
        saveX = self.x
        saveY = self.y
        if (len(self.vertex) < 3):
            if (saveX < centerLine):
                self.vertex.append((SCREEN_WIDTH/2) + 70)
            else:
                self.vertex.append((SCREEN_WIDTH/2) - 70)    
            self.vertex.append((SCREEN_HEIGHT/2)+50)
            if (self.x < centerLine):
                self.vertex.append(1)
            else:
                self.vertex.append(-1)  
        if (self.stage == 1):
            self.x += (10 * self.vertex[2])
            a = ((self.stableY - self.vertex[1])) / ((self.stableX - self.vertex[0])**3)
            self.y = (a) * ((self.x-self.vertex[0])**3) + self.vertex[1]
            if (self.y > SCREEN_HEIGHT-100):
                self.stage = 2
                self.vertex[0] = self.x-(150 * self.vertex[2])
                self.vertex[1] = self.y+45 
        elif (self.stage == 2):
            self.x -= (10 * self.vertex[2])
            self.y = (-1/500) * ((self.x - (self.vertex[0])) ** 2) + self.vertex[1]
            if (self.y < SCREEN_HEIGHT-100):
                self.stage = 3 
        elif self.stage == 3:
            self.vertex.clear() 
            self.zeroRobot()   
                   
        if (self.stage!=0):
            return self.getAngle(saveX, saveY)
        else:
            return -1            
#GALAGA subCLASS------------------------------------------------------------------------------------------------------------------------------------------------------------------             
class Galaga(Enemy):
    def __init__(self, x, y, stableX, stableY):
        super().__init__(x, y, stableX, stableY)
        self.frames = [load("galaga"), load("galaga2"), load("galaga3"), load("galaga4")]
        self.withshipFrames = [load("galagaPlusShip"), load("galagaPlusShip2"), load("galagaPlusShip3"), load("galagaPlusShip4")]
        self.frameNum = 0  
        self.hp = 2  
        self.net = False
        self.netFrames = [load("net25"), load("net50"), load("net75"), load("net"), load("net2"), load("net3")]  
        self.netFrameNum = 0
        self.frameCount = 0
        self.hasPlayer = False
    
    #OVERRIDE 
    #ensures that the enemy blit function blits the correct version of the Galaga sprite, also blits the Galaga's net when necessary  
    def blit(self):
        if (self.net):
            SCREEN.blit(self.netFrames[self.netFrameNum], (self.x-32, self.y+30))
        if (self.hp == 1 and self.frameNum < 2):
            self.frameNum += 2  
        if (self.hasPlayer):    
            self.sprite = self.withshipFrames[self.frameNum]    
            super().blit(False)    
        else:
            super().blit() 
            
    #OVERRIDE  
    #since Galaga has different sprites when hp = 2 and hp = 1, the sprites must be adjusted differently (since they are grouped together)      
    def increaseFrame(self):
        self.frameNum += 1
        if (self.hp == 1):
            if (self.frameNum >= 4):
                self.frameNum = 2 
        else:
            if (self.frameNum >= 2):
                self.frameNum = 0                 
    
    #Heads vertically down near the player and attempts to spawn the net over them, if the player is already captured or in dual mode then it just performs a thwomp-like motion       
    def diveGG(self, playX, skipNet):
        saveX = self.x
        saveY = self.y
        if (len(self.vertex) < 3):
            if (playX > self.x):
                self.vertex.append(self.stableX) 
            else:
                self.vertex.append(self.stableX)
            self.vertex.append((SCREEN_HEIGHT/2)+50)
            self.vertex.append(1 + random.randint(1, 10)/10)
        if (self.stage == 1):
            if (len(self.vertex) < 4 and self.y > self.vertex[1]):
                self.vertex.append(-1)      
            self.y+=15
            a = (self.stableX - self.vertex[0]) / ((self.stableY - self.vertex[1])**3) 
            if (len(self.vertex) == 4):
                self.x = self.vertex[3] * (self.vertex[2]) * (a) * ((self.y - self.vertex[1]) ** 3) +  self.vertex[0] 
            else:    
                self.x = (a) * (self.vertex[2]) * ((self.y - self.vertex[1]) ** 3) +  self.vertex[0]
            if (self.y > SCREEN_HEIGHT - 360 and skipNet == False): 
                self.stage = 2
                self.net = True
            elif (self.y > SCREEN_HEIGHT - 100 and skipNet):
                self.stage = 3
        elif (self.stage == 2):
            if (self.frameCount > 6):
                self.frameCount = 0
                self.net = False
                self.stage = 3
        elif (self.stage == 3):
            self.vertex.clear() 
            self.zeroRobot()
                 
        if (self.stage == 1 or self.stage == 3):
            return self.getAngle(saveX, saveY)
        else:
            return -1                          
#TITLESCREEN CLASS------------------------------------------------------------------------------------------------------------------------------------------------------------  
class TitleScreen():
    def __init__(self):
        self.highscore = 20000  
        self.score = 0 
        self.blink = True #Makes sure that the "PUSH START BUTTON" text is blinking on screen 1
        self.screen = 1 #Manages the different screens to blit
        
        self.starList = [] #Holds every star to blit
        
        self.stage = 1
        self.stagePart = 1 #tracks subparts of the stage 
        self.enemyMode = 1 #controls the default enemy movement when they are 'stable'
        
        self.smallShipSprite = load("shipSmall") #this is for blitting the lives in the bottom left
        self.playerOne = Player() #The Player
        
        for i in range(50): #Creates 50 stars to blit on launch
            self.starList.append(Star())
            
        self.enemyList = []  
        self.diveList = [] #tracks currently diving enemies
        
        self.totalSway = 0 #tracks the enemies offset during self.enemyMode = 1
        self.centerPoint = [0, 90] #this is just a random, default center point for before the real one can be calculated
        
        self.canShoot = False #prohibits the player from shooting while loading
        
        self.enemyLazerList = [] #tracks the lazers fired from enemies
        
        self.netAnimate = False 
        self.galagaAnimateStep = 0 #this is for progressing the galaga capturing animation
        self.combinePlayerAnimateStep = 0 #this is for progressing the dual ship combination animation
        self.combineStartPoint = [] #for setting a starting position for the combine animation
        self.tempPlayer = None #this is for animation purposes only
        self.playerCaptured = False 
        
        self.explosionList = [] #for blitting multiple enemy explosions at the same time
        self.explosionFrames = [load("explosion1"), load("explosion2"), load("explosion3"), load("explosion4"), load("explosion5")] #explosion sprite
        
    #STAGE SETUP
    def stageSetup(self):
        if (self.stage == 1):
            self.enemyList = [Goei(305, 1000, 270, 150), Goei(345, 1000, 330, 150), Goei(385, 1000, 270, 200), Goei(425, 1000, 330, 200), Zako(300, 1000, 270, 250), Zako(260, 1000, 330, 250), Zako(220, 1000, 270, 300), Zako(180, 1000, 330, 300), Galaga(-50, -100, 218, 90), Goei(-100, -100, 220, 150), Galaga(-150, -100, 272, 90), Goei(-200, -100, 220, 200), Galaga(-250, -100, 327, 90), Goei(-300, -100, 380, 150), Galaga(-350, -100, 378, 90), Goei(-400, -100, 380, 200), Goei(700, 650, 480, 150), Goei(750, 650, 430, 150), Goei(800, 650, 480, 200), Goei(850, 650, 430, 200), Goei(900, 650, 120, 150), Goei(950, 650, 170, 150), Goei(1000, 650, 120, 200), Goei(1050, 650, 170, 200), Zako(400, 1000, 430, 250), Zako(450, 1000, 380, 250), Zako(500, 1000, 430, 300), Zako(550, 1000, 380, 300), Zako(600, 1000, 220, 250), Zako(650, 1000, 170, 250), Zako(700, 1000, 220, 300), Zako(750, 1000, 170, 300), Zako(300, 1000, 70, 250), Zako(250, 1000, 120, 250), Zako(200, 1000, 70, 300), Zako(150, 1000, 120, 300), Zako(100, 1000, 480, 250), Zako(50, 1000, 530, 250), Zako(0, 1000, 480, 300), Zako(-50, 1000, 530, 300)]    
            self.diveList.append(self.enemyList[0])
        for i in range(len(self.enemyList)):
            self.enemyList[i].number = i
    #WIN AND LOSE CONDITIONS       
    def winLoseCondition(self):
        if (self.playerOne.lives <= 0):
            self.screen = 5
        if (len(self.enemyList) == 0):
            self.screen = 5
            GAME_SCORE_FONT.render_to(SCREEN, (70, 400), "THAT'S IT FOR NOW", "white", size=40)
            GAME_SCORE_FONT.render_to(SCREEN, (50, 450), "THANKS FOR PLAYING!", "white", size=40)                 
   #ALL TEXT
   #blits all text, ordered from top to bottom & left to right; Also calls ALL relevant functions for each screen
    def blitCorrect(self):
        if self.screen == 1:
            self.blitText1()
        elif self.screen == 2:
            self.blitText2()    
        elif self.screen == 3:
            self.blitText3()
        elif self.screen == 4:
            self.blitText4()
        elif self.screen == 5:
            self.blitText5()            
   
    def blitText1(self):
        GAME_SCORE_FONT.render_to(SCREEN, (50, 5), "1UP", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (70, 30), f"{self.score}", "white", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (220, 5), "HIGH SCORE", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (280, 30), f"{self.highscore}", "white", size=30)
        if (self.blink):
            GAME_SCORE_FONT.render_to(SCREEN, (140, 290), "PUSH START BUTTON", "white", size=30)   
        GAME_SCORE_FONT.render_to(SCREEN, (80, 410), "1ST BONUS FOR 30000 PTS", "yellow", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (80, 480), "2ND BONUS FOR 120000 PTS", "yellow", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (80, 550), "AND FOR EVERY 120000 PTS", "yellow", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (100, 650), "1981 2022 NOMO LTD.", "white", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (125, 700), "ALL RIGHTS RESERVED", "white", size=25)
        #image blit
        SCREEN.blit(self.smallShipSprite, (20, 400))
        SCREEN.blit(self.smallShipSprite, (20, 470))
        SCREEN.blit(self.smallShipSprite, (20, 540))
   
    def blitText2(self):
        self.blitStars()
        GAME_SCORE_FONT.render_to(SCREEN, (50, 5), "1UP", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (70, 30), f"{self.score}", "white", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (220, 5), "HIGH SCORE", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (280, 30), f"{self.highscore}", "white", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (250, 380), f"Player 1", "white", size=30)
        
    def blitText3(self):
        self.blitStars()
        GAME_SCORE_FONT.render_to(SCREEN, (50, 5), "1UP", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (70, 30), f"{self.score}", "white", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (220, 5), "HIGH SCORE", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (280, 30), f"{self.highscore}", "white", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (250, 380), f"STAGE {self.stage}", "white", size=30)
        self.blitPlayer()
        
    def blitText4(self):
        self.winLoseCondition()
        self.blitStars(True) #load stars first
        GAME_SCORE_FONT.render_to(SCREEN, (50, 5), "1UP", "red", size=30)
        if (self.score < 10):
            GAME_SCORE_FONT.render_to(SCREEN, (70, 30), f"{self.score}", "white", size=30)
        else:
            GAME_SCORE_FONT.render_to(SCREEN, (60 - ((len(str(self.score))/2)*10), 30), f"{self.score}", "white", size=30)        
        GAME_SCORE_FONT.render_to(SCREEN, (220, 5), "HIGH SCORE", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (280, 30), f"{self.highscore}", "white", size=30)
        #all necessary functions for the game
        self.blitLives()
        self.blitPlayer()
        self.explosionAnimation()
        self.blitEnemy()
        for i in range(7):
            self.playerOne.lazerTravel()
            self.lazerCollision()
        self.playerOne.lazerBlit()
        self.enemyCollision()
        if (self.combinePlayerAnimateStep > 0):
            self.combineAnimation()   
        self.destroyEnem()  
        
    def blitText5(self):
        GAME_SCORE_FONT.render_to(SCREEN, (50, 5), "1UP", "red", size=30)
        if (self.score < 10):
            GAME_SCORE_FONT.render_to(SCREEN, (70, 30), f"{self.score}", "white", size=30)
        else:
            GAME_SCORE_FONT.render_to(SCREEN, (60 - ((len(str(self.score))/2)*10), 30), f"{self.score}", "white", size=30)        
        GAME_SCORE_FONT.render_to(SCREEN, (220, 5), "HIGH SCORE", "red", size=30)
        GAME_SCORE_FONT.render_to(SCREEN, (280, 30), f"{self.highscore}", "white", size=30)
        
        if (self.playerOne.lives == 0):
            GAME_SCORE_FONT.render_to(SCREEN, (160, 200), "GAME OVER", "red", size=50)
        else:
            GAME_SCORE_FONT.render_to(SCREEN, (155, 200), "WELL DONE!", "blue", size=50)
                
        
        GAME_SCORE_FONT.render_to(SCREEN, (70, 400), "THAT'S IT FOR NOW", "white", size=40)
        GAME_SCORE_FONT.render_to(SCREEN, (50, 450), "THANKS FOR PLAYING!", "white", size=40) 
        
              
            
    #BLINKS "PUSH START BUTTON" on screen 1           
    def blinkText(self):
        if self.blink:
            self.blink = False
        else:
            self.blink = True      
            
    #BLITS AND MOVES STARS
    def blitStars(self, move = False):   
        for star in self.starList:
            pygame.draw.rect(SCREEN, star.color, (star.x, star.y, star.xSize, star.ySize))
            rand = random.randint(1,5)
            if (rand == 2):
                star.color = (0, 0, 0)
            else:
                star.color = (255, 255, 255) 
            if move:
                star.y += 10
                if (star.y>SCREEN_HEIGHT):
                    self.starList.remove(star) 
                    while (len(self.starList) < 85): 
                        self.starList.append(Star(-300))    
                
    #MOVES PLAYER (see Player Class for more)
    def blitPlayer(self):
        if (self.playerOne.lives >= 0):
            self.playerOne.move()
           
    #BLITS ALL ENEMIES AND ENSURES THAT THEY ARE SYNCHRONIZED AND HAVE THE CORRECT PARAMETERS INDIVIDUALLY
    def blitEnemy(self):
        next = True
        if (self.enemyMode == 2): 
            for enem in self.diveList:
                if (enem.stage == 0):
                    enem.stage = 1
                if (isinstance(enem, Zako)):
                    enem.diveZ(self.centerPoint[0])  
                elif (isinstance(enem, Goei)):
                    enem.diveG(self.playerOne.x)  
                elif (isinstance(enem, Galaga)):  
                    if (enem.net and enem.hasPlayer == False and self.playerOne.mode != "twin" and self.combinePlayerAnimateStep < 1):
                        self.netAnimate = True
                    else:
                        self.netAnimate = False    
                    if (self.playerCaptured):    
                        enem.diveGG(self.playerOne.x, True) 
                    else:
                        enem.diveGG(self.playerOne.x, False)   
                    self.netCollision()
                if (enem.stage == 0):
                    if (len(enem.robot) > 0):
                        enem.x = enem.robot[0]
                        enem.y = enem.robot[1]
                    self.diveList.remove(enem)                                
        if self.stage == 1: #calls enemy spawns
            for i in range(len(self.enemyList)):
                if (self.enemyList[i] not in self.diveList):
                    self.enemyList[i].angle = -1
                    if (self.enemyMode == 2):
                        self.enemyList[i].angle = -2    
                if (self.enemyList[i].stage != 0):
                    if (self.stagePart == 1 and self.enemyList[i].number < 8):
                        next = False
                        if (self.enemyList[i].number < 4):
                            self.enemyList[i].rtlLoop()
                        elif (self.enemyList[i].number < 8):
                            self.enemyList[i].ltrLoop()                   
                    if (self.stagePart == 2 and self.enemyList[i].number < 24):
                        next = False
                        if (self.enemyList[i].number < 16):
                            self.enemyList[i].lLoopdeLoop() 
                        elif (self.enemyList[i].number < 24):
                            self.enemyList[i].rLoopdeLoop()    
                    elif (self.stagePart == 3 and self.enemyList[i].number < 40):
                        next = False
                        if (self.enemyList[i].number < 32):
                            self.enemyList[i].lSwerve()     
                        elif (self.enemyList[i].number < 40):
                            self.enemyList[i].rSwerve()                                                        
                self.enemyList[i].blit()     
            if next and self.stagePart < 4:
                self.stagePart += 1   
            if self.stagePart == 4:
                self.enemyMode = 2
                self.stagePart = 5        
                self.centerPoint[0] = 320 + self.totalSway
                self.totalSway = 0
                for enem in self.enemyList:
                    if (len(enem.robot)==0):
                        enem.robot.append(enem.x)
                        enem.robot.append(enem.y)
                    enem.x = enem.stableX
                    enem.y = enem.stableY        
                                                      
    #BLITS PLAYER LIVES       
    def blitLives(self):
        for i in range(self.playerOne.lives):
            SCREEN.blit(self.smallShipSprite, (30 + (45 * i), 850))        
    
    #MOVES ENEMIES STABLE POSITIONS ACCORDING TO self.enemyMode        
    def staggerEnem(self):
        if (self.enemyMode == 1): #horizontal motion
            rand = random.randrange(-10, 11, 10)
            if (self.totalSway + rand > 60):
                rand = -10
            elif (self.totalSway - rand < -60):
                rand = 10
            else:
                self.totalSway += rand    
            for enem in self.enemyList:
                if (enem.x == enem.stableX):
                    enem.x += rand
                enem.stableX += rand 
        elif (self.enemyMode == 2): #diagonal motion
            sign = 1
            if (self.totalSway >= 10):
                sign = -1             
            for enem in self.enemyList:
                notDive = True
                if (enem in self.diveList):
                    notDive = False
                xDif = enem.stableX - self.centerPoint[0]
                yDif = abs(enem.stableY - self.centerPoint[1])
                for i in range(0, 201, 50):
                    if (xDif > i):
                        if (notDive):
                            enem.x += 5 * sign 
                        enem.robot[0] += 5 * sign  
                    elif (xDif < -i):
                        if (notDive):
                            enem.x -= 5 * sign  
                        enem.robot[0] -= 5 * sign     
                for i in range(50, 501, 30):        
                    if (yDif > i):
                        if (notDive):
                            enem.y += 5 * sign     
                        enem.robot[1] += 5 * sign        
            self.totalSway += 5 
            if (self.totalSway == 20):
                self.totalSway = 0             
                
    #TRACKS LAZER HITBOXES AND CORRECTLY HANDLES LAZER INTERACTIONS                        
    def lazerCollision(self):
        for lazer in self.playerOne.lazerList: #lazer with enemy
            for enem in self.enemyList:
                if ((enem.rect(()))).colliderect(Rect((lazer.x, lazer.y), lazer.size)):    
                    enem.hp -= 1
                    if (lazer in self.playerOne.lazerList):
                        self.playerOne.lazerList.remove(lazer) 
        for lazer in self.enemyLazerList: #lazer with player
            lazY = lazer.move()
            lazer.blit()
            if (lazY > SCREEN_HEIGHT + 30): #offscreen
                self.enemyLazerList.remove(lazer)
                return
            if ((Rect((self.playerOne.x, self.playerOne.y), self.playerOne.size))).colliderect(Rect((lazer.x, lazer.y), lazer.size)):
                self.playerOne.lives -= 1
                self.enemyLazerList.remove(lazer)
    #GETS A RANDOM ENEMY TO DO THEIR DIVE ANIMATION                                                
    def addEnemyDive(self):
        if (self.enemyMode != 2 or len(self.enemyList) <= 1 or self.galagaAnimateStep > 0):
            return
        if (len(self.diveList) < 2):
            rand = random.randint(0, len(self.enemyList)-1)
            self.diveList.append(self.enemyList[rand])  
            chosenEnem = self.enemyList[rand]
            xLeg = chosenEnem.x - self.playerOne.x
            yLeg = chosenEnem.y - self.playerOne.y 
            propX = (5 / yLeg) * xLeg 
            if (self.netAnimate and isinstance(self.enemyList[rand], Galaga)):
                self.addEnemyDive()
                return
            self.enemyLazerList.append(Lazer(self.enemyList[rand].x, self.enemyList[rand].y, .8, propX)) 
    #ALLOCATES THE CORRECT SCORE FOR DESTROYING AN ENEMY THEN REMOVES THEM FROM THE GAME       
    def destroyEnem(self):
        for enem in self.enemyList:
            if (enem.hp <= 0):
                if (isinstance(enem, Goei)):
                    self.score += 80
                elif (isinstance(enem, Zako)):
                    self.score += 100
                elif (isinstance(enem, Galaga)):
                    if (enem.hasPlayer == True):
                        self.score += 800
                        self.playerOne.mode = "stuck"
                        self.combinePlayerAnimateStep = 1   
                        self.combineStartPoint = [enem.x, enem.y]
                        self.playerCaptured = False
                    else:
                        self.score += 400 
                self.explosionList.append([enem.rect().centerx, enem.rect().centery, 0])
                ENEMY_EXPLODE.play()
                if (enem in self.diveList):
                    self.diveList.remove(enem)           
                self.enemyList.remove(enem)
    #HANDLES ENEMY COLLIDING WITH PLAYER INTERACTION                      
    def enemyCollision(self):
        if (self.enemyMode != 2 or self.galagaAnimateStep > 0):
            return
        for enem in self.diveList:
            if ((enem.rect(()))).colliderect(Rect((self.playerOne.x, self.playerOne.y), self.playerOne.size)):
                self.playerOne.lives -= 1
                if (enem in self.diveList):
                    self.diveList.remove(enem) 
                if (enem in self.enemyList):      
                    self.enemyList.remove(enem)   
    #PROPERLY DISPLAYS THE FRAMES OF Galaga's NET WHEN IT IS ACTIVE                
    def netAnimation(self):
        for enem in self.diveList:
            if (isinstance(enem, Galaga)):
                enem.netFrameNum += 1
                if (self.galagaAnimateStep < 1):
                    enem.frameCount += 1
                if (enem.netFrameNum >= len(enem.netFrames)):
                    enem.netFrameNum = 3 
             
                       
    #HANDLES THE PLAYER COLLIDING WITH Galaga's NET INTERACTION AND SUBSEQUENT ANIMATION                
    def netCollision(self):
        if ((self.netAnimate == False and self.galagaAnimateStep != 2)):
            return
        save = None
        for enem in self.diveList:
            if (isinstance(enem, Galaga)):
                save = enem
                
        if (save == None):
            self.netAnimate = False
            self.galagaAnimateStep = 0
            return

        if (self.galagaAnimateStep == 0):
            rec = save.netFrames[save.netFrameNum].get_rect()
            if (Rect(save.x, save.y+30, rec[2], rec[3]).colliderect(Rect((self.playerOne.x, self.playerOne.y), self.playerOne.size))):
                self.playerOne.x = save.x 
                self.playerOne.mode = "locked"
                self.galagaAnimateStep = 1
        elif (self.galagaAnimateStep == 1):
            if (self.playerOne.y < save.y+30):
                self.playerOne.angle = 0
                self.netAnimate = False
                self.galagaAnimateStep = 2
                save.stage = 3
                save.frameCount = 0
                save.net = False
        elif (self.galagaAnimateStep == 2):
            self.playerOne.x = save.x
            self.playerOne.y = save.y+30      
            self.playerCaptured = True
            if (self.playerOne.y == save.stableY + 30):
                save.hasPlayer = True 
                self.galagaAnimateStep = 0 
                self.playerOne.lives -= 1
                self.playerOne.x = SCREEN_WIDTH/2  - 20
                self.playerOne.y = SCREEN_HEIGHT - 150
                self.playerOne.mode = "free"
    #ANIMATE THE PLAYER TRAVELING UP Galaga's NET                              
    def galagaAnimation(self):
        if (self.playerOne.mode != "locked"):
            return
        self.playerOne.y -= 4
        self.playerOne.angle += 60
        self.playerOne.modelRotate = pygame.transform.rotate(self.playerOne.model, self.playerOne.angle)
    #ANIMATES THE PLAYER COMBINING WITH THE FORMERLY CAPTURED PLAYER   
    def combineAnimation(self):
        if (self.combinePlayerAnimateStep == 1):
            self.tempPlayer = Player()
            self.tempPlayer.x = self.combineStartPoint[0]
            self.tempPlayer.y = self.combineStartPoint[1]
            self.combinePlayerAnimateStep = 2
        if (self.combinePlayerAnimateStep == 2):
            self.tempPlayer.angle += 30
            self.tempPlayer.modelRotate = pygame.transform.rotate(self.tempPlayer.model, self.tempPlayer.angle)
            if (self.tempPlayer.angle >= 1080):
                self.combinePlayerAnimateStep = 3
                if (self.playerOne.x < SCREEN_WIDTH/2):
                    self.tempPlayer.mode = "right"
                else:
                    self.tempPlayer.mode = "left"    
        elif (self.combinePlayerAnimateStep == 3):
            xDone = False
            yDone = False
            if (self.tempPlayer.mode == "right"):
                for i in range(5):
                    if (self.tempPlayer.x < self.playerOne.x + 45):
                        self.tempPlayer.x += 1
                    elif (self.tempPlayer.x > self.playerOne.x + 45):
                        self.tempPlayer.x -= 1
                    else:
                        xDone = True
            elif (self.tempPlayer.mode == "left"):
                for i in range(5):
                    if (self.tempPlayer.x < self.playerOne.x - 45):
                        self.tempPlayer.x += 1
                    elif (self.tempPlayer.x > self.playerOne.x - 45):
                        self.tempPlayer.x -= 1
                    else:
                        xDone = True
            for i in range(15):
                if (self.tempPlayer.y < self.playerOne.y):
                    self.tempPlayer.y += 1
                else:
                    yDone = True
            if (xDone and yDone):
                if (self.tempPlayer.mode == "left"):
                    self.playerOne.x -= 45
                self.playerOne.mode = "twin" 
                self.combinePlayerAnimateStep = 0
                self.tempPlayer = None
        if (self.tempPlayer != None):        
            self.tempPlayer.blit()    
    #ENSURES ALL ENEMIES ARE ANIMATED IN SYNC                
    def enemyFrameAnimation(self):
        for enem in self.enemyList:
            enem.increaseFrame()    
    #ANIMATES ENEMIES EXPLOSION ANIMATION WHEN DESTROYED        
    def animateExplosionAnimation(self):
        if (len(self.explosionList) == 0):
            return
        
        for item in self.explosionList:
            item[2] += 1
            if (item[2] >= len(self.explosionFrames)):
                self.explosionList.remove(item)
    #BLITS THE ENEMIES EXPOSION ANIMATION WHEN DESTROYED                         
    def explosionAnimation(self):
        if (len(self.explosionList) == 0):
            return
        
        for item in self.explosionList:
            SCREEN.blit(self.explosionFrames[item[2]], (item[0]-35, item[1]-35))
                                                                          
#MAIN==========================================================================================================================================================================       
def test():
    titleScreen = TitleScreen()
    titleScreen.stageSetup()
    while(1):
        #ALL GAME EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if titleScreen.screen == 1 and event.key == K_SPACE and not pygame.mixer.music.get_busy():
                    titleScreen.screen = 2  
                    INTRO_MUSIC.play()  
                elif titleScreen.screen == 4 and event.key == K_SPACE and titleScreen.canShoot:
                    titleScreen.playerOne.shoot()  
                    titleScreen.canShoot = False        
            if titleScreen.screen == 1 and event.type == BLINKEVENT:
                titleScreen.blinkText()
            if titleScreen.screen == 2 and event.type == STAGE_COOLDOWN:
                titleScreen.screen = 3
            if titleScreen.screen == 3 and event.type == STAGE_START:
                titleScreen.screen = 4          
            if titleScreen.screen == 4  and event.type == ENEM_STAGGER:   
                titleScreen.staggerEnem()   
            if titleScreen.screen == 4 and event.type == SHOOT_COOLDOWN and titleScreen.canShoot == False:
                titleScreen.canShoot = True     
            if titleScreen.enemyMode == 2 and event.type == ENEM_DIVE:
                titleScreen.addEnemyDive() 
            if titleScreen.netAnimate and event.type == NET_ANIMATION and titleScreen.playerOne.mode != "twin":
                titleScreen.netAnimation()   
            if titleScreen.galagaAnimateStep == 1 and event.type == GALAGA_ANIMATION:
                titleScreen.galagaAnimation()  
            if titleScreen.screen == 4 and event.type == ENEMY_FRAME_ANIMATION:
                titleScreen.enemyFrameAnimation()   
            if titleScreen.screen == 4 and event.type == EXPLOSION_ANIMATION:
                titleScreen.animateExplosionAnimation()                                           
        SCREEN.fill("black") #GAME BACKGROUND
        titleScreen.blitCorrect() #BLITS THE CORRECT SCREEN
        if (pygame.key.get_pressed()[K_RETURN]): #DEBUGGING SPEEDUP
            FPS = 300
        else:
            FPS = 30      
        GAME_SCORE_FONT.render_to(SCREEN, (555, 865), "FPS " + str(int(FPS_CLOCK.get_fps())), "white", size=20) #FPS COUNTER
        pygame.display.update() #UPDATES FRAMES
        FPS_CLOCK.tick(FPS)  #LOCKS FPS
                
if __name__ == "__main__":
    test()     