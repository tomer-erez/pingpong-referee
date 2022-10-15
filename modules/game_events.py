from modules.serve import serve_detection

def ping_pong_events( game,frame_number):
    """
    :param game
    :param frame_number
    Event spotting: was the ball served, double bounced, single bounce etc..
    """

    if game.live_ball is False:# a point has yet to be started, search for a serve
        serve_detection(game,frame_number) # if the ball was served, meaning first bounce in the server player, update "live ball" to true and "about to serve" to false

    else: # we are in the middle of a ping pong rally
        game.ball.live_ball_bounce(game, frame_number)
        rally(game,frame_number)


def rally(game,frame_number):
    print("point bounces array ",game.point.last_bounces)

    if double_bounce(game):
        game.live_ball = False

    elif winner(game,frame_number):
        game.live_ball = False



def double_bounce(game):
    side=2
    prev_bounce_side=game.point.last_bounces[-2][side]
    cur_bounce_side=game.point.last_bounces[-1][side]
    if cur_bounce_side==prev_bounce_side: #if 2nd last and last bounces on same side
        game.update_score(1-cur_bounce_side)
        print("ball bounced twice on ",game.players_txt[cur_bounce_side] ," player side")
        game.prev_event="player %s scored" % (game.players_txt[1-cur_bounce_side])
        game.point.reset(game)
        return True
    return False

def  winner(game,frame_number):
    frame_idx=3
    side_idx=2
    if frame_number-game.point.last_bounces[-1][frame_idx]>1.25*game.fps: # if the ball hasnt returned in essentialy 1.25 seconds, it wont come back at all
        print("the ball hasn't bounced in too long of a time span")
        game.update_score(1 - game.point.last_bounces[-1][side_idx])
        print("LAST BOUNCE SIDE",game.point.last_bounce_side)
        print("ball was not returned by", game.players_txt[1-game.point.last_bounce_side], " player")
        game.prev_event = "player %s scored" % (game.players_txt[1-game.point.last_bounce_side])
        game.point.reset(game)
        return True
    return False