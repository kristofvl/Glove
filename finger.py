import numpy as np
from numpy.linalg import inv
import settings
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLUT import *  # noqa: F403
from limb import *
import pyrr


class Finger():
    def __init__(self, l, w, h):
        self.limbs = [Limb(
            l=l,
            w=w,
            h=h/3
        ) for i in range(3)]

        self.tipPosition = self.limbs[2].calculateTip()

    def update(self):
        # zip: convert list to tubles of 2 arrays
        # allclose: compare if 2 arrays are euqual element wise with tolerance
        # all: OR combination of all truth values
        # if all([np.allclose(x, y, atol=0.0001) for x, y in zip(self.rotationList, settings.rotationList)]):
        pass

    def updateTipRotation(self, rotationTip, rotationPalm):
        self.limbs[2].rotation = rotationTip
        self.calculateSubRotations(rotationTip, rotationPalm)

    def calculateSubRotations(self, rotationTip, rotationPalm):
        tipQuat = pyrr.Quaternion.from_matrix(rotationTip)
        palmQuat = pyrr.Quaternion.from_matrix(rotationPalm)
        identityQuat = pyrr.Quaternion(pyrr.Matrix44.identity())
        dist = palmQuat.inverse * tipQuat  # rotation of tip without rotation of palm
        if (dist.w < 0):
            dist = - dist
        finger1 = palmQuat * identityQuat.slerp(dist, 0.333)
        finger2 = palmQuat * identityQuat.slerp(dist, 0.666)

        self.limbs[0].rotation = pyrr.matrix44.create_from_quaternion(finger1)
        self.limbs[1].rotation = pyrr.matrix44.create_from_quaternion(finger2)

        # TODO seperate swing and twist?!
        # TODO implement natural divisions https://scielo.conicyt.cl/pdf/ijmorphol/v28n3/art15.pdf
        pass

    def updatePosition(self, palmTip, palmRotation, offsetX, offsetZ):
        # calculate fingerBot position
        delta = np.dot(np.array([offsetX, 0, offsetZ], dtype=np.float32), palmRotation[:3, :3])
        self.limbs[0].position = palmTip + delta
        self.limbs[0].calculateTip()
        self.limbs[1].position = self.limbs[0].tipPosition
        self.limbs[1].calculateTip()
        self.limbs[2].position = self.limbs[1].tipPosition
        self.limbs[2].calculateTip()
        self.tipPosition = self.limbs[2].tipPosition

    def overlapsWith(self, cubeList: list[Cuboid]):
        overlapping = []

        for index, cube in enumerate(cubeList):
            # x
            if (self.tipPosition[0]+self.limbs[2].l/2) < (cube.position[0]-cube.l/2):
                continue

            if (self.tipPosition[0]-self.limbs[2].l/2) > (cube.position[0]+cube.l/2):
                continue

            # y
            if (self.tipPosition[1]) < (cube.position[1]-cube.h):
                continue

            if (self.tipPosition[1]-2) > (cube.position[1]):
                continue

            # z
            if (self.tipPosition[2]-self.limbs[2].w/2) > (cube.position[2]+cube.w/2):
                continue

            if (self.tipPosition[2]+self.limbs[2].w/2) < (cube.position[2]+cube.w/2):
                continue

            overlapping.append(index)
        return overlapping

    def draw(self):
        settings.texture.use()
        for limb in self.limbs:
            limb.draw()