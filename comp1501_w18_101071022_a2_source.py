import pygame
import random
import math
import time
import csv
"""
	print ("     ┌─[Yiwei' Guide for B.C.S. at Carleton University]───────────────────┐     ")
	print ("     │     This is a game that guides you to finish the dues and pass     │     ")
	print ("     │finals in order to pass the 1st year as a Computer Science          │     ")
	print ("     │Undergraduate 				                          │     ")
	print ("     │ GG & GL, Have fun!                                                 │     ")
	print ("     └────────────────────────────────────┘     ")
"""

# the window is the actual window onto which the camera view is resized and blitted
global window_wid,window_hgt,frame_rate,delta_time
window_wid = 1200
window_hgt = 800

# the frame rate is the number of frames per second that will be displayed and although
# we could (and should) measure the amount of time elapsed, for the sake of simplicity
# we will make the (not unreasonable) assumption that this "delta time" is always 1/fps
frame_rate = 40
delta_time = 1 / frame_rate
GPAcalculator=(('A+',12,101,90),('A',11,90,85),('A-',10,85,80),('B+',9,80,77),('B',8,77,73),('B-',7,73,70),('C+',6,70,67),('C',5,67,63),('C-',4,63,60),('D+',3,60,57),('D',2,57,53),('D-',1,52,50),('F',0,50,-1)) 

# constants for designating the different games states
STATE_TITLE = 0
STATE_PAUSE = 1
STATE_READY = 2
red=(255,180,180)
green=(180,255,180)
blue=(200,200,255)
white=(255,255,255)
grey=(125,125,125)

#### ====================================================================================================================== ####
#############                                         INITIALIZE                                                   #############
#### ====================================================================================================================== ####
from pygame.locals import *

def read_csv(file_name):
    list_csv=[]   
    with open(file_name,'r+',newline='') as csv_file:
        reader = csv.reader(csv_file)
        for i in reader:
            list_csv.append(i)
    return list_csv

def LaserDict(list_csv):
    lasers=[]
    for k in range(1,len(list_csv),1):
        laser={}
    #handle strings in csv, change them to datatypes we need:
        laser[list_csv[0][0]]=list_csv[k][0]
        laser[list_csv[0][1]]=float(list_csv[k][1])
        laser[list_csv[0][2]]=int(list_csv[k][2])
        laser[list_csv[0][3]]=[int(list_csv[k][3].split(',')[0]),int(list_csv[k][3].split(',')[1])]
        laser[list_csv[0][4]]=[float(list_csv[k][4].split(',')[0]),float(list_csv[k][4].split(',')[1])]
        laser[list_csv[0][5]]=[float(list_csv[k][5].split(',')[0]),float(list_csv[k][5].split(',')[1])]
        laser[list_csv[0][6]]=int(list_csv[k][6])
        laser[list_csv[0][7]]=int(list_csv[k][7])
        laser[list_csv[0][8]]=int(list_csv[k][8])
        laser[list_csv[0][9]]=bool(list_csv[k][9])
        laser[list_csv[0][10]]=bool(list_csv[k][10])
        laser['seg']=[]    
        lasers.append(laser)
        #print (laser)
    return  lasers


def initialize():
    ''' Central Initialize function. Calls helper functions to initialize Pygame and then the gameData dictionary.
    Input: None
    Output: gameData Dictionary
    '''
    pygame.key.set_repeat(1, 1)
    screen = pygame.display.set_mode((1200, 800))
    return initializeData(screen)

