import sys
import pygame
from pygame.locals import *

#CONSTANTS
#Uplading constants from setup.ini file
from source import core, controls, scenario, loader, tools, items

constants = tools.Constants()
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

    tools.db_backup()
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
    Core = core.Core(ScreenSurface, Scenario, Loader)
    #Defining side menu
    Controls = controls.Controls(ScreenSurface, Core, Loader)
    #Drawing clear landscape
    Core.blit_map()

    tribe_name = ['Gabonga','CPU1','CPU2','CPU3']
    count = 0
    for Tribe in Core.tribes:
        Tribe.add_tribesman("Oku")
        Tribe.add_tribesman("Buba")
        Tribe.add_tribesman("Cora")
        Tribe.add_tribesman("Garu")
        Tribe.add_tribesman("Okupa")
        # 5
        '''Tribe.add_tribesman("Timb")
        Tribe.add_tribesman("Dema")
        Tribe.add_tribesman("Hala")
        Tribe.add_tribesman("Kibo")
        Tribe.add_tribesman("Moz")
        # 10
        Tribe.add_tribesman("Zev")
        Tribe.add_tribesman("Aka")
        Tribe.add_tribesman("Lem")
        Tribe.add_tribesman("Nurg")
        Tribe.add_tribesman("Pela")'''
        '''
        for i in range(1,6):
            Tribe.population[i - 1].add_item(items.Item(7))#i + 2
        '''
        Tribe.name = tribe_name[count]
        count += 1
        #
        '''
        item_lst = []
        catalog = tools.all_items_catalog()
        for category in catalog:
            item_lst.extend(catalog[category])
        print(len(item_lst), 'items are imported')
        for item in item_lst:
            Tribe.inventory.append(items.Item(item))
        '''
        #


    while True:
        # check for the QUIT event
        for event in pygame.event.get():
            if event.type == QUIT:
                Core.Logger.finalize()
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONUP:
                Controls.mouseInput(pygame.mouse.get_pos())

        if not Controls.pause:
        #Performing game flow and changing game state
            Core.flow()

        # Restoring empty Landscape without animated sprites

            Core.clear_map()

        # Calculating changes in sprite frames
            Core.process_sprites()

        #Drawing new sprites
            Core.blit_sprites()

        #Updates controls
        Controls.refresh()

        #UPDATING SCREEN
        pygame.display.update()
        mainClock.tick(FPS)

if __name__ == '__main__':
    main()