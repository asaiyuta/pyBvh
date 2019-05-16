import numpy as np
import math

# use numpy geometry helpers for bvh file
# created by 4541 

class Vec3:
    def __init__(self, x=0.0, y=0.0, z=0.0, dtype=np.float32):
        self.dtype = dtype
        self.values = np.array([x, y, z], dtype=self.dtype)
    
    def __array__(self):
        return self.values

    def __array_wrap__(self, out_arr, context=None):
        return Vec3(out_arr[0], out_arr[1], out_arr[2], self.dtype)

    def x(self, value=None):
        if value:
            self.values[0] = value
        return self.values[0]
        
    def y(self,value=None):
        if value:
            self.values[1] = value
        return self.values[1]

    def z(self, value=None):
        if value:
            self.values[2] = value
        return self.values[2]

    def get4x4Translate(self):
        return np.array([
            [1, 0, 0, self.values[0]],
            [0, 1, 0, self.values[1]],
            [0, 0, 1, self.values[2]],
            [0, 0, 0, 1]
        ], dtype=self.dtype)

class Rotate:
    def __init__(self, unit=None, dtype=np.float32):
        self.dtype = dtype
        self.values = Rotate.Unit(self.dtype)
        if unit is not None:
            self.values = unit

    @staticmethod
    def Unit(dtype=np.float32):
        return np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=dtype)

    @staticmethod
    def getRotateX(rad, dtype=np.float32):
        c = np.cos(rad)
        s = np.sin(rad)
        return Rotate(np.array([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c]
        ], dtype=dtype), dtype)

    @staticmethod
    def getRotateY(rad, dtype=np.float32):
        c = np.cos(rad)
        s = np.sin(rad)
        return Rotate(np.array([
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c]
        ], dtype=dtype), dtype)

    @staticmethod
    def getRotateZ(rad, dtype=np.float32):
        c = np.cos(rad)
        s = np.sin(rad)
        return Rotate(np.array([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1]
        ], dtype=dtype), dtype)

    def __array__(self):
        return self.values

    def __array_wrap__(self, out_arr, context=None):
        return Rotate(out_arr, self.dtype)
    
    def rotateX(self, rad):
        def __get_rotateX_mat(rad, dtype):
            c = np.cos(rad)
            s = np.sin(rad)
            return np.array([
                [1, 0, 0],
                [0, c, -s],
                [0, s, c]
            ], dtype=dtype)
        self.values = np.matmul(self.values, __get_rotateX_mat(rad, self.dtype))
    
    def rotateY(self, rad):
        def __get_rotateY_mat(rad, dtype):
            c = np.cos(rad)
            s = np.sin(rad)
            return np.array([
                [c, 0, s],
                [0, 1, 0],
                [-s, 0, c]
            ], dtype=dtype)
        self.values = np.matmul(self.values, __get_rotateY_mat(rad, self.dtype))

    def rotateZ(self, rad):
        def __get_rotateZ_mat(rad, dtype):
            c = np.cos(rad)
            s = np.sin(rad)
            return np.array([
                [c, -s, 0],
                [s, c, 0],
                [0, 0, 1]
            ], dtype=dtype)
        self.values = np.matmul(self.values, __get_rotateZ_mat(rad, self.dtype))

    def get4x4(self):
        return np.insert(np.insert(self.values, 3, [0, 0, 0], axis=0), 3, [0, 0, 0, 1], axis=1)

class Matrix4x4:
    def __init__(self, unit=None, dtype=np.float32):
        self.dtype = dtype
        self.values = Matrix4x4.Unit(self.dtype)
        if unit is not None:
            self.values = unit

    @staticmethod
    def Unit(dtype=np.float32):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=dtype)

    def __array__(self):
        return self.values

    def __array_wrap__(self, out_arr, context=None):
        return Matrix4x4(unit=out_arr, dtype=self.dtype)

    def getRotate(self):
        return Rotate(self.values[:3, :3] ,self.dtype)

    def getTranslate(self):
        return Vec3(self.values[0][3], self.values[1][3], self.values[2][3], dtype=np.float32)

    def rotate(self, rotate):
        self.values = np.matmul(self.values, rotate.get4x4())

    def translate(self, translate):
        self.values = np.matmul(self.values, translate.get4x4Translate())

    def multi(self, mat4x4):
        self.values = np.matmul(self.values, mat4x4.values)