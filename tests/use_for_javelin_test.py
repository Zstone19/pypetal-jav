import os
import shutil
import unittest

import numpy as np

import pypetal_jav.pipeline as pl


class TestDrwRej(unittest.TestCase):

    def setUp(self):

        output_dir_og = 'for_jav/pypetal_out1/'
        line_names = ['continuum', 'yelm', 'zing']
        
        #Copy to new directory
        shutil.copytree( output_dir_og, '.tmp/')
        output_dir = '.tmp/'        


        #Javelin parameters
        fixed1 = [1, 0,           1, 0,  1]
        p_fix1 = [0, np.log(300), 0, 20, 0]
        fixed2 = None
        p_fix2 = None

        javelin_params = {
            'nchain': 20,
            'nburn': 10,
            'nwalker': 10,
            'fixed': [fixed1, fixed2],
            'p_fix': [p_fix1, p_fix2]
        }

        lag_bounds = [-1000, 1000]
        
        
        #Get DRW rejection results
        reject_data = [True, False, False]
        taus = []
        sigs = []
        jits = []
        
        for x, rej in zip(line_names, reject_data):
            if rej:
                s, t, j = np.loadtxt( output_dir + x + '/drw_rej/' + x + '_chain.dat',
                                      unpack=True, usecols=[0,1,2], delimiter=',')
                
                taus.append(t)
                sigs.append(s)
                jits.append(j)
                
        drw_rej_res = {
            'reject_data': reject_data,
            'taus': taus,
            'sigmas': sigs,
            'jitters': jits
        }


        #Run pypetal
        res = pl.run_pipeline(output_dir, line_names,
                              javelin_params=javelin_params, use_for_javelin=True,
                              drw_rej_res=drw_rej_res,
                              lag_bounds=lag_bounds,
                              file_fmt='csv')

        filenames = [output_dir + 'light_curves/' + x + '.dat' for x in line_names]

        self.filenames = filenames
        self.line_names = line_names
        self.res = res


    #Make chain is only one value for sigma and tau
    #Make sure the fixed value is from the DRW rejection, and not from "fixed/p_fix"
    def test_chain(self):
        output_dir = '.tmp/'
        s, t, j = np.loadtxt(output_dir + self.line_names[0] + '/drw_rej/' + self.line_names[0] + '_chain.dat', 
                                unpack=True, usecols=[0,1,2], delimiter=',')        
        
        drw_sigma = np.median(s)
        drw_tau = np.median(t)

        for i in range(len(self.filenames)-1):
            for j in range(20*10):
                self.assertAlmostEqual( self.res[i]['sigma'][j], drw_sigma, places=6 )
                self.assertAlmostEqual( self.res[i]['tau'][j], drw_tau, places=6 )  

        for j in range(20*10):              
            self.assertAlmostEqual( self.res[0]['tophat_params'][1][j], 20, places=6 )


    def tearDown(self):
        if os.path.exists('.tmp/') and os.path.isdir('.tmp/'):
            shutil.rmtree('.tmp/')



if __name__ == '__main__':
    unittest.main()
