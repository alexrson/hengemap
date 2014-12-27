import argparse
from collections import namedtuple
from collections import deque
import matplotlib.pyplot as plt
import numpy as np
from operator import attrgetter
import shapefile


ANGLE_THRESH = 4.  # Degrees
D_THRESH = 6.  # Lambert_Conformal_Conic (I literally can't even...)
MIN_LEN = 600
colors = [plt.cm.jet(i/8.) for i in range(9)]
Seg = namedtuple('Seg', ['angle','p1','p2','length'])


def arctan(slope_):
    if slope_:
        angle = np.arctan(slope_) * 57.2957795
    else:
        angle = -90
    return angle


def in_line(seg1, seg2):
    if abs(seg1.angle - seg2.angle) > ANGLE_THRESH:
        return 0
    d_thresh = 3.
    pairs = [
        (seg1.p1, seg2.p1),
        (seg1.p1, seg2.p2),
        (seg1.p2, seg2.p1),
        (seg1.p2, seg2.p2),
    ]
    for pair_i, pair in enumerate(pairs):
        if euclidean_dist(*pair) < d_thresh:
            if pair_i in [0, 1]:
                return 1  # append seg2 to right
            else:
                return -1  # append seg2 to left
    return 0


def write_segs(segs):
    with open('cambridge_segments.tsv', 'w') as of:
        of.write('angle\tx1\ty1\tx\ty2\tlength\n')
        for slope_, p1, p2, length in segs:
            p1 = list(p1)
            p2 = list(p2)
            angle = arctan(slope_)
            of.write('\t'.join(map(str,[angle] + p1 + p2 + [length])) + '\n')


def read_segs():
    segs = []
    with open('cambridge_segments.tsv') as fp:
        for line in fp:
            if line.startswith('an'):
                continue
            angle, x1, y1, x2, y2, length = map(float, line.split())
            segs.append(Seg(angle, (x1, y1), (x2, y2), length))
    return segs


def build_lines(segs=None):
    """
       This function has three nested while loops and uses deques. Lol.
    """
    segs = segs or read_segs()
    lines = []  # list of deque of segs
    while segs:
        deq = deque([segs.pop(0)])
        line_changed = True
        while line_changed:
            i = 0
            line_changed = False
            while len(segs) > i and segs[i].angle - deq[-1].angle < ANGLE_THRESH:
                match1 = in_line(deq[0], segs[i])
                match2 = in_line(deq[-1], segs[i])
                if match1 or match2:
                    line_changed = True
                    if match1 == -1 or match2 == -1:
                        deq.appendleft(segs.pop(i))
                    elif match1 == 1 or match2 == 1:
                        deq.append(segs.pop(i))
                else:
                    i += 1
        length = sum([s.length for s in deq])
        if length > MIN_LEN:
            lines.append(deq)
    write_lines(lines)
    return lines


def write_lines(lines):
    with open('lines.txt', 'w') as of:
        for line_i, line in enumerate(lines):
            length = sum([s.length for s in line])
            of.write('LINE: %i\t%f\n' % (line_i, length))
            for seg in line:
                of.write('\t'.join(
                    [seg.p1[0], seg.p1[1], seg.p2[0], seg.p2[1]]) + '\n')


def simpleaxis(sp):
    sp.spines['top'].set_visible(False)
    sp.spines['right'].set_visible(False)
    sp.get_xaxis().tick_bottom()
    sp.get_yaxis().tick_left()


def slope(point1, point2):
    if (point2[0] - point1[0]):
        return (point2[1] - point1[1]) / (point2[0] - point1[0])
    else:
        return None


def euclidean_dist(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


def analyze_shapefile(in_file):
    """ as """
    shp = open(in_file, 'rb')
    dbf_file = in_file[:-4]+ '.dbf'
    dbf = open(dbf_file, 'rb')
    sf = shapefile.Reader(shp=shp, dbf=dbf)
    fig1 = plt.figure()
    sp = fig1.add_subplot(1, 1, 1)
    simpleaxis(sp)
    segs = []
    for si, s in enumerate(sf.shapes()):
        for point1, point2 in zip(s.points, s.points[1:]):
            seg_len = euclidean_dist(point1, point2)
            _slope = slope(point1, point2)
            angle = arctan(_slope)
            segs.append(Seg(angle, point1, point2, seg_len))
            color = (0.9, 0.9, 0.9)
            sp.plot(zip(point1, point2)[0],
                    zip(point1, point2)[1],
                    marker=None,
                    color=color)
    segs = sorted(segs, key=attrgetter('angle'))
    write_segs(segs)
    lines = build_lines(segs)
    for line_i, line in enumerate(lines):
        color = colors[line_i % len(colors)]
        for seg in line:
            sp.plot([seg.p1[0], seg.p2[0]],
                    [seg.p1[1], seg.p2[1]],
                    marker=None,
                    color=color)
    sp.set_title('Henges of Cambridge, MA')
    fig1.savefig('map.pdf')


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')
    run_args = subparsers.add_parser('run', help='Analyze Cambridge')
    run_args.add_argument('--in-file', dest='in_file', required=True, help='*.shp')
    args = parser.parse_args()
    analyze_shapefile(args.in_file)


if __name__ == '__main__':
    main()
