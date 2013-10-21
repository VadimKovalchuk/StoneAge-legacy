import sys
import pygame
from pygame.locals import *


#CONSTANTS
#Uplading constants from setup.ini file
from source import mapprocessing, controls, scenario, loader, tools

constants = tools.importConstants()
'___________________________________________________________'
#Set up window resolution
WINDOW_WIDTH    = constants['WINDOW_WIDTH']     #Default 1280
WINDOW_HEIGHT   = constants['WINDOW_HEIGHT']    #Default 720
FPS             = constants['FPS']              #Default 40
#Number of cells by X and Y axises
LAND_NUM_Y      = constants['LAND_NUM_Y']       #Default 4
LAND_NUM_X      = constants['LAND_NUM_X']       #Default 6
#Side(control) panel and game field width
SIDE_PANEL_WIDTH= constants['SIDE_PANEL_WIDTH'] #Calculated
FIELD_WIDTH     = constants['FIELD_WIDTH']      #Calculated
#Cell width and height
LAND_CELL_HEIGHT= constants['LAND_CELL_HEIGHT'] #Calculated
LAND_CELL_WIDTH = LAND_CELL_HEIGHT
del constants
'___________________________________________________________'

def main():
    # set up pygame
    pygame.init()
    ScreenSurface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
    pygame.display.set_caption('Stone Age')
    mainClock = pygame.time.Clock()

    #BUILDING MAIN CLASSES
    #Loading images and (sounds not implemented)
    Loader= loader.Loader()
    #Defining event set and story line
    Scenario = scenario.Scenario('free.scn')
    #Building map
    Map = mapprocessing.Map(ScreenSurface, Scenario, Loader)
    #Defining side menu
    SideMenu = controls.SideMenu(ScreenSurface,Map, Loader)
    #Drawing clear landscape
    Map.blit_map()
    '_________________________________________________________________'
    'PATH FINDER SANDBOX'

    #Map.PathFinder.get_path((1,1),(2,3))
    #Map.PathFinder.get_path((1,1),(4,0))
    #Map.PathFinder.get_path((2,1),(2,3))
    #print(Map.PathFinder.path_collection)

    def gloryCircle(Tribesman):
        Tribesman.setLocation((3,0))
        waypoints = [(2,0),(1,1),(1,2),(2,3),(3,3),(4,2),(4,1),(3,0)]
        Tribesman.travel(waypoints)

    def gloryCircle2(Tribesman):
        Tribesman.setLocation((1,1))
        waypoints = [(2,0),(1,0),(0,0),(0,1),(0,2),(1,3),(2,3),(3,3),(4,3),(5,2)
                     ,(5,1),(5,0),(4,0),(4,1),(3,1),(2,1),(1,1)]
        Tribesman.travel(waypoints)

    '_________________________________________________________________'

    tribe_name = ['Gabonga','CPU1','CPU2','CPU3']
    count = 0
    for Tribe in Map.tribes:
        Tribe.add_tribesman("Oku")
        Tribe.add_tribesman("Buba")
        Tribe.add_tribesman("Cora")
        Tribe.add_tribesman("Garu")
        Tribe.add_tribesman("Okupa")
        # 5
        Tribe.add_tribesman("Timb")
        Tribe.add_tribesman("Dema")
        Tribe.add_tribesman("Hala")
        Tribe.add_tribesman("Kibo")
        Tribe.add_tribesman("Moz")
        # 10
        Tribe.add_tribesman("Zev")
        Tribe.add_tribesman("Aka")
        Tribe.add_tribesman("Lem")
        Tribe.add_tribesman("Nurg")
        Tribe.add_tribesman("Pela")
        Tribe.name = tribe_name[count]
        count += 1


    five_seconds = pygame.time.get_ticks()
    #tools.drawNet(ScreenSurface)

    while True:
        # check for the QUIT event

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONUP:
                SideMenu.mouseInput(pygame.mouse.get_pos())
        '''
        # Vaiting for 5 seconds to add one more tribesman
        if (pygame.time.get_ticks() - five_seconds) >= 1000 :
            five_seconds = pygame.time.get_ticks()
            for meeple in Camp.population:
                if meeple.visible == False:
                    gloryCircle2(meeple)
                    Map.active_sprites.append(meeple)
                    break
        '''
        #Performing game flow and changing game state
        Map.flow()

        # Restoring empty Landscape without animated sprites
        Map.clear_map()

        # Calculating changes in sprite frames
        Map.process_sprites()

        #Drawing new sprites. Side menu update if nescesary
        Map.blit_sprites()
        if SideMenu.update == True:
            SideMenu.blit_all()

        #UPDATING SCREEN
        pygame.display.update()
        mainClock.tick(FPS)

if __name__ == '__main__':
    main()