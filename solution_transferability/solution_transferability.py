import cv2
import numpy as np
from pyModbusTCP.client import ModbusClient

FRAME_Y_MIN = 0
FRAME_Y_MAX = 480
FRAME_X_MIN = 0
FRAME_X_MAX = 640
conversion_factor_x = 0.288
conversion_factor_y = 0.288


def image_capture():
    cam_port = 0
    cam = cv2.VideoCapture(cam_port, cv2.CAP_DSHOW)

    result, image = cam.read()
    crop_image = image[FRAME_Y_MIN:FRAME_Y_MAX, FRAME_X_MIN:FRAME_X_MAX]
    if result:
        cv2.imshow("camera", crop_image)
        # cv2.imwrite("cam10.jpeg", crop_image)  ## to save the file
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Some Error, Try again")

    return crop_image


raw_image = image_capture()

# raw_image = cv2.imread("camera1.jpeg")

# roi = cv2.selectROI("camera_button", raw_image)
# print(roi)  # .......... to print the co_ordinates of
# roi_cropped = raw_image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

gray_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
blured_img = cv2.GaussianBlur(gray_image, (5, 5), 0)
ret, thresh1 = cv2.threshold(blured_img, 80, 255, cv2.THRESH_BINARY_INV)

contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
print("Number of contours" + str(len(contours)))

for cnts in contours:
    area = cv2.contourArea(cnts)
    print(area)
    peri = cv2.arcLength(cnts, True)
    approx = cv2.approxPolyDP(cnts, 0.03 * peri, True)

    if 400 < area < 1100 and len(approx) == 4:
        rect = cv2.minAreaRect(cnts)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(raw_image, [box], 0, (0, 0, 255), 2)
        x, y = rect[0]
        width, height = rect[1]
        rotation_angle = rect[-1]

        if width < height:
            rotation_angle = 90 - rect[-1]
        else:
            rotation_angle = 180 - rect[-1]

        x_world = x * conversion_factor_x
        y_world = y * conversion_factor_y

        x_robot = x_world + 215.8

        #y_robot = 49.8 - y_world

        rotation_angle1 = 180 - rotation_angle

        print("The co-ordinates in mm are: ", (x_world, y_world))
        print("The ROBO co-ordinates in mm are: ", (x_robot, y_world))
        print("The rotation angle is :", rotation_angle)

cv2.imshow("threshold_img", thresh1)
cv2.imshow("contour", raw_image)
if cv2.waitKey(0) & 0xFF == ord("s"):
    cv2.destroyAllWindows()

client = ModbusClient(host="194.94.86.6", port=502)
client.open()

print(client.is_open(), "For checking the connection")
print("Sending values......")
client.write_single_register(24640, int(rotation_angle*10))
client.write_single_register(24641, int(x_robot * 10))
client.write_single_register(24642, int(y_world * 10))
client.write_single_register(24643, int(1000))
print("Value sent successfully")