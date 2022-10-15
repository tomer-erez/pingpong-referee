import numpy as np
import cv2

class BALL:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vertical_direction = None  # up/down/none
        self.horizontal_direction = None  # right/left/none
        self.queue_length=9
        self.location_queue = self.queue_length * [(0,0,0)]  # x,y,frame_number

    def update_location_queue(self, cor,frame_number,game):
        """
        :param cor:
        :param frame_number:
        :return:
        """
        self.x = cor[0] + cor[2] // 2  # where ball was located at the last frame
        self.y = cor[1] + cor[3]  # where ball was located at the last frame
        if cor[0]!=0 and cor[1]!=0:
            self.location_queue.pop(0)  # pop the item that was inserted first
            self.location_queue.append((self.x, self.y,frame_number))  # append to the end of the array
            if game.live_ball:
                game.point.update_hitter(self)
                print("change of direction: frame ",frame_number)

        else:
            print("no detection in this image")

        print("frame number:", frame_number)
        print("Live ball=",game.live_ball)
        print(self.location_queue)



    def in_left_table(self, table,cor):
        """ a little room to spare bcuz of how 60 fps could miss the balls that are above the table but close to it
        or right near it, from the left or right"""

        if cor[0] < table.left_BL[0]-table.x_factor or cor[0]>table.left_BR[0] or cor[1]>table.left_BR[1]+table.y_factor or cor[1]<table.left_TR[1]-table.y_factor:
            print("out of the rectangle that closes the trapez")
            return False

        elif table.left_TR[1]-table.y_factor< cor[1]<table.left_BR[1]+table.y_factor:  #y in range
            edge_x=(table.image_height- cor[1]-table.left_intercept)/table.left_slope   # the table "edge x" for this y of the ball
            if  cor[0]<edge_x-table.x_factor:

                return False

        return True  #in


    def in_right_table(self, table,cor):
        """ a little room to spare bcuz of how 60 fps could miss the balls that are above the table but close to it
        or right near it, from the left or right"""

        if cor[0] < table.right_BL[0] or cor[0]>table.right_BR[0]+table.x_factor or cor[1]>table.right_BR[1]+table.y_factor or cor[1]<table.right_TR[1]-table.y_factor:
            print("out of the rectangle that closes the trapez")
            return False
        elif table.left_TR[1]-table.y_factor< cor[1]<table.left_BR[1]+table.y_factor:  #y in range
            edge_x=(table.image_height- cor[1]-table.right_intercept)/table.right_slope   # the table "edge x" for this y of the ball
            if cor[0]>edge_x+table.x_factor:  # ball is righter than the table edge x for this y
                print("# ball is righter than the table edge x for this y")
                return False
        return True   #in

    def frames_were_close(self,start,step):
        """
        difference of less than 5 frames between each of the last 3 detections
        """
        if self.location_queue[start][2]-self.location_queue[start-step][2]<7 and self.location_queue[start+step][2]-self.location_queue[start][2]<7:
            print("FRAMES WERE CLOSE")
            return True
        else:
            print("FRAMEWS WERENT CLOSE")
            return False

    def up_down_up(self,table,start_search,step):
        """
        :return:# - _ - motion or - _ _ - motion
        """

        # we want a more significant dip and rise so the machine will not fail as with balls that rose and dipped with y coordinate of 1 or 2
        prev_x, prev_y, prev_frame = self.location_queue[start_search - step]  # frame for ex -4
        cur_x, cur_y, cur_frame = self.location_queue[start_search]  # frame for ex -3
        next_x, next_y, next_frame = self.location_queue[start_search + step]  # frame for ex -2
        if prev_y < cur_y-2 and next_y < cur_y-2:  # - _ - motion with a threshold of two pixels rise
            if self.frames_were_close(start=start_search,step=step):
                if cur_frame-table.bounces_queue[-1][3] > 3: # avoids problem of ''-_''' where both the 3rd and 4th chars would count as bounces
                    if (cur_x, cur_y) != (table.bounces_queue[-1][0],table.bounces_queue[-1][1]):# make sure we dont mark the same bounce twice
                        print("verdict bounce, start=",start_search, "step =",step)
                        return True
        return False

    def live_ball_bounce(self,game, frame_number):
        cor = self.location_queue[-3]  # 2nd last ball detection
        left = self.in_left_table(game.table, cor)
        right = self.in_right_table(game.table, cor)
        if left or right:  # if that 2nd last was on left or right table
            if self.up_down_up(game.table,start_search=-3,step=1) or self.up_down_up(game.table,start_search=-3,step=2):  # if the ball did bounce at his 3rd last location
                if self.keep_left_direction() or self.keep_right_direction():# ball keeps moving right or left meaning its not a bounce on the racket, helps eliminate scratch hits
                    game.table.update_last_bounce_cor(self.location_queue[-3][:2], left, right, self.location_queue[-3][2])
                    self.print_bounce(left,frame_number-2)
                    game.point.update_bounce(self.location_queue[-3][:2], left, right, self.location_queue[-3][2])

        print("recent bounces array: ", game.table.bounces_queue)


    def keep_left_direction(self):
        for i in range(1,5):
            if self.location_queue[-i][0]>self.location_queue[-i-1][0]:
                print("failed left motion")
                return False
        print("success left motion")
        return True

    def keep_right_direction(self):
        for i in range(1,5):
            if self.location_queue[-i][0]<self.location_queue[-i - 1][0]:
                print("failed right motion")
                return False
        print("success right motion")
        return True

    def print_bounce(self,left,frame_number):
        side = 0 if left is True else 1
        print("bounced at: ", self.location_queue[-3][:2],"frame "+str(frame_number), "which is ", side, " side")


