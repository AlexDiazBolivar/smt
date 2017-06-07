"""
Author: Dr. Mohamed Amine Bouhlel <mbouhlel@umich.edu>
        Dr. Nathalie.bartoli      <nathalie@onera.fr>

TO DO:
- define outputs['sol'] = self.sol
"""

from __future__ import division

import numpy as np
import scipy
from smt.sm import SM
from smt.utils.caching import cached_operation

class PA2(SM):

    """
    Square polynomial approach
    """

    def _declare_options(self):
        super(PA2, self)._declare_options()
        declare = self.options.declare

        declare('name', 'PA2', types=str,
                desc='Squared polynomial interpolant')
        declare('data_dir', values=None, types=str,
                desc='Directory for loading / saving cached data; None means do not save or load')

    ############################################################################
    # Model functions
    ############################################################################

    def _new_train(self):

        """
        Train the model
        """

        if 0 in self.training_points['exact']:
            x = self.training_points['exact'][0][0]
            y = self.training_points['exact'][0][1]

        if x.shape[0] < (self.dim+1)*(self.dim+2)/2.:
            raise Exception("Number of training points should be greater or equal to %d."
                            % ((self.dim+1)*(self.dim+2)/2.))

        X = self.respoSurf(x)
        self.coef = np.dot(np.linalg.inv(np.dot(X.T,X)),(np.dot(X.T,y)))

    def _train(self):
        """
        Train the model
        """
        inputs = {'self': self}
        with cached_operation(inputs, self.options['data_dir']) as outputs:
            if outputs:
                self.sol = outputs['sol']
            else:
                self._new_train()
                #outputs['sol'] = self.sol
        

    def respoSurf(self,x):

        """
        Build the response surface of degree 2

        argument
        -----------
        x : np.ndarray [nt, dim]
            Training points

        Returns
        -------
        M : np.ndarray
            Matrix of the surface
        """

        dim = x.shape[1]
        n = x.shape[0]
        n_app = int(scipy.special.binom(dim+2, dim))
        M = np.zeros((n_app,n))
        x = x.T
        M[0,:] = np.ones((1,n))
        for i in range(1,dim+1):
            M[i,:] = x[i-1,:]
        for i in range(dim+1,2*dim+1):
            M[i,:]=x[i-(dim+1),:]**2
        for i in range(dim-1):
            for j in range(i+1,dim):
                k = int(2*dim+2+(i)*dim-((i+1)*(i))/2+(j-(i+2)))
                M[k,:] = x[i,:]*x[j,:]

        return M.T

    def _predict(self, x, kx):
        """
        Evaluate the surrogate model at x.

        Parameters
        ----------
        x: np.ndarray[n_eval,dim]
        An array giving the point(s) at which the prediction(s) should be made.
        kx : int or None
        None if evaluation of the interpolant is desired.
        int  if evaluation of derivatives of the interpolant is desired
             with respect to the kx^{th} input variable (kx is 0-based).

        Returns
        -------
        y : np.ndarray[n_eval,1]
        - An array with the output values at x.
        """

        X = self.respoSurf(x)
        y = np.dot(X,self.coef).T

        return y