def initializeData(screen, numCannonBalls=12, numTargets=1):   #############IMPORTANT
    ''' Initializes the gameData dictionary. Includes: Entity Data and Logistical Data (isOpen).
    Input: pygame screen
    Output: gameData Dictionary
    '''
    # Initialize gameData Dictionary
    gameData = {"screen": screen,
                "background": pygame.transform.scale(pygame.image.load("resources/backgrounds/background.png").convert_alpha(), (1200, 800)),
                "START":pygame.transform.scale(pygame.image.load("resources/backgrounds/gameover.png").convert_alpha(), (1200, 800)),
                "OVER":pygame.transform.scale(pygame.image.load("resources/backgrounds/gameover.png").convert_alpha(), (1200, 800)),
                "entities": [],
                'isOpen': True,
                "ammo": pygame.transform.scale(pygame.image.load("resources/cannonball/cannonball.png").convert_alpha(), (20,20)),    
                "settings": {"maxTargets": numTargets,
                             "maxCannonBalls": numCannonBalls},
                "score":[100,100,100,100],
                #{'Comp1405:100,'Comp1406':100,'Comp1501':100,'Comp1805':100},
                'gameover':False,
                'combatClock':pygame.time.Clock(),
                'combatTime':0.0   ,
                'CGPA':None,
                'state': 'start'
                }

   # Initialize Target Object(s)
    for _ in range(numTargets):
        gameData["entities"].append({"type": "target",
                                     "location": [1200, random.randint(200, 600)],
                                     "size": (150, 150),
                                     "sprite": pygame.transform.scale(pygame.image.load("resources/targets/target_{}.png".format(random.randint(1, 4))).convert_alpha(), (88, 88)),
                                     "isHit": False,
                                     "isDisappear": False,
                                     "clock": 0
                                     })

    # Initialize CannonBall Object(s)
    for _ in range(numCannonBalls):
        gameData["entities"].append({"type": "cannonball",
                                     "location": [1100, 750],
                                     "velocity": None,
                                     "size": (25,25),
                                     "sprite": pygame.transform.scale(pygame.image.load("resources/cannonball/cannonball.png").convert_alpha(), (25,25)),
                                     "exists": False,
                                     "destroy": False,
                                     "reload":False})


    # Initialize Cannon Object(s)
    gameData["entities"].append({"type": "cannon",
                                 "location": [300, 550], # Note: When rotating, you may need to adjust the location to (1300, 875) depending on your method
                                 "size": (200, 150),
                                 "sprite": pygame.transform.scale(pygame.image.load("resources/cannons/cannon.png").convert_alpha(), (200, 150)),
                                 "loaded": True,
                                 "isFiring": False,
                                 "angle": 45.00,
                                 "isMoving": False,
                                 "power": 10,
                                 "velocity": [4,4],
                                 'direction':{'left':None,'right':None,'up':None,'down':None},
                                 'coll':None,
                                 "rad":75,
                                 "invicible":False,
                                 'invicibleclock':None,
                                 "invicibletime": 0
                                 })

    # Initialize CrossHair Object
    gameData["entities"].append({"type": "crosshair",
                                 "location": pygame.mouse.get_pos(),
                                 "size": (100, 100),
                                 "hasMoved": False,
                                 "sprite": pygame.transform.scale(pygame.image.load("resources/crosshairs/crosshair.png").convert_alpha(), (100, 100))
                                 })

    for laser in LaserDict(read_csv("Laser.csv")):
        gameData["entities"].append(laser)
    return gameData

#### ====================================================================================================================== ####
#############                                           PROCESS                                                    #############
#### ====================================================================================================================== ####

def processstart(gameData):
    events = pygame.event.get()
    for event in events:   
        # Handle [x] Press
        if event.type == pygame.QUIT:
            gameData['isOpen'] = False
        if event.type == pygame.KEYDOWN:
            # Handle 'Escape' Key
            if event.key == pygame.K_ESCAPE:
                handleKeyEscape(gameData)
            if event.key == pygame.K_SPACE:
                gameData['state']='combat'   
    

def process(gameData):
    ''' Central Process function. Calls helper functions to handle various KEYDOWN events.
    Input: gameData Dictionary
    Output: None
    '''
    # Handle Game over or not

    events = pygame.event.get()
    for event in events:   
        # Handle [x] Press
        if event.type == pygame.QUIT:
            gameData['isOpen'] = False         
        # Handle Key Presses  in order to impletate 8-dir control and quit
        if event.type == pygame.KEYDOWN:
            # Handle 'Escape' Key
            if event.key == pygame.K_ESCAPE:
                handleKeyEscape(gameData)
            # Handle press‘ direction ' Key
            if event.key == pygame.K_a:
                handleKeyLeft(gameData)
            if event.key  == pygame.K_d:
                handleKeyRight(gameData)
            if event.key  == pygame.K_w:
                handleKeyUp(gameData)
            if event.key  == pygame.K_s:
                handleKeyDown(gameData)
        if event.type == pygame.KEYUP:
            # Handle loosen ‘ direction ' Key
            if event.key == pygame.K_a:
                looseKeyLeft(gameData)
            if event.key  == pygame.K_d:
                looseKeyRight(gameData)
            if event.key  == pygame.K_w:
                looseKeyUp(gameData)
            if event.key  == pygame.K_s:
                looseKeyDown(gameData)            
       # Handle Mouse Movement
        if event.type == pygame.MOUSEMOTION:
            handleMouseMovement(gameData)
        # Handle Mouse Click
        if event.type == pygame.MOUSEBUTTONUP:
            handleMouseClick(gameData)
    if gameData['combatTime']>=30:
        gameData['gameover']=True


