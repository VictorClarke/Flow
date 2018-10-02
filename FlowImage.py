from functools import reduce

__author__ = 'Victor'
import cv2
import numpy as np

class FlowImage:
    def __init__(self, image):
        self.image = cv2.imread(image)
        self.GrayImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.getGrid()
        self.getColors()


    def getColors(self):
        circles = cv2.HoughCircles(self.GrayImage, cv2.cv.CV_HOUGH_GRADIENT, 1, 25, param1=70, param2=50, minRadius=30, maxRadius=80)
        circles = np.uint16(np.around(circles))
        centers = []
        sorted = []
        groups = []

        for circle in circles[0,:]:
            groups.append(self.image[circle[1], circle[0]])
            centers.append((circle[1], circle[0]))

        for circle1, (b1, g1, r1) in enumerate(groups):
            for circle2, (b2, g2, r2) in enumerate(groups):

                difference = abs(abs(int(r1) - int(r2)) + abs(int(g1) - int(g2)) + abs(int(b1) - int(b2)))
                if difference < 25 and difference is not 0:
                    groups[circle1] = groups[circle2]

        for circle1, (b1,g1,r1) in enumerate(groups):
            for circle2, (b2,g2,r2) in enumerate(groups):
                if b1 == b2 and g1 == g2 and r1 == r2 and circle2 > circle1:
                    color1 = (centers[circle1][0]/self.cell_spacing,centers[circle1][1]/self.cell_spacing)
                    color2 = (centers[circle2][0]/self.cell_spacing,centers[circle2][1]/self.cell_spacing)
                    sorted.append([color1,color2])
        self.colors = sorted


    def getGrid(self):
        edges = cv2.Canny(self.GrayImage, 200, 250, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 325, minLine=560, maxGap=120)[0].tolist()

        for x1, y1, x2, y2 in lines:
            for i, (x3, y3, x4, y4) in enumerate(lines):
                if y1 == y2 and y3 == y4:
                    difference = abs(y1-y3)
                elif x1 == x2 and x3 == x4:
                    difference = abs(x1-x3)
                else:
                    difference = 0
                if difference < 15 and difference is not 0:
                    del lines[i]

        self.gridSize = (len(lines) - 2) / 2
        spaceForCells = [(L[0]) for L in lines if L[0] == L[2]]
        spaceForCells = sorted(spaceForCells)
        spaceForCells = spaceForCells[0:2]
        self.cell_spacing = reduce(lambda a, b: b-a, spaceForCells)