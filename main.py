import numpy as np
import cv2

#
# s = set()
# s.add(1)
# s.add(1)
# s.add(2)
# s.add(3)
#
# ss = set([2,3])
# print("Is subset: %(isSubset)s with %(certaintity)f%% certainty" % {"isSubset": ss.issubset(s), "certaintity": 0.05})
#
# print(s)
#
# img = cv2.imread("image1.jpg")
#
# img = np.array(img)
#
# for x in range(0, len(img)):
#     for y in range(0, len(img[x])):
#         val = img[x,y]
#         if img[x,y].any() > 30:
#             img[x, y][1] = 255
#         else:
#             img[x, y][1] = 0
#
#
# cv2.imshow('image',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()



def captch_ex(file_name):
    img = cv2.imread(file_name)

    img_final = cv2.imread(file_name)
    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 150, 255, cv2.THRESH_BINARY)
    image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
    cv2.imshow('Threshold 1', image_final)
    cv2.waitKey()
    ret, new_img = cv2.threshold(image_final, 25, 255, cv2.THRESH_BINARY)  # for black text , cv.THRESH_BINARY_INV
    cv2.imshow('Throshold 2', new_img)
    '''
            line  8 to 12  : Remove noisy portion
    '''
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2,
                                                         2))  # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more

    erosion_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
    eroded = cv2.erode(new_img, erosion_kernel, iterations=1)
    cv2.imshow('Eroded', eroded)
    dilated = cv2.dilate(eroded, kernel, iterations=5)  # dilate , more the iteration more the dilation
    cv2.imshow('Dialation', dilated)

    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # get contours
    """
    image, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)  # cv3.x.x
    """

    car_plate_ratio = 200/40
    error_margin = 5

    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        ok_color = (0,255,0)
        false_color = (255,0,0)
        selected_color = ok_color

        # Don't plot small false positives that aren't text
        if w < 35 and h < 35:
            continue

        if w / h < car_plate_ratio - error_margin or w / h > car_plate_ratio + error_margin:
            selected_color = false_color

        # draw rectangle around contour on original image
        cv2.rectangle(img, (x, y), (x + w, y + h), selected_color, 2)

        '''
        #you can crop image and send to OCR  , false detected will return no text :)
        cropped = img_final[y :y +  h , x : x + w]

        s = file_name + '/crop_' + str(index) + '.jpg'
        cv2.imwrite(s , cropped)
        index = index + 1

        '''
    # write original image with added contours to disk
    cv2.imshow('captcha_result', img)
    cv2.waitKey()


file_name = 'sample_img_1.jpg'
captch_ex(file_name)