#############                                           HANDLERS                                                   #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def handleMouseMovement(gameData):
    ''' Replace this and the return statement with your code '''
    for entity in gameData['entities']:
        if  entity['type']=="cannon":
            entity["isMoving"]= True
        if  entity['type']=="crosshair":
            entity["hasMoved"]= True
    return
        
def handleMouseClick(gameData):   
    ''' Replace this and the return statement with your code '''
    for entity in gameData["entities"]:
        if entity['type']== "cannonball":
            if entity['exists']==False:
                entity['exists']=True
                break
    return

def handleKeyEscape(gameData):
    ''' Handles the Escape KEYDOWN event. Sets a flag for 'isOpen' to 'False'.
    Input: gameData Dictionary
    Output: None
    '''
    gameData['isOpen'] = False


######## Press Key Handle

def handleKeyLeft(gameData):
    ''' Please replace this and the return with your code. '''
   # ("Dummy Print -> LEFT KEY(A) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['left']=True  
    return gameData

def handleKeyRight(gameData):
    ''' Please replace this and the return with your code. '''
    #("Dummy Print -> RIGHT KEY(D) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['right']=True
    return gameData

def handleKeyUp(gameData):
    ''' Please replace this and the return with your code. '''
    #("Dummy Print -> UP KEY(W) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['up']=True 
    return gameData

def handleKeyDown(gameData):
    ''' Please replace this and the return with your code. '''
    #("Dummy Print -> DOWN KEY(S) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['down']=True 
    return gameData


######## Loosen Key Handle
def looseKeyLeft(gameData):
    ''' Please replace this and the return with your code. '''
    # ("Dummy Print -> LEFT KEY(A) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['left']=False
    
    return gameData

def looseKeyRight(gameData):
    ''' Please replace this and the return with your code. '''
   # ("Dummy Print -> RIGHT KEY(D) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['right']=False
    return gameData

def looseKeyUp(gameData):
    ''' Please replace this and the return with your code. '''
    # ("Dummy Print -> UP KEY(W) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['up']=False
    return gameData

def looseKeyDown(gameData):
    ''' Please replace this and the return with your code. '''
    # ("Dummy Print -> DOWN KEY(S) PRESSED")
    for entity in gameData['entities']:
        if entity['type']=='cannon':
            entity['direction']['down']=False
    return gameData


#### ====================================================================================================================== ####
#############                                            UPDATE                      now                               #############
#### ====================================================================================================================== ####

def update(gameData):
    ''' Central Update function. Calls helper functions to update various types of Entities [crosshair, target, cannon, cannonball].
    Input: gameData Dictionary
    Output: None
    '''
    gameData['combatClock'].tick(frame_rate)
    gameData['combatTime']+=gameData['combatClock'].get_time()
    if int(gameData['combatTime']*10)/10000>45:
        gameData['state']='over'
        
#get the list of targets and lasers
    lasers=[]
    targets=[]
      # 'seg' is for for aaline detect
    for moreEntities in gameData["entities"]:
        if moreEntities["type"] == "target":
            targets.append(moreEntities)
        if moreEntities["type"] == "laser":
            if moreEntities["time"]*1000<= gameData['combatTime']:
                updatelaser(moreEntities)
                lasers.append(moreEntities)
    #print (lasers,targets)
