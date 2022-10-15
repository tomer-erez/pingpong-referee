import time
from modules.nnet_functions import *
from modules.display_functions import *
from modules.game_events import ping_pong_events


def game_setup():
    """
    this function reads the neural network weight and architecture, gets video file and extracts the game fps
    important that the game fps will be in the directory name

    :return: the neuralnet, the first image read from the file, and the game fps
    """
    weights = "yolo_weight/yolov4-tiny-pp-pixeled.weights"
    cfg = "yolo_cfg/yolov4-tiny-pp-pixeled.cfg"
    model = set_net(weights, cfg)
    video = "film/games_with_serve_prep/60/2k/7.MP4"
    fps = int(video.split("/")[2])
    print(fps, " fps video was captured")
    #fps =
    cap = cv2.VideoCapture(video)
    start_frame_number =100    # base is 630, check problem in 17240
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)
    return model, cap, fps


def get_single_prediction(classes, scores, boxes):
    """
    improve it!!!
    just access the first element

    input : the detections made by the neural net in a given frame

    :return: the first element in a legal area, and with maximal probability
    """

    score, box = 0, (0, 0, 0, 0)  # default values if no ball was found
    multiple_objects = False
    for (classid, score, box) in zip(classes, scores, boxes):
        box = list(box)
        if (518< box[0] < 640 and 193< box[1] < 282) or (1450 < box[0] < 1580 and 100< box[1] < 190):# yellow tree leafs are bothering the detection
            score, box = 0, (0, 0, 0, 0)
            continue
        multiple_objects = True
        if multiple_objects == True:  # avoid multiple detections, choose prediction with max likelihood
            break
    print("current detection",box)
    return score, box


def game_play(model, video, game, frame_number, total_read_time):
    """
    :param model: the neural net
    :param video: video file, we will read frame by frame
    :param frame_number: our frame number
    :param game: this item holds the table point and ball inside it, as well as the game properties like score and server
    :param total_read_time initialized as 0 , used to track our fps performance
    :return: nothing
    this functio will read a frame, find the ball in it, update the ball location queue, send us to the pingpong event spotting and caption functions
    """
    while True:
        # if game.score[0]==11 or game.score[1]==11:
        #     sum_game(game)
        #     exit()
        start_frame = time.time()
        grabbed, frame = video.read()
        if not grabbed: # no more frames to read
            avg_fps(total_read_time, frame_number)  # print avg fps
            print("final score: ",game.score)
            sum_game(game)
            exit()

        classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)  # detect objects
        score, box = get_single_prediction(classes, scores, boxes)  # avoid multiple detections

        game.ball.update_location_queue(box, frame_number, game)  # update the last two coordinates of the ball

        ping_pong_events(game, frame_number)  # spot events: bounce, serve, double bounce...
        end_frame,total_read_time = end_timer(start_frame, total_read_time,frame_number)  # end timer, print local fps performance
        graphics(frame, start_frame, end_frame,frame_number, score,game,total_read_time)  # draw on the image(objects,captions...)
        cv2.imshow("game", frame)
        cv2.waitKey(1)
        print("game score", game.score,"\n\n\n")
        #cv2.imwrite('frames_to_look_at\Frame' + str(frame_number) + '.jpg', frame)
        frame_number += 1

        # if cv2.waitKey(50) & 0xFF == ord("p"):  # press p to pause v, doesn't work great
        #     cv2.imshow("game", frame)
        #     while True:
        #         if cv2.waitKey(50) & 0xFF == ord("r"):  # press r to resume video
        #             break
        #     continue