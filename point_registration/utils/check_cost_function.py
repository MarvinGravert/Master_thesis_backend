"""This module checks the results of the point alignment in the sense of the least square method

It takes both point sets and the R, t from the point alignment algorithm and computes the least square distance

"""
import numpy as np
def check_adjust_dimension(point_set: np.ndarray) -> np.ndarray:
    # check data transmitted in column matrix or in row matrix and transform
    # into column matrix nx3
    row, column = point_set.shape
    if row == 3 and column >= 3:
        # column matrix
        return point_set.T
    elif row >= 3 and column == 3:
        # row matrix
        return point_set
    else:
        raise Exception("Data matrix not correct format")
def check_cost_function(point_set_1:np.ndarray,
            point_set_2:np.ndarray,
            R:np.ndarray,t:np.ndarray)->float:
    """module transforms point_set_1 into the frame of the second point set 
    using R, t and checks the least squared distance between the correspondances

    Args:
        point_set_1 (np.ndarray): point set nx3 or 3xn
        point_set_2 (np.ndarray): point set nx3 or 3xn
        R (np.ndarray): Rotationsmatrix from 1->2 3x3
        t (np.ndarray): translation vector 3x1

    Returns:
        float: sum of the normed distances 
    """

    #first transform into nx3 because i like this better also a bit easier looping
    p1= check_adjust_dimension(point_set=point_set_1)
    p2= check_adjust_dimension(point_set=point_set_2)
    #each row is corresponding to another one in the other point set
    sum=0
    length=p1.shape[0]
    for vec1,vec2 in zip(p1,p2):
        temp=R@vec1.reshape([3,1]) +t.reshape([3,1]) #transform vec1 into frame of vec2
        diff=np.linalg.norm(vec2-temp)
        sum+=diff
    return sum/length