# update entities one by one           
    for entity in gameData["entities"]:
        if entity['type'] == 'crosshair' and entity['hasMoved'] == True:
            updateCrossHair(entity)
        if entity['type'] == 'cannon' :
            updateCannon(entity,lasers,targets,gameData)
                   
        if entity['type'] == 'cannonball' and entity['exists'] == True:
            cannonEntity = None
            targetEntity = None
            for moreEntities in gameData["entities"]:
                if moreEntities["type"] == "target":
                    targetEntity = moreEntities
                elif moreEntities["type"] == "cannon":
                    cannonEntity = moreEntities
            updateCannonBall(entity, cannonEntity, targetEntity)
        if entity['type'] == 'target':# and entity['isHit'] == True:
            if entity['isHit'] == True:
                tempindex=random.randint(0,3)
                gameData["score"][tempindex]=min(100,gameData["score"][tempindex]+2)
            updateTarget(entity)
    gameData['CGPA']=CGPA(gameData)   

#############                                           HELPERS of UPDATE                                          #############
#### ---------------------------------------------------------------------------------------------------------------------- ####
      
def updateCannon(entity,lasers,targets,gameData):

#location and direction control
    if  entity['type']=="cannon":
        if entity["coll"] and entity["invicible"]==False:
            entity["invicible"]=True
            entity["invicibleclock"]=pygame.time.Clock()
        elif entity["invicible"]:
            entity["invicibleclock"].tick(frame_rate)
            entity["invicibletime"]+=entity["invicibleclock"].get_time()
            entity["coll"]=False
            print(entity["invicibletime"])
            if entity["invicibletime"]>=1000:                
                entity["invicible"]=False
                entity["coll"]=False
                entity["invicibleclock"]=None
                entity["invicibletime"]=0                         
        if entity["isMoving"]== True:
            (mousex,mousey)=pygame.mouse.get_pos()
            entity["angle"] = - (math.atan2(entity['location'][1] - mousey, entity['location'][0] - mousex)) * 180/math.pi + 270
        if  entity['direction']['left']:
            entity["location"][0]-=entity["velocity"][0]
        if entity['direction']['right']:
            entity["location"][0]+=entity["velocity"][0]
        if entity['direction']['up']:
            entity["location"][1]-=entity["velocity"][1]
        if entity['direction']['down']:
            entity["location"][1]+=entity["velocity"][1]
        entity["location"][1]=max(50,min(entity["location"][1],750))
        entity["location"][0]=max(50,min(entity["location"][0],1000))
  #  for laser in lasers:
      #  if detect_collision_line_circ(u, v):
        # consider possible collisions between the circle hitbox and each line segment
        if entity["invicible"]==False:
            entity["coll"] = False
            for laser in lasers:
                if laser['type'] == 'laser' and laser['exist'] ==True and laser['dead'] ==False:
                    #print(laser["seg"])
                    for seg in laser["seg"]:
                        # if there is any collision at all, your coresponding grade of course would be deducted
                        if detect_collision_line_circ(seg, [entity["location"], entity["rad"]]):
                            entity["coll"] = True
                            gameData['score'][laser['ltype']-1]=min(max(gameData['score'][laser['ltype']-1]-10,0)  ,100)                            
                            break
        
        return

def updatelaser(laser):
    if  laser['type']=="laser":
        laser['exist']=True
        laser['seg']=[]
        laser["ini_angle"]+= laser["va"]
        if laser["va"]>0:
            if laser["ini_angle"] >=laser["death_angle"]:
                laser['dead']=True
        elif laser["va"]<0:
            if laser["ini_angle"] <=laser["death_angle"]:
                laser['dead']=True
        sol_x = laser["ori"][0] + math.cos(math.radians(laser["ini_angle"])) * window_wid * laser["len1"][0]
        sol_y = laser["ori"][1] + math.sin(math.radians(laser["ini_angle"])) * window_wid * laser["len1"][0]

        # ...and the end of the line...
        eol_x = laser["ori"][0] + math.cos(math.radians(laser["ini_angle"])) * window_wid * laser["len1"][1]
        eol_y = laser["ori"][1] + math.sin(math.radians(laser["ini_angle"])) * window_wid * laser["len1"][1]


                    # compute the start of the line...
        sol_x2 = laser["ori"][0] + math.cos(math.radians(laser["ini_angle"])) * window_wid * laser["len2"][0]
        sol_y2 = laser["ori"][1] + math.sin(math.radians(laser["ini_angle"])) * window_wid * laser["len2"][0]

        # ...and the end of the line...
        eol_x2 = laser["ori"][0] + math.cos(math.radians(laser["ini_angle"])) * window_wid * laser["len2"][1]
        eol_y2 = laser["ori"][1] + math.sin(math.radians(laser["ini_angle"])) * window_wid * laser["len2"][1]        
                # ...and then add that line to the list
        laser["seg"].append( [[int(sol_x), int(sol_y)], [int(eol_x), int(eol_y)],laser['ltype']] )
        laser["seg"].append( [[int(sol_x2), int(sol_y2)], [int(eol_x2), int(eol_y2)],laser['ltype']] )

    

