from collections import namedtuple
from accumulate_segments import euclidean_dist


Seg = namedtuple('Set', ['angle','p1','p2','length'])


def in_line(seg1, seg2):
    if abs(seg1.angle - seg2.angle) > 1:
        return False
    d_thresh = 3.
    pairs = [
        (seg1.p1, seg2.p1),
        (seg1.p1, seg2.p2),
        (seg1.p2, seg2.p1),
        (seg1.p2, seg2.p2),
    ]
    for pair in pairs:
        if euclidean_dist(*pairs) < d_thresh:
            return True
    return False

angle_ps_len = []
with open('cambridge_segments.tsv') as fp:
    for line in fp:
        if line.startswith('an'):
            continue
        angle,x1,y1,x2,y2,length = map(float, line.split())
        angle_ps_len.append(Seg(angle, (x1,y1), (x2,y2), length))
