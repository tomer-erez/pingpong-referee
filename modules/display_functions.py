import cv2
import numpy as np
import time


def mark_table(table,frame):
    cv2.polylines(frame, table.pts_for_polygon_draw,True, (203,192,255), 2)
    cv2.putText(frame, "table", (table.left_TR[0]+10,table.left_TR[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,1, (203,192,255), 1)

    cv2.line(frame, table.net_top, table.net_Bottom, (255, 128, 0), 4)
    cv2.putText(frame, "net", (table.net_top[0],table.net_top[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 0), 1)


def mark_trail(frame,ball,curr_frame_number):
    color = (0, 255, 255)# default ball color is yellow
    for x, y,ball_frame_number in ball.location_queue:
        if curr_frame_number-ball_frame_number<ball.queue_length: # dont mark balls from many frames ago just because we didnt notice any since then
            if ball_frame_number==curr_frame_number: # mark the current ball detection in orange
                color =(0, 128, 255)
            cv2.circle(frame, (x, y), 4, color, -1)


def mark_prev_bounce(table,image,game):
    color=(0,0,255)#red
    if game.live_ball is False:
        color=(0,0,0)# if we are in dead ball mark bounces black
    # if game.about_to_serve is True:
    #     color=(255,0,0)#if we are in pre serve routine mark the bounces blue
    cv2.putText(image, 'x', table.bounces_queue[-1][:2], cv2.FONT_HERSHEY_SIMPLEX,1, color, 2)


def mark_ball(score, frame,ball,number_of_frames):
    label = "%s : %f" % ("BALL", score)
    cv2.putText(frame, label, (ball.x, ball.y-30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)
    mark_trail(frame,ball,number_of_frames)


def server_label(game):
    server = "player left" if game.server == 0 else "player right"
    serve_label = "%s : %s" % ("current server", server)
    return serve_label


def bounce_side(live_ball,last_bounce_side):
    side = "serve"
    if live_ball == True:
        side = "left table bounce" if last_bounce_side == 0 else "right table bounce"
    return "state: expecting a "+side


def HIT(live_ball,last_hitter):
    hitter="None"
    if live_ball == True:
        hitter = "left" if last_hitter == 0 else "right"
    return "previous hitter: "+hitter



def captions(frame, start, end,ball,number_of_frames,game,point,total_read_time):
    # mask_depth=130
    # img_1 = np.zeros([mask_depth, game.image_width, 1], dtype=np.uint8)
    # img_1.fill(255)
    # frame[:mask_depth, :game.image_width,:]=img_1

    curr_fps = "current FPS: %d " % (1 / (end - start+0.00001))
    cv2.putText(frame, curr_fps, (5, 30), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255),2)
    average_fps= "average FPS: %d " % (number_of_frames/total_read_time+0.00001)
    cv2.putText(frame, average_fps, (5, 60), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, "frame number: "+str(number_of_frames), (5, 90), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)

    game_score_label= "%s : %d-%d" % ("score", game.score[0], game.score[1])
    cv2.putText(frame, game_score_label, (int(game.image_width//3), 30), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)
    cv2.putText(frame, server_label(game), (int(game.image_width//3),60), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)

    cv2.putText(frame, bounce_side(game.live_ball,point.last_bounce_side), (int(game.image_width//1.5), 60), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)
    cv2.putText(frame, "previous event: "+str(game.prev_event), (int(game.image_width//1.5), 30), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)

    live_or_dead = "live ball" if game.live_ball is True else "dead ball"
    # if game.about_to_serve:
    #     live_or_dead="dead ball, about to serve"
    cv2.putText(frame, live_or_dead, (int(game.image_width//1.5), 90), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)
    cv2.putText(frame, HIT(game.live_ball,point.last_hitter), (int(game.image_width//1.5),120), cv2.FONT_HERSHEY_TRIPLEX  , 1, (0, 0, 255), 2)


def graphics(frame, start, end,number_of_frames,score,game,total_read_time):

    mark_ball(score, frame, game.ball,number_of_frames)  # bounding box around the ball
    captions(frame, start, end, game.ball, number_of_frames,game,game.point,total_read_time)  # put captions on the image
    mark_prev_bounce(game.table, frame,game)
    mark_table(game.table, frame)


def avg_fps(total_read_time,frame_number):
    avg_read_time = (total_read_time + 0.00001) / frame_number
    print("avg frame time: ", avg_read_time, "avg fps: ", 1 / avg_read_time)

def end_timer(start_read, total_read_time,frame_number):
    end_read = time.time()
    read_time = end_read - start_read
    print("LOCAL time for read: ", read_time, ", fps: ", 1 / (read_time + 0.00001))
    total_read_time += read_time
    print("GLOBAL time for read: ",total_read_time/frame_number , ", fps: ",frame_number/total_read_time)
    return end_read,total_read_time

def sum_game(game):
    cv2.waitKey(1)
    cv2.destroyAllWindows()

    img=cv2.imread('film/game_over.jpg')
    img=cv2.resize(img,(1920,1080))

    if game.score[0]>game.score[1]:
        winner_label="Player left won"
    elif game.score[0]<game.score[1]:
        winner_label="Player right won"
    else:
        winner_label="Tied game"
    cv2.putText(img, winner_label, (650, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    label="Final score: "+str(game.score[0])+"-"+str(game.score[1])

    cv2.putText(img, label, (650, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    cv2.imshow('game over', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()