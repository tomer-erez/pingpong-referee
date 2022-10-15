import cv2


CONFIDENCE_THRESHOLD = 0.15  # threshold of score to show prediction
NMS_THRESHOLD = 0.4  # for non max suppression

def set_net(weights, cfg):
    net = cv2.dnn.readNet(weights, cfg)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)
    return model
