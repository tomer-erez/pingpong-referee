import cv2
import numpy as np

# Create point matrix get coordinates of mouse click on image
point_matrix = 3*[(0,0)]
counter = 0
def mousePoints(event, x, y, flags, params):
    global counter
    # Left button mouse click event opencv
    if event == cv2.EVENT_LBUTTONDOWN:
        point_matrix[counter] = x, y
        counter = counter + 1
# Read image

def draw(img):
    #4 clicks on the screen for table corners, 5th to exit
    while True:
        for x in range(3):
            cv2.circle(img, (point_matrix[x][0], point_matrix[x][1]), 4, (226, 43, 138), cv2.FILLED)
        if counter == 3:
            return point_matrix[:2]
        # Showing original image
        cv2.imshow("Original Image ", img)
        # Mouse click event on original image
        cv2.setMouseCallback("Original Image ", mousePoints)
        # Printing updated point matrix
        # Refreshing window all time
        cv2.waitKey(300)

def get_net_line(img):
    corners = draw(img)
    cv2.destroyAllWindows()
    corners = sorted(corners, key=lambda tup: tup[1])
    print("the following are the net vertices: ", corners)
    return corners