def updateCrossHair(entity):
        if entity["hasMoved"]== True:
            (mousex,mousey)=pygame.mouse.get_pos()
            entity["location"]=[mousex,mousey]




def detect_collision_line_circ(u, v):

	# unpack u; a line is an ordered pair of points and a point is an ordered pair of co-ordinates
	[u_sol, u_eol, l] = u
	[u_sol_x, u_sol_y] = u_sol
	[u_eol_x, u_eol_y] = u_eol

	# unpack v; a circle is a center point and a radius (and a point is still an ordered pair of co-ordinates)
	[v_ctr, v_rad] = v
	[v_ctr_x, v_ctr_y] = v_ctr

	# the equation for all points on the line segment u can be considered u = u_sol + t * (u_eol - u_sol), for t in [0, 1]
	# the center of the circle and the nearest point on the line segment (that which we are trying to find) define a line 
	# that is is perpendicular to the line segment u (i.e., the dot product will be 0); in other words, it suffices to take
	# the equation v_ctr - (u_sol + t * (u_eol - u_sol)) · (u_evol - u_sol) and solve for t
	
	t = ((v_ctr_x - u_sol_x) * (u_eol_x - u_sol_x) + (v_ctr_y - u_sol_y) * (u_eol_y - u_sol_y)) / ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2)

	# this t can be used to find the nearest point w on the infinite line between u_sol and u_sol, but the line is not 
	# infinite so it is necessary to restrict t to a value in [0, 1]
	t = max(min(t, 1), 0)
	
	# so the nearest point on the line segment, w, is defined as
	w_x = u_sol_x + t * (u_eol_x - u_sol_x)
	w_y = u_sol_y + t * (u_eol_y - u_sol_y)
	
	# Euclidean distance squared between w and v_ctr
	d_sqr = (w_x - v_ctr_x) ** 2 + (w_y - v_ctr_y) ** 2
	
	# if the Eucliean distance squared is less than the radius squared
	if (d_sqr <= v_rad ** 2):
	
		# the line collides
		return True  # the point of collision is (int(w_x), int(w_y))
		
	else:
	
		# the line does not collide
		return False

	# visit http://ericleong.me/research/circle-line/ for a good supplementary resource on collision detection\
def updateCannonBall(entity, cannonEntity, targetEntity):  #now
    ''' Replace this and the return statement with your code '''

    if entity['type']== "cannonball":
        if entity['destroy']==True:
            entity['location']=cannonEntity['location']
            entity['velocity']=None
            entity['reload']= False
        if entity['reload']==True:
            entity['location']=cannonEntity['location']
            entity['velocity']=None
            entity['destroy']= False
            entity['exists']= False
            entity['reload']= False
        if entity['velocity']==None:
            (mousex,mousey)=pygame.mouse.get_pos()
            entity['location']=[cannonEntity['location'][0],cannonEntity['location'][1]]
            angle= math.atan2(entity['location'][1]- mousey, entity['location'][0] - mousex)
            entity['velocity']=[-15*math.cos(angle),-15*math.sin(angle)]
        else :
            if entity['location'][0]>1200 or entity['location'][1]>800 or  entity['location'][0]<0 or entity['location'][1]<0:
                entity['destroy']=True
            elif (entity['location'][0]+int(0.5*entity['size'][0])-targetEntity['location'][0]- int(0.5*targetEntity['size'][0]))**2+(entity['location'][1]+int(0.5*entity['size'][1])-targetEntity['location'][1]- int(0.5*targetEntity['size'][1]))**2<=(int(0.5*entity['size'][1])+int(0.5*targetEntity['size'][1]))**2:
                targetEntity['isHit']=True
                entity['reload']=True
            else:
                entity['velocity'][1]+=0.03
                entity['location'][0]+=entity['velocity'][0]
                entity['location'][1]+=entity['velocity'][1]
    return


