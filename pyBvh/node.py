from . import geometry
from copy import deepcopy
import numpy as np
from enum import Enum
import math

class ntype(Enum):
    ROOT = 'ROOT'
    JOINT = 'JOINT'
    END = 'End'

class node:
    class ordered_vec3(geometry.Vec3):
        def __init__(self, seaquence_str='X Y Z', dtype=np.float32):
            super().__init__(dtype=dtype)
            self.sequence = seaquence_str.split(' ')

        def set_values_from_str(self, value_str, is_separate=False):
            seq = value_str
            if is_separate:
                seq = seq.split(' ')
            for s, v in zip(self.sequence, seq):
                if 'X' in s:
                    self.x(float(v)) 
                elif 'Y' in s:
                    self.y(float(v)) 
                elif 'Z' in s:
                    self.z(float(v))

        def set_values(self, values):
            for s, v in zip(self.sequence, values):
                if 'X' in s:
                    self.x(v)
                elif 'Y' in s:
                    self.y(v)
                elif 'Z' in s:
                    self.z(v)

    class ordered_rotate(geometry.Rotate):
        def __init__(self, seaquence_str='X Y Z', dtype=np.float32):
            super().__init__(dtype=dtype)
            self.sequence = seaquence_str.split(' ')

        def set_values_from_str(self, value_str, is_separate=False):
            seq = value_str
            if is_separate:
                seq = seq.split(' ')
            self.values = geometry.Rotate.Unit(dtype=self.dtype)
            for s, v in zip(self.sequence, seq):
                if 'X' in s:
                    self.rotateX(math.radians(float(v)))
                elif 'Y' in s:
                    self.rotateY(math.radians(float(v)))
                elif 'Z' in s:
                    self.rotateZ(math.radians(float(v)))

        def set_values(self, values):
            self.values = geometry.Rotate.Unit(dtype=self.dtype)
            for s, v in zip(self.sequence, values):
                if 'X' in s:
                    self.rotateX(np.radians(v))
                elif 'Y' in s:
                    self.rotateY(np.radians(v))
                elif 'Z' in s:
                    self.rotateZ(np.radians(v))


    def __init__(self, ntype, name=None, parent=None):
        self.ntype = ntype
        self.name=name
        self.value = []
        self.parent = parent
        self.children = []
        self.num_channels = 0
        self.channels = []
        self.offset = None
        self.position = None
        self.rotation = None
        self.global_matrix = geometry.Matrix4x4()
        self.local_matrix = geometry.Matrix4x4()
        
        if self.parent:
            self.parent.add_child(self)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def print_tree(self, sy=''):
        _sy = sy
        print(_sy + '[{0}({1})]'.format(self.name, self.ntype))
        for child in self.children:
            child.print_tree(sy + '+')
    
    def update_matrix(self, global_mat):
        _global_mat = deepcopy(global_mat)
        local_mat = geometry.Matrix4x4()
        if self.position is None:
            local_mat.translate(self.offset)
        else:
            local_mat.translate(self.position)
        if not self.rotation is None:
            local_mat.rotate(self.rotation)
        _global_mat.multi(local_mat)
        self.local_matrix = local_mat
        self.global_matrix = _global_mat
        for child in self.children:
            child.update_matrix(_global_mat)

    def add_position(self, seaquence_str):
        self.position = node.ordered_vec3(seaquence_str)
        self.channels.append('position')

    def add_rotation(self, seaquence_str):
        self.rotation = node.ordered_rotate(seaquence_str)
        self.channels.append('rotation')

    def initialize_values(self):
        def __get_order(chs, elase=''):
            ch_order = chs[0] + ' ' + chs[1] + ' ' + chs[2]
            return ch_order.replace(elase, '')

        if self.value is not None:
            _, ox, oy, oz = self.value[0].split(' ')
            self.offset=geometry.Vec3(ox, oy, oz)
            if len(self.value) == 2:
                ch_datas = self.value[1].split(' ')[2:]
                self.num_channels = self.value[1].split(' ')[1]
                for ch in zip(*[iter(ch_datas)]*3):
                    if 'position' in ch[0]:
                        self.add_position(__get_order(ch, 'position'))
                    elif 'rotation' in ch[0]:
                        self.add_rotation(__get_order(ch, 'rotation'))
