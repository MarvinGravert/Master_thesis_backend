"""Optimize the Transformation using non linear optimization
Point set A and point set B shoudl be provided to this function as well
as the matrix R and vector t 

The relation should be B_i=R@A_i+t aka A->B

The called module will return a R*,t* optimized regarding some nonlinear
optimization algorithm

For the moment it is assumed to be an unbounded problem.
"""

import numpy as np
from scipy.optimize import least_squares
from loguru import logger
"""
The problem we are trying to solve is argmin (sum_i->m[(B_i- F(A_i,X))²])
see: https://en.wikipedia.org/wiki/Levenberg%E2%80%93Marquardt_algorithm

To do this we use the least_squares solver from scipy:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html

We need to provide a function and initial values.
The function should be F(X, *args,**kwargs)->residulas

This module allows to optimize the entire transformation T=(R,t), just the rotation R
or just the translation t. 
For the part that is not optimized, the initial value is used throughout the optimisation
and returned at the end

The initial value X depends on the optimisation case but residuals necessary for the function
are calculated via the following function
B_i-R@A_i+t across all N point correspondances i=1,2,...,N

Hence, X is either (9+3)x1, 9x1 or 3x1  vector and residual is a Nx1 vector

"""
class Optimizer():
    def __init__(self,
                point_set_1:np.ndarray,
                point_set_2:np.ndarray,
                R:np.ndarray,
                t:np.ndarray
                ):
        logger.info("Initialising the optimizer")
        self._point_set_1=point_set_1
        self._point_set_2=point_set_2
        self._R:np.ndarray=R
        self._t:np.ndarray=t
    def _calc_residuals(self,X:np.ndarray)->np.ndarray:
        """Calculates the resuldials across the point correspondances


        Args:
            X (np.ndarray): 12x1 vector containing row major flattend R and t e.g [r11,r12,r13,r21,...,t1,t2,t3]

        Returns:
            np.ndarray: Nx1 vectors containing the residuals 
        """
        residuals=[]
        ## Set R,t depending on what optimisation case
        ## Case is clear via the length#TODO: ensure dass der gesamte Vektor zurückkommt und nicht die Norm 
        if len(X)==12:
            R:np.ndarray=X[0:9].reshape([3,3])
            t:np.ndarray=X[9:].reshape([3,1])
        elif len(X)==9:
            R:np.ndarray=X.reshape([3,3])
            t:np.ndarray=self._t
        elif len(X)==3:
            R:np.ndarray=self._R
            t:np.ndarray=X.reshape([3,1])

        for vec_A, vec_B in zip(self._point_set_1,self._point_set_2):
            vec_A_in_B=R@vec_A.reshape([3,1])+t
            # residuals.append(np.linalg.norm(vec_B-vec_A_in_B))
            temp=(vec_B.reshape([3,1])-vec_A_in_B)
            for e in temp:
                residuals.append(float(e))
        return np.array(residuals)
    
    
    def find_optimal_transformation(self):
        logger.info("Starting searching for optimal transformation")
        x_0=np.vstack([self._R,self._t.flatten()]).flatten()
        res=least_squares(self._calc_residuals, x_0)
        return res.x[0:9].reshape([3,3]), res.x[9:].reshape([3,1])

    def find_optimal_rotation(self):
        logger.info("Starting searching for optimal rotation")
        x_0=self._R.flatten()
        res=least_squares(self._calc_residuals, x_0)
        return res.x.reshape([3,3]), self._t

    def find_optimal_translation(self):
        logger.info("Starting searching for optimal translation")
        x_0=self._t.flatten()
        res=least_squares(self._calc_residuals, x_0)
        return self._R, res.x.reshape([3,1])
    
    def correct_rotation_matrix(self, R:np.ndarray)->np.ndarray:
        """corrects the rotation matrix to be an orthogonal matrix

            The optimization doesnt gurantee a orthogonal Matrix. Infact, there 
            are no gurantee on the form of the matrix. Alas, this module uses svd
            to find the nearest orthogonal matrix

            Alternative: TODO: Verify scipy.spatial as an option to find closest rotation
        Args:   
            R (np.ndarray): matrix returned from optimization

        Raises:
            Exception: if determinate of after svd is not 1 or -1 

        Returns:
            np.ndarray: orthogonal matrix
        """
        u,sig,v=np.linalg.svd(R)
        R=u@v
        det_R=np.linalg.det(R)
        if np.isclose(det_R,-1):
            u[:,2]=-u[:,2]
            R=u@v
            return R
        elif np.isclose(det_R,1):
            return R
        else:
            raise Exception() 
        

if __name__=="__main__":
    pass