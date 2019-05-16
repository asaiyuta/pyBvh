# pyBvh
decode bvh and calculate coordinates of each node😄

## Requirement
+ numpy  
+ matplotlib (it does not have to be for drawing in sample.py)

## Usage
so simple😄😄😄
```Python
mocap = bvh("path_to_bvhfile.bvh")
mocap.print_tree() #print hierarchy tree

bone = mocap[frame] #get hierarchy at frame
for n in bone:
  pos = n.global_matrix.getTranslate() #global position
  name = n.name #node name
```
