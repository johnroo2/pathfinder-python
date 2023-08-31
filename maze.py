import pygame
import random
from alive_progress import alive_bar

pygame.display.set_caption("Pathfinder")

class Maze:

    TILE_SIZE = 15
    DEPTH = 6
    X = 40
    Y = 40
    FILL = 0.25
    
    def __init__(self):

        self.x = Maze.X
        self.y = Maze.Y
        self.tile_cap = self.x * self.y + 1
        self.grid = [[0 for _ in range(self.y)] for _ in range(self.x)]

        self.surface = pygame.display.set_mode((Maze.TILE_SIZE * self.x, Maze.TILE_SIZE * self.y))
        self.clock = pygame.time.Clock()
        self.run = True
        self.fill(Maze.FILL)
        self.get = lambda coords: self.grid[coords[0]][coords[1]]
        self.inbounds = lambda coords: coords[0] >= 0 and coords[0] < self.x and coords[1] >= 0 and coords[1] < self.y and self.get(coords) != 1

        self.surface.fill((255, 255, 255))

        self.colourmap = {
            0:(255, 255, 255),
            1:(125, 125, 125),
            2:(200, 220, 240),
            3:(100, 160, 200)
        }

    def fill(self, fill):
        for i in range(self.x):
            for j in range(self.y):
                if random.random() < fill:
                    self.grid[i][j] = 1
        for i in range(0, 3):
            for j in range(0, 3):
                self.grid[i][j] = 0
                self.grid[self.x-1-i][self.y-1-j] = 0

        #print(self.grid)

    def pathfind_two_coords(self, coords, dest_coords, max = -1, path = []):
        if not self.inbounds(dest_coords) or not self.inbounds(coords) or len(set(path)) < len(path) or (max > -1 and len(path) >= max):
            return (self.tile_cap, path)
        
        if coords == dest_coords: #ARRIVE
            if max == -1: max = len(path)
            elif len(path) < max: max = len(path)  
            return (len(path), path)
        
        right = self.pathfind_two_coords((coords[0] + 1, coords[1]), dest_coords, max, path + [(coords[0] + 1, coords[1])])
        down = self.pathfind_two_coords((coords[0], coords[1] + 1), dest_coords, max, path + [(coords[0], coords[1] + 1)])
        left = self.pathfind_two_coords((coords[0] - 1, coords[1]), dest_coords, max, path + [(coords[0] - 1, coords[1])])
        up = self.pathfind_two_coords((coords[0], coords[1] - 1), dest_coords, max, path + [(coords[0], coords[1] - 1)])
            
        return sorted([up, left, down, right], key=lambda t: t[0])[0]
    
    def pathfind(self):
        memos = {(0, 0):[(0, 0)]}
        self.grid[0][0] = 2

        with alive_bar(int((self.x + self.y) * (self.x + self.y + 1) * 0.5) - 1) as bar:    
            for width in range(1, self.x + self.y):
                for double_backoffset in range(0, width-1):
                    destroy_tuple = (double_backoffset, width-double_backoffset-2)
                    if destroy_tuple in memos: del memos[destroy_tuple]
                for offset in range(0, width + 1):
                    bar()
                    self.draw()

                    center_coords = (offset, width-offset)
                    if not self.inbounds(center_coords): continue
                    evals = []
                    for spot in [(back_offset, width-1-back_offset) for back_offset in range(0, width)]:
                        if spot in memos and memos[spot] == "invalid": continue
                        if not self.inbounds(spot): continue
                        pathfind = self.pathfind_two_coords(spot, center_coords, max = Maze.DEPTH + len(memos[spot]), path=memos[spot])
                        if pathfind[0] == self.tile_cap: continue
                        evals.append(pathfind)
                    sortlist = sorted(evals, key=lambda p: p[0])

                    if len(sortlist) > 0: 
                        memos[center_coords] = sortlist[0][1]
                    else: 
                        if not self.inbounds(center_coords):
                            memos[(self.x-1, self.y-1)] = "invalid"
                            break
                        else:
                            memos[center_coords] = "invalid"
                    #print(f"SETTING: {center_coords} -> {memos[center_coords]}")
                    if memos[center_coords] != "invalid" and len(memos[center_coords]) < self.tile_cap: 
                        self.grid[offset][width-offset] = 2
                else: 
                    if width + 1 < self.x + self.y:
                        for offset in range(0, width + 1):
                            center_coords = (offset, width-offset)
                            if center_coords in memos: break
                        else:
                            memos[(self.x-1, self.y-1)] = "invalid"
                            break
                        continue
                break
            return memos

    def draw(self):
        self.surface.fill((255, 255, 255))
        #self.clock.tick(200)
        
        for i in range(self.x): 
            for j in range(self.y):
                #border base
                pygame.draw.rect(self.surface, (0, 0, 0), (i * Maze.TILE_SIZE, j * Maze.TILE_SIZE, Maze.TILE_SIZE, Maze.TILE_SIZE))
                #main 
                pygame.draw.rect(self.surface, self.colourmap.get(self.grid[i][j]), (i * Maze.TILE_SIZE + 1, j * Maze.TILE_SIZE + 1, Maze.TILE_SIZE - 1, Maze.TILE_SIZE - 1))
            

        pygame.display.update()

    def init_game(self):

        self.draw()
        steps = self.pathfind().get((self.x-1, self.y-1))
        print(f"PATH: {steps}" if steps != "invalid" else "NOT POSSIBLE")
        if steps != "invalid":
            for point in steps:
                self.grid[point[0]][point[1]] = 3

        while self.run:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    pygame.quit()
                    quit()  

main_maze = Maze()