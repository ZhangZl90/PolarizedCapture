import cv2
import matplotlib
import numpy as np

matplotlib.use('Agg')


def f_1(x, A, B):
    return A * x + B


if __name__ == '__main__':
    left_camera_matrix = np.array([[8.995005273265216e+02, 0, 0],
                                   [0.165559863153613, 8.994060391394378e+02, 0],
                                   [6.213816830168396e+02, 5.034540671546230e+02, 1]])
    left_camera_matrix = left_camera_matrix.T
    left_distortion = np.array([[-0.2088, 0.2735, -0.0012, 8.2097e-04, -0.3771]])
    right_camera_matrix = np.array([[9.148181171049489e+02, 0, 0],
                                    [0.538038273554672, 9.152026195909501e+02, 0],
                                    [6.017004172321599e+02, 5.132135829459576e+02, 1]])
    right_camera_matrix = right_camera_matrix.T
    right_distortion = np.array([[-0.1718, 0.1618, 0.0027, 8.1992e-06, -0.2572]])

    R = np.array([[0.9997, -0.0170, -0.0170],
                  [0.0170, 0.9998, -0.0036],
                  [0.0171, 0.0033, 0.9998]])
    R = R.T
    T = np.array([-46.3535, -7.0962, 13.6637])
    size = (1224, 1024)  # 图像尺寸
    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(left_camera_matrix, left_distortion, right_camera_matrix, right_distortion, size, R, T)
    left_map1, left_map2 = cv2.initUndistortRectifyMap(left_camera_matrix, left_distortion, R1, P1, size, cv2.CV_16SC2)
    right_map1, right_map2 = cv2.initUndistortRectifyMap(right_camera_matrix, right_distortion, R2, P2, size, cv2.CV_16SC2)
    focal_length = Q[2][-1]
    Baseline = np.abs(T[0]) / 1000

    left_images = cv2.imread('./TRI050S-Q-194100034/2021-12-11(degree0)/21-12-11-15-06-32-587526_0.png')
    right_images = cv2.imread('./TRI050S-Q-194100036/2021-12-11(degree0)/21-12-11-15-06-33-616783_0.png')
    imageH, imageW, _ = left_images.shape
    left_rec = cv2.remap(left_images, left_map1, left_map2, cv2.INTER_LINEAR)
    right_rec = cv2.remap(right_images, right_map1, right_map2, cv2.INTER_LINEAR)
    image_rec = np.zeros((imageH, imageW * 2, 3))
    image_rec[:, :imageW] = left_rec
    image_rec[:, imageW:] = right_rec
    cv2.imwrite('rec.png', image_rec)
