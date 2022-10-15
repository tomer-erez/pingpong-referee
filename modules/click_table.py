import cv2
import numpy as np

# Create point matrix get coordinates of mouse click on image
point_matrix = 5*[(0,0)]
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
        for x in range(5):
            cv2.circle(img, (point_matrix[x][0], point_matrix[x][1]), 3, (0, 0, 255), cv2.FILLED)
        if counter == 5:
            return point_matrix[:4]
        # Showing original image
        cv2.imshow("Original Image ", img)
        # Mouse click event on original image
        cv2.setMouseCallback("Original Image ", mousePoints)
        # Printing updated point matrix
        # Refreshing window all time
        cv2.waitKey(300)

def get_table_corners(img):
    corners = draw(img)
    cv2.destroyAllWindows()
    corners = sorted(corners, key=lambda tup: tup[0])
    print("the following are the table corners: ", corners)
    return corners