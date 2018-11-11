from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import colorList
import time

maze_width = 15#15
maze_height = 15#15
ball_color = 'blue'#
extra_color = 'cyan'#
bg_color = 'green'#
filename='newmaze.png'#newmaze.png
startx = 0
starty = 0
endx = 14
endy = 14

def get_rid_of_color(frame):
    print('Analysing color')
    img = frame
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)#HSV空间
    mask=cv2.inRange(hsv,color_dict[bg_color][0],color_dict[bg_color][1])#cheng色
    mask2=cv2.inRange(hsv,color_dict[ball_color][0],color_dict[ball_color][1])
    mask3=cv2.inRange(hsv,color_dict[extra_color][0],color_dict[extra_color][1])
    mask = mask + mask2 + mask3 #color of the path, ball and extra color
    #cv2.imshow('img',mask)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    cv2.bitwise_not(mask,mask)
    return mask
    #red=cv2.bitwise_and(img,img,mask=red_mask)#对原图像处理
    #res=red
    #cv2.imshow('img',red_mask)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

def mazeMatrix(maze):
    res=cv2.resize(maze,(maze_width,maze_height),interpolation=cv2.INTER_CUBIC)
    
    for i in range(0,maze_width):
        for j in range(0,maze_height):
            if res[i][j] > 150:
                res[i][j] = 1
            else:
                res[i][j] = 0
    return res

def get_ball_color(frame):
    print('Locating ball')
    img = frame
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)#HSV空间
    mask2=cv2.inRange(hsv,color_dict[ball_color][0],color_dict[ball_color][1])
    mask3=cv2.inRange(hsv,color_dict[extra_color][0],color_dict[extra_color][1])
    mask = mask2 + mask3 #color of the ball and extra color
    cv2.bitwise_not(mask,mask)
    return mask

def ballMatrix(ball):
    res=cv2.resize(ball,(maze_width,maze_height),interpolation=cv2.INTER_CUBIC)
    
    for i in range(0,maze_width):
        for j in range(0,maze_height):
            if res[i][j] == 0:
                return i,j
            else:
                pass
    return False
    

#BFS algorithm
class node:
    def __init__(self, x=0, y=0, t=0):
        self.x = x
        self.y = y
        self.t = t #t表示走到这个格子用的步数
 
class father:
    def __init__(self, x=0, y=0, cz=[]):
        self.x = x #当前格子的父节点坐标
        self.y = y
        self.cz = cz #由什么操作到达的这个格子
 
vis = []
for i in range(0, maze_width):
    vis += [[]]
    for j in range(0, maze_height):
        vis[i] += [False]
 
lj = []
for i in range(0, maze_width):
    lj += [[]]
    for j in range(0, maze_height):
        lj[i] += [father()]
 
xx =[1,0,0,-1]                          #下、右、左、上
yy =[0,1,-1,0]
q = []
s = node() 
 
def bfs(mmap):
    print('Calculating path')
    if mmap[startx][starty] == 1 or mmap[endx][endy] == 1:
        return False
    n = maze_width
    m = maze_height
    s.x = startx
    s.y = starty
    s.t = 0

    q.append(s)
    lj[s.x][s.y].x = 0
    lj[s.x][s.y].y = 0
    lj[s.x][s.y].cz = 0
    vis[s.x][s.y] = True    #标为已经访问过
    #print("vis={}".format(vis))
    while q:
        now = q[0]
        q.pop(0)
        for i in range(0, 4):
            new = node()
            new.x = now.x + xx[i]
            new.y = now.y + yy[i]
            new.t = now.t + 1
            #print("i={} new.x={} new.y={} now.x={} now.y={}".format(i, new.x, new.y, now.x, now.y))
            #print("new.x ={} new.y={} n={} m={} vis[new.x][new.y]={} mmap[new.x][new.y]={}".format(new.x, new.y, n, m, vis[new.x][new.y], mmap[new.x][new.y]))
            if new.x < 0 or new.y < 0 or new.x >= n or new.y >= m or vis[new.x][new.y] == True or mmap[new.x][new.y] == 1:  # 下标越界或者访问过或者是障碍物
                continue
 
            q.append(new)
            lj[new.x][new.y].x = now.x
            lj[new.x][new.y].y = now.y
            if i == 0:
                lj[new.x][new.y].cz = 'D'
            elif i == 1:
                lj[new.x][new.y].cz = 'R'
            elif i == 2:
                lj[new.x][new.y].cz = 'L'
            elif i == 3:
                lj[new.x][new.y].cz = 'U'
            vis[new.x][new.y] = True
            #print("value={} ({},{}) {}\n".format(mmap[new.x][new.y], new.x, new.y, lj[new.x][new.y].cz))
            #print("=============================================================")
            if new.x == endx and new.y == endy:
                return new.t                         #到达终点
    return False
ans_lj = []
def dfs(x, y):
    if x == startx and y == starty: return
    else: dfs(lj[x][y].x,lj[x][y].y)
    #print(lj[x][y].cz)
    #print(lj[x][y].x,lj[x][y].y)
    ans_lj.append(lj[x][y].cz)

def moveMotors():
    count = 1
    for i in range(0,len(ans_lj)):#←↑→↓
        if ans_lj[i] == 'U':
            if i+1 == len(ans_lj):
                print('↑ ',count,' times')
                break
            if ans_lj[i+1] == ans_lj[i]:
                count += 1
            else:
                print('↑ ',count,' times')#Move up
                count = 1
        if ans_lj[i] == 'D':
            if i+1 == len(ans_lj):
                print('↓ ',count,' times')
                break
            if ans_lj[i+1] == ans_lj[i]:
                count += 1
            else:
                print('↓ ',count,' times')#Move down
                count = 1
        if ans_lj[i] == 'L':
            if i+1 == len(ans_lj):
                print('← ',count,' times')
                break
            if ans_lj[i+1] == ans_lj[i]:
                count += 1
            else:
                print('← ',count,' times')#Move left
                count = 1
        if ans_lj[i] == 'R':
            if i+1 == len(ans_lj):
                print('→ ',count,' times')
                break
            if ans_lj[i+1] == ans_lj[i]:
                count += 1
            else:
                print('→ ',count,' times')#Move right
                count = 1
 
if __name__ == '__main__':
    cost = time.time()
    color_dict = colorList.getColorList() 
    frame = cv2.imread(filename,1)
    maze = get_rid_of_color(frame)#create maze graph
    res = mazeMatrix(maze)#resize maze

    ball = get_ball_color(frame)#get ball
    ball_maze = mazeMatrix(ball)
    bx,by = ballMatrix(ball_maze)#find ball coord
    print('The coord of ball is',bx,by)
    
    #res[6][0]=1
    #res[6][1]=1
    ans = bfs(res)
    if ans == False: print("No way to get out of this maze")
    else:
        print('There are',ans,'steps to get out')
        dfs(endx, endy)
        #print("迷宫行走方式{}".format(ans_lj))

    moveMotors()    
    print("Total time cost:",time.time()-cost)
    #cv2.imshow('name',cv2.resize(maze, (380 ,380)))
    #cv2.imshow('name',cv2.resize(ball, (380 ,380)))
