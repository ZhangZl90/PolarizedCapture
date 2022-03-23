# @Author:ZhangZl
# @Date:26/11/2021

import cv2
import numpy as np


class polarizedImage:
    def __init__(self, raw_image):
        self.raw_image = raw_image
        self.width = self.raw_image.shape[0]
        self.height = self.raw_image.shape[1]
        self.channels = self.raw_image.shape[2]

    def raw2images(self):
        image_90 = self.raw_image[::2, ::2, ::-1]
        image_45 = self.raw_image[::2, 1::2, ::-1]
        image_135 = self.raw_image[1::2, ::2, ::-1]
        image_0 = self.raw_image[1::2, 1::2, ::-1]
        return image_0, image_45, image_90, image_135

    def get_color(self):
        return cv2.resize(self.raw_image, (self.width // 4, self.height // 4))


if __name__ == "__main__":
    imgP = cv2.imread('./TRI050S-Q-194100034/21-12-01-14-40-55-980008_0.png',cv2.IMREAD_UNCHANGED)
    imgA = cv2.imread('TRI050S-Q-194100034/LUCID_TRI050S-Q_194100034__20211201144118899_image0_0.jpg', cv2.IMREAD_UNCHANGED)
    imgD = np.mean(imgA-imgP)

    print("debug")
