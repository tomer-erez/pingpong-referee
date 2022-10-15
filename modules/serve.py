def serve_detection(game,frame_number):
    fifth = game.ball.location_queue[-5] # suspicious as the bounce coordinate
    if game.server == 0:
        in_table = game.ball.in_left_table(game.table, fifth[:2]) # if the fifth last cor was on the left table
    else:
        in_table = game.ball.in_right_table(game.table, fifth[:2]) # if the fifth last cor was on the right table

    if in_table:
        if game.ball.up_down_up(game.table,start_search=-5,step=1) or game.ball.up_down_up(game.table,start_search=-5,step=2):## if the ball did - _ - in the frames -x-2 , -x, -x+2 or -x-1,-x,-x+1
            if frame_number-game.table.bounces_queue[-2][3]>30:  # not a part of the previous point that was determined with a score
                if (game.server == 0 and serve_left(game,game.ball)) or (game.server == 1 and serve_right(game,game.ball)):# the serve direction matches the server
                    game.table.bounces_queue.pop(0)
                    game.table.bounces_queue.append([fifth[0],fifth[1],game.server,frame_number-6])
                    start_point(game.point, game, game.table)




def start_point(point,game,table):
    game.live_ball = True
    game.about_to_serve = False
    game.prev_event = "served"
    print("ball was served")
    point.last_bounce_side = game.server
    point.last_bounces[-1] = table.bounces_queue[-1]



def serve_left(game,ball):
    x_cor = 0
    for i in range(2, 6):
        if ball.location_queue[-i][x_cor] - ball.location_queue[-i - 1][x_cor] < game.x_traveling_dist:# 7 pixels for 120 fps, 13 pixels for 60fps
            print("failed in x traveling condition-LEFT")
            return False
    print("served left")
    return True


def serve_right(game,ball):
    x_cor = 0
    for i in range(2, 6):
        if ball.location_queue[-i][x_cor] - ball.location_queue[-i - 1][x_cor] > -game.x_traveling_dist:# 7 pixels for 120 fps, 13 pixels for 60fps
            print("failed in x traveling condition-RIGHT")
            return False
    print("served right")
    return True