from modules.classes import *
from modules.get_table import scan_table
from modules.game_play import *
from modules.click_table import *
from modules.click_net import *



def start():
    model, video,fps = game_setup()  # build model with weights and cfg file,  get video file,  get game fps
    status, image = video.read()  # read one picture

    table_corners=get_table_corners(image)  # mouse click to mark table edges
    net_edges=get_net_line(image)           # mouse click to mark net edges
    table = TABLE(table_corners, net_edges,image)  # build table object from the coordinates of net and table
    ball = BALL()  # initiate ball
    point=POINT()   # init point
    game=GAME(table,ball,point,fps,image.shape) # init game with all the params for it

    game_play(model, video,game, frame_number=1,total_read_time=0) # start capturing frames, find ball, spot events