def updateTarget(entity):
    ''' Replace this and the return statement with your code '''
    if entity['type']== "target":
        #clocktar = pygame.time.Clock()
        if  entity['isHit']==True:
            entity['location']=[1200, random.randint(200, 600)]
            entity['sprite']=pygame.transform.scale(pygame.image.load("resources/targets/target_{}.png".format(random.randint(1, 4))).convert_alpha(), (88, 88))
            entity['isHit']=False
            entity['isDisappear']=False
            entity['clock']=0
        elif entity['isDisappear']==True:
            entity['location']=[1200, random.randint(200, 600)]
            entity['sprite']=pygame.transform.scale(pygame.image.load("resources/targets/target_{}.png".format(random.randint(1, 4))).convert_alpha(), (88, 88))
            entity['isHit']=False
            entity['isDisappear']=False
            entity['clock']=0
        else:
            if entity['location'][0]<0:# entity['clock']>=400:
                entity['isDisappear']=True            
            else:
                entity['location'][0]-=3
                #clocktar.tick(400)
                #entity['clock']+=clocktar.get_time()
    return
#Calculate your CGPA
def CGPA(gameData):
    sum1=0
    for grade in gameData['score']:
        sum1+=grade
    avg=sum1/4
    for GP in GPAcalculator:
        if GP[3]<=avg<GP[2]:
            return GP[0]


#### ====================================================================================================================== ####
#############                                            RENDER                                                    #############
#### ====================================================================================================================== ####

	
def game_loop_render(gameData):
        gameData["screen"].blit(gameData["background"], (0, 0))
        ammo=[]
        # clear the window surface (by filling it with black)
        # draw each of the rotating line segments
        for entity in gameData["entities"]:
            if entity['type'] == 'laser' and entity['exist'] ==True and entity['dead'] ==False:
                for seg in entity["seg"]:
                    renderlaser(seg,gameData)
            if entity['type'] == 'cannon':
                renderCannon(gameData, entity)

            elif entity['type'] == 'cannonball':
                renderCannonBall(gameData, entity)
                if entity['exists'] ==True :
                    ammo.append(entity)             
            elif entity['type'] == 'target':
                renderTarget(gameData, entity)

            elif entity['type'] == 'crosshair':
                renderCrossHair(gameData, entity)
        rendertime(gameData)
        if gameData["screen"]!=None:
            renderscore(gameData)
        renderAmmo(gameData, ammo)
 # update the display
        pygame.display.update()



#############                                           HELPERS  of the RENDER                                      #############
#### ---------------------------------------------------------------------------------------------------------------------- ####

def renderlaser(seg,gameData):
    #pygame.draw.aaline(gameData["screen"], (255, 255, 255), seg[0], seg[1])
    coursefont=pygame.font.Font(None,30)
    if seg[2]==1:
        pygame.draw.polygon(gameData["screen"],red,[[seg[0][0]+10,seg[0][1]+10],[seg[0][0]-10,seg[0][1]-10],[seg[1][0]-10,seg[1][1]-10],[seg[1][0]+10,seg[1][1]+10]], 0)
        score3text=coursefont.render("1405DUE:",1,grey)
    elif seg[2]==2:
        pygame.draw.polygon(gameData["screen"],green,[[seg[0][0]+10,seg[0][1]+10],[seg[0][0]-10,seg[0][1]-10],[seg[1][0]-10,seg[1][1]-10],[seg[1][0]+10,seg[1][1]+10]], 0)
        score3text=coursefont.render("1406DUE:",1,grey)
    elif seg[2]==3:
        pygame.draw.polygon(gameData["screen"],blue,[[seg[0][0]+10,seg[0][1]+10],[seg[0][0]-10,seg[0][1]-10],[seg[1][0]-10,seg[1][1]-10],[seg[1][0]+10,seg[1][1]+10]], 0)
        score3text=coursefont.render("1501DUE:",1,grey)
    else:
        pygame.draw.polygon(gameData["screen"],white,[[seg[0][0]+10,seg[0][1]+10],[seg[0][0]-10,seg[0][1]-10],[seg[1][0]-10,seg[1][1]-10],[seg[1][0]+10,seg[1][1]+10]], 0)
        score3text=coursefont.render("1805DUE:",1,grey)
    gameData["screen"].blit(score3text, [(seg[0][0]+seg[1][0])/2, (seg[0][1]+seg[0][1])/2])
    
def renderscore(gameData):
    scorefont=pygame.font.Font(None,30)
    #get the color of the entity
    colorinfo=(150,100,0)
    #draw the name of socre	
    score1text=scorefont.render("Your Grades:                  CGPA:{}  ".format(gameData['CGPA']),1,colorinfo)
    score2text1=scorefont.render("COMP1405:{}".format(gameData['score'][0]),1,red)
    score2text2=scorefont.render('COMP1406:{}'.format(gameData['score'][1]),1,green)
    score2text3=scorefont.render('COMP1501:{}'.format(gameData['score'][2]),1,blue)
    score2text4=scorefont.render('COMP1805:{}'.format(gameData['score'][3]),1,white)                     
    score3text=scorefont.render("Your Hair:",1,colorinfo)
    gameData["screen"].blit(score1text, (50, 50))
    gameData["screen"].blit(score2text1, (10, 80))
    gameData["screen"].blit(score2text2, (200, 80))
    gameData["screen"].blit(score2text3, (400, 80))
    gameData["screen"].blit(score2text4, (600, 80))
    gameData["screen"].blit(score3text, (50, 650))
    pygame.display.update()
def rendertime(gameData):
    timefont=pygame.font.Font(None,30)
    #get the color of the entity
    colorinfo=(250,100,0)
    #draw the name of socre	
    timetext=timefont.render("TIME: {}s".format( int(gameData['combatTime']*10)/10000),1,colorinfo)
    gameData["screen"].blit(timetext, (1000, 50))
def renderTarget(gameData, entity):
    ''' Replace this and the return statement with your code '''
    if entity['type']== "target":
        scorefont=pygame.font.Font(None,20)
        score2text1=scorefont.render("Rob's Notes",1,blue)
        gameData["screen"].blit(entity["sprite"],entity["location"])
        gameData["screen"].blit(score2text1,[entity["location"][0]+10,entity["location"][1]+88])
    return

def renderCrossHair(gameData, entity):
    ''' Replace this and the return statement with your code '''
    if entity['type']== "crosshair":
        gameData["screen"].blit(entity["sprite"],[entity["location"][0]-entity["sprite"].get_size()[0],entity["location"][1]-entity["sprite"].get_size()[1]])
    return

def renderCannon(gameData, entity):         
    rotated_image = pygame.transform.rotate(entity["sprite"], entity['angle'])
    new_size=rotated_image.get_size()
    newx=entity["location"][0]-int(0.5*new_size[0])
    newy=entity["location"][1]-int(0.5*new_size[1])
    if entity['invicible']:
        pygame.draw.circle(gameData["screen"], (255, random.randint(0,100), 0), entity["location"],entity['rad'])
        gameData["screen"].blit(pygame.Surface.convert_alpha(rotated_image) ,[newx,newy])       
    else:
        gameData["screen"].blit(rotated_image ,[newx,newy])
    return

def renderCannonBall(gameData, entity):  
    ''' Replace this and the return statement with your code ''' 
    if entity['type']== "cannonball":
        if entity['exists']==True:
            gameData["screen"].blit(entity["sprite"],entity["location"])
    return

def renderAmmo(gameData, ammoList):
    ''' Replace this and the return statement with your code '''
    for i in range(12-len(ammoList)):
        gameData["screen"].blit(gameData["ammo"],[100+i*40,700])
    return
