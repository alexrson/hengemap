import argparse
import numpy as np
import shapefile
import os
import matplotlib.pyplot as plt

"""
+proj=lcc +lat_1=41.71666666666667 +lat_2=42.68333333333333 +lat_0=41 +lon_0=-71.5 +x_0=200000 +y_0=750000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs
"""


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
    projection_file = in_file[:-4]+ '.prj'
    dbf_file = in_file[:-4]+ '.dbf'
    dbf = open(dbf_file, 'rb')
    assert os.path.exists(projection_file)
    sf = shapefile.Reader(shp=shp, dbf=dbf)
    fig1 = plt.figure()
    sp = fig1.add_subplot(1, 1, 1)
    simpleaxis(sp)
    point1_point2Tolen = {}
    all_lens = []
    min_len = 5
    for si,s in enumerate(sf.shapes()):
        for point1, point2 in zip(s.points, s.points[1:]):
            seg_len = euclidean_dist(point1, point2)
            if seg_len > min_len:
                all_lens.append(euclidean_dist(point1, point2))
    all_lens = sorted(all_lens)
    slope_points_len = []
    for si,s in enumerate(sf.shapes()):
        for point1, point2 in zip(s.points, s.points[1:]):
            seg_len = euclidean_dist(point1, point2)
            _slope = slope(point1, point2)
            slope_points_len.append((_slope, point1, point2, seg_len))
            if seg_len > min_len:
                norm_len = (1.0 * all_lens.index(seg_len) / len(all_lens)) **4.
                point1_point2Tolen[(point1, point2)] = seg_len
                color = (0.8 + 0.2*norm_len,0.8-0.8*norm_len,0.8-0.8*norm_len)
                color = 'bgry'[si % 4]
                sp.plot(zip(point1, point2)[0],
                        zip(point1, point2)[1],
                        marker=None,
                        color=color)
            else:
                sp.plot(zip(point1, point2)[0],
                        zip(point1, point2)[1],
                        color=(0.8,0.8,0.8))
    slope_points_len = sorted(slope_points_len)
    fig1.savefig('map.pdf')
    fig2 = plt.figure()
    sp = fig2.add_subplot(1,1,1)
    simpleaxis(sp)
    slopes = zip(*slope_points_len)[0]
    slopes = filter(None, slopes)
    angles = map(np.arctan, slopes)
    n, bins = np.histogram(angles, bins=90)
    sp.bar(bins[1:], n, width=bins[1]-bins[0],facecolor='#2CB4AC', edgecolor='#2CB4AC')
    sp.set_xlim([-3.14/2,3.14/2])
    sp.set_xticks([-1.57, 0, 1.57])
    sp.set_xticklabels([-45,0,45])
    fig2.savefig('angle_hist.png')
    with open('cambridge_segments.tsv', 'w') as of:
        of.write('angle\tx1\ty1\tx\ty2\tlength\n')
        for slope_, p1, p2, length in slope_points_len:
            p1 = list(p1)
            p2 = list(p2)
            if slope_:
                angle = np.arctan(slope_) * 57.2957795
            else:
                angle = -90
            of.write('\t'.join(map(str,[angle] + p1 + p2 + [length])) + '\n')




def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')
    run_args = subparsers.add_parser('run', help='Analyze Cambridge')
    run_args.add_argument('--in-file', dest='in_file', required=True, help='*.shp')
    args = parser.parse_args()
    analyze_shapefile(args.in_file)


if __name__ == '__main__':
    main()
