""" env data analysis
    this program takes output data from Ferret and processes for insert into a relational database format
    it will essentially convert an N x N matrix of data into an N x 3 list of data
    methods will be built for wind stress curl, sst, and chla
    
converts this matrix:
['head1', 'a', 'b', 'c']
['val1', '1', '7', '9']
['val2', '8', '3', '4']
['val3', '9', '1', '1']

into this:

['val1', 'a', '1']
['val1', 'b', '7']
['val1', 'c', '9']
['val2', 'a', '8']
['val2', 'b', '3']
['val2', 'c', '4']
['val3', 'a', '9']
['val3', 'b', '1']
['val3', 'c', '1']
"""
# import connection
import os
import csv


def matrixToKeyKeyVal(mtrx):
    """ takes an NxN matrix where column 1 is headers and row 1 is also headers
        and converts it to an N X 3 matrix of the format header1, header2, value.
    """
    target = []
    rHead = [x.strip() for x in mtrx[0][1:]]
    for row in mtrx[1:]:
        cHead = row[0].strip()
        for idx, col in enumerate(row[1:]):
            target.append([cHead, rHead[idx], col.strip()])
    return target


def processWinStressCurl(infile, outfile):
    mtrx = []
    with open(infile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            mtrx.append(row)

    mtrx = matrixToKeyKeyVal(mtrx)

    with open(outfile, 'w') as f:
        writer = csv.writer(f)
        for row in mtrx:
            writer.writerow(row)


if __name__ == '__main__':
    curPath = os.path.dirname(os.path.abspath(__file__))
    print curPath
    processWinStressCurl(os.path.join(curPath, '../data/ferret_windcurl.csv'), os.path.join(curPath, '../data/mysql_windStressCurl.csv'))

    # m = [['head1', 'a', 'b', 'c'], ['val1', '1', '7', '9'], ['val2', '8', '3', '4'], ['val3', '9', '1', '1']]
    # print m
    # print matrixToKeyKeyVal(m)