def renderGameOver(gameData):
    ''' Replace this and the return statement with your code '''
    if gameData['state']== 'over':
        scorefont=pygame.font.Font(None,40)
        gameData["screen"].blit(gameData["OVER"],(0,0))
        overfont=pygame.font.Font(None,100)
        Ocolor=(250,10,0)
        #draw the name of socre	
        score1text=scorefont.render("Your Grades:       CGPA:{}".format(gameData['CGPA']),1,Ocolor)
        score2text1=scorefont.render("COMP1405:{}".format(gameData['score'][0]),1,red)
        score2text2=scorefont.render('COMP1406:{}'.format(gameData['score'][1]),1,green)
        score2text3=scorefont.render('COMP1501:{}'.format(gameData['score'][2]),1,blue)
        score2text4=scorefont.render('COMP1805:{}'.format(gameData['score'][3]),1,white)                     
        gameData["screen"].blit(score1text, (350, 450))
        gameData["screen"].blit(score2text1, (450, 500))
        gameData["screen"].blit(score2text2, (450, 550))
        gameData["screen"].blit(score2text3, (450, 600))
        gameData["screen"].blit(score2text4, (450, 650))
        overtext=overfont.render("First Year Transcript",1,Ocolor)
        gameData["screen"].blit(overtext, (200,200))
        pygame.display.update()
def renderGamestart(gameData):
    if gameData['state']== 'start':
        scorefont=pygame.font.Font(None,30)
        scorefont2=pygame.font.Font(None,66)
        gameData["screen"].blit(gameData["START"],(0,0))
        overfont=pygame.font.Font(None,88)
        Ocolor=(random.randint(100,250),10,random.randint(100,250))
        Ocolor2=(255,200,random.randint(100,250))
        #draw the name of socre	
        score1text=scorefont2.render("Press SPACE to Start:  ",1,Ocolor2)
        score2text1=scorefont.render("Press W to move upward",1,white)
        score2text2=scorefont.render('Press S to move downward',1,white)
        score2text3=scorefont.render('Press A to move to left',1,white)
        score2text4=scorefont.render('Press D to move to right',1,white)                     
        gameData["screen"].blit(score1text, (320, 450))
        gameData["screen"].blit(score2text1, (110, 600))
        gameData["screen"].blit(score2text2, (110, 650))
        gameData["screen"].blit(score2text3, (110, 700))
        gameData["screen"].blit(score2text4, (110, 750))
        overtext=overfont.render("Survival Guide for B.C.S Freshmen",1,Ocolor)
        gameData["screen"].blit(overtext, (60,200 ))
        pygame.display.update()
#### ====================================================================================================================== ####
#############                                             MAIN                                                     #############
#### ====================================================================================================================== ####
	

def main():
    # initialize pygame
    pygame.init()

   #####################################################################################################
    # these are the initial game objects that are required (in some form) for the core mechanic provided
    #####################################################################################################
    DATA = initialize()
    
    """
    menu = pygame.image.load('menu.png')
    rank = pygame.image.load('rank.png')
    instuction= pygame.image.load('instuction.png')
    disc = pygame.image.load("disclaimer.png")
    """


    # create the window and set the caption of the window
    pygame.display.set_caption("Survial Guide for B.C.S.")
    # create a clock
    clock = pygame.time.Clock()

    # this is the initial game state
    
    pygame.mixer.music.load('resources/Space Sprinkles_0.mp3')
    pygame.mixer.music.play(-1)
    while DATA['isOpen'] :
        if DATA['state']=='over':
            process(DATA)
            renderGameOver(DATA)
        elif DATA['state']=='combat':  
                    
        #####################################################################################################
        # Process loop
        #####################################################################################################

            process(DATA)

        #####################################################################################################
        # this is the "update" phase of the game loop, where the changes to the game world are handled
        #####################################################################################################
            update(DATA)                   

        #####################################################################################################
        # this is the "render" phase of the game loop, where a representation of the game world is displayed
        #####################################################################################################
            game_loop_render(DATA)
        elif DATA['state']=='start'  :
            processstart(DATA)
            renderGamestart(DATA)

        # enforce the minimum frame rate



        
    pygame.quit()
            
		
if __name__ == "__main__":
	main()