class TABLE:

    def __init__(self, table_corners, net_edges,image):

        self.left_TL = table_corners[1]
        self.left_BL = table_corners[0]
        self.left_TR = ((table_corners[1][0] + table_corners[2][0]) // 2, (table_corners[1][1] + table_corners[2][1]) // 2)
        self.left_BR = ((table_corners[0][0] + table_corners[3][0]) // 2, (table_corners[0][1] + table_corners[3][1]) // 2)
        self.right_TR = table_corners[2]
        self.right_BR = table_corners[3]
        self.right_TL = ((table_corners[1][0] + table_corners[2][0]) // 2, (table_corners[1][1] + table_corners[2][1]) // 2)
        self.right_BL = ((table_corners[0][0] + table_corners[3][0]) // 2, (table_corners[0][1] + table_corners[3][1]) // 2)
        self.net_top = net_edges[0]
        self.net_Bottom = net_edges[1]
        self.net_edges=net_edges

        self.bounces_queue = 3*[[0, 0,-1,0]] #x,y,side,frame_number
        self.pts_for_polygon_draw=[np.array([[self.left_BL],[self.left_TL],[self.right_TR],[self.right_BR]],np.int32).reshape((-1, 1, 2))]

        self.image_height = image.shape[0]

        self.left_slope=(self.left_BL[1]-self.left_TL[1])/(self.left_TL[0]-self.left_BL[0])
        self.left_intercept=-1*(self.left_slope*self.left_BL[0])+(self.image_height-self.left_BL[1])
        self.right_slope=(self.right_TR[1]-self.right_BR[1])/(self.right_BR[0]-self.right_TR[0])
        self.right_intercept=-1*(self.right_slope*self.right_TR[0])+(self.image_height-self.right_TR[1])
        """
        i inverted the y axis for these atributes so 0,0 now is bottom left of the screen
        """
        self.y_factor=70
        self.x_factor=70
        self.last_bounce_side=None


    def update_last_bounce_cor(self, cor,left,right,frame_number):
        self.bounces_queue.pop(0)
        if left:
            self.bounces_queue.append([cor[0],cor[1],0,frame_number])
            self.last_bounce_side = 0
        else :
            self.bounces_queue.append([cor[0],cor[1],1,frame_number])
            self.last_bounce_side = 1


class GAME:
    def __init__(self,table,ball,point,fps,shape):
        self.table=table
        self.ball=ball
        self.point=point
        self.fps = fps
        self.score = [0,0]
        self.server = point.server# left=0/right=1
        self.live_ball = False  # false until serve, true until point scored
        self.about_to_serve = False
        self.left=0
        self.right=1
        self.pre_serve_bounces=3
        self.image_width=shape[1]
        self.image_height=shape[0]
        self.prev_event="None"
        self.players_txt=["left","right"]
        if self.fps==120:
            self.x_traveling_dist=7
        else:
            self.x_traveling_dist = 13
    def update_score(self, scorer):  # scorer is a string of who scored
        self.score[scorer]+=1


class POINT:
    def __init__(self):
        self.server=0
        self.last_bounce_side=None
        self.last_bounces=2*[[0,0,-1,0]]
        self.last_hitter=self.server

    def reset(self,game):
        self.last_bounce_side=None
        self.last_bounces[0] = [0,0,-1,0]
        self.last_bounces[1] = [0,0,-1,0]
        self.last_hitter=None
        if (game.score[0]+game.score[1])%5==0:
            game.server=1-game.server
            self.server=1-self.server

    def update_bounce(self,location, left, right, frame_number):
        self.last_bounces.pop(0)
        bounce_side = 0 if left is True else 1
        self.last_bounces.append([location[0], location[1], bounce_side, frame_number])
        self.last_bounce_side = bounce_side


    def update_hitter(self,ball):
        if ball.location_queue[-1]>ball.location_queue[-2]>ball.location_queue[-3]:
            print('left player hit')
            self.last_hitter=0
        elif ball.location_queue[-1]<ball.location_queue[-2]<ball.location_queue[-3]:
            print('right player hit')
            self.last_hitter=1
        else:
            print("could not find continues motion in any direction")
            self.last_hitter=-1