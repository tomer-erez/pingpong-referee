from modules.nnet_functions import *
#from display_functions import show_frame


def scan_table(image):
    colors = [(203, 192, 255), (0, 128, 255)]  # beige, orange

    # get classes names
    with open("classes/table_net.txt", "r") as f:
        class_names = [cname.strip() for cname in f.readlines()]

    # set neural net
    model = set_net("yolo_weight/yolov4-tiny-table.weights", "yolo_cfg/yolov4-tiny-table.cfg")

    # detect objects in image
    classes, scores, boxes = model.detect(image, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    # read model return values
    for (classid, score, box) in zip(classes, scores, boxes):
        # choosing color
        color = colors[int(classid)]

        # draw around the items
        label = "%s : %f " % (class_names[classid], score)
        cv2.rectangle(image, box, color, 2)
        cv2.putText(image, label, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)

    # show the frame for a second and close
    cv2.imshow("window name",image)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

    # table cors,net cors
    return boxes[0], boxes[1]
