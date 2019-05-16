from . import node as nd
from . import geometry as gm
from functools import singledispatch
import numpy as np


class hierarchy:
    def __init__(self, bone_str=None, dtype=np.float32):
        self.nodes = []
        self.dtype=dtype
        if bone_str:
            self.__from_bone_str(bone_str)

    def __iter__(self):
        for n in self.nodes:
            yield n
    
    @singledispatch
    def __getitem__(self, key):
        return [n for n in self.nodes if n.ntype == key]

    @__getitem__.register(str)
    def __getitem_name__(self, key):
        return [n for n in self.nodes if n.name == key]

    def __from_bone_str(self, bone_str):
        def get_name(l):
            return l.split(' ')[-1]

        parent = None
        back = None
        for g in bone_str:
            # print(g)
            if '{' in g:
                parent = back
            if '}' in g:
                parent = parent.parent

            if nd.ntype.ROOT.value in g:
                back = nd.node(name=get_name(g), ntype=nd.ntype.ROOT)
                self.nodes.append(back)
            
            elif nd.ntype.JOINT.value in g:
                back = nd.node(name=get_name(g), ntype=nd.ntype.JOINT, parent=parent)
                self.nodes.append(back)

            elif nd.ntype.END.value in g:
                back = nd.node(name=get_name(g), ntype=nd.ntype.END, parent=parent)
                self.nodes.append(back)

            if 'OFFSET' in g:
                back.value.append(g)

            if 'CHANNELS' in g:
                back.value.append(g)

        
        for n  in self.nodes:
            n.initialize_values()
    
    def print_tree(self):
        for r in self[nd.ntype.ROOT]:
            r.print_tree()

    def updata_matrix(self):
        for r in self[nd.ntype.ROOT]:
            global_mat = gm.Matrix4x4()
            r.update_matrix(global_mat)

class motion:
    def __init__(self, motion_str=None, dtype=np.float32):
        self.frames = 0
        self.frame_time = 0.0
        self.frame_data = None
        self.dtype = dtype
        if motion_str :
            self.__from_motion_str(motion_str)

    def __getitem__(self, key):
        return self.motion_data.frame_data[key]

    def __from_motion_str(self, motion_str):
        self.frames = int(motion_str[0].replace('Frames:', ''))
        self.frame_time = float(motion_str[1].replace('Frame Time:', ''))
        frame_str = motion_str[2:]
        self.frame_data = np.array([list(zip(*[iter(f.split(' '))]*3)) for f in frame_str]).astype(self.dtype)

class bvh:
    def __init__(self, path=None, dtype=np.float32):
        self.dtype = dtype
        self.hierarchy_data = hierarchy(dtype=self.dtype)
        self.motion_data = motion(dtype=self.dtype)
        if path:
            self.load(path)
    
    def __update(self, frm):
        ch_index = 0
        for n in self.hierarchy_data:
            for ch_name in n.channels :
                if ch_name is 'position':
                    n.position.set_values(frm[ch_index])
                elif ch_name is 'rotation':
                    n.rotation.set_values(frm[ch_index])
                ch_index += 1

        self.hierarchy_data.updata_matrix()

    def print_tree(self):
        self.hierarchy_data.print_tree()

    def get_num_frames(self):
        return self.motion_data.frames
    
    def get_frame_time(self):
        return self.motion_data.frame_time

    def get_num_nodes(self):
        return len(self.hierarchy_data.nodes)

    def load(self, path):
        with open(path) as f:
            ls = [s.strip() for s in f.readlines()]  
            h_ind = ls.index('HIERARCHY')
            m_ind = ls.index('MOTION')
            self.hierarchy_data = hierarchy(bone_str=ls[h_ind+1:m_ind], dtype=self.dtype)
            self.motion_data = motion(ls[m_ind+1:], dtype=self.dtype)

    def __getitem__(self, key):
        frm = self.motion_data.frame_data[key]
        self.__update(frm)
        return self.hierarchy_data
    
    def __iter__(self):
        for frm in self.motion_data.frame_data:
            self.__update(frm)
            yield self.hierarchy_data

