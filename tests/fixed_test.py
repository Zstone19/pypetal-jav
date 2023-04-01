import glob
import os
import shutil
import unittest

import numpy as np

import pypetal_jav.pipeline as pl


class TestJAVELIN(unittest.TestCase):

    def setUp(self):

        output_dir_og = 'for_jav/pypetal_out1/'
        output_dir = '.tmp/'
        line_names = ['continuum', 'yelm', 'zing']
        
        #Copy to new directory
        shutil.copytree( output_dir_og, output_dir)
        

        fixed1 = [1, 0,           0,   1, 1]
        p_fix1 = [0, np.log(275), 200, 0, 0]

        fixed2 = [1, 1, 0,   0,   1]
        p_fix2 = [0, 0, 150, 300, 0]


        javelin_params = {
            'nchain': 20,
            'nburn': 10,
            'nwalker': 10,
            'fixed': [fixed1, fixed2],
            'p_fix': [p_fix1, p_fix2]
        }

        lag_bounds = [ 'baseline', [-500, 500] ]

        #Run pypetal
        res = pl.run_pipeline(output_dir, line_names,
                              javelin_params=javelin_params,
                              lag_bounds=lag_bounds,
                              file_fmt='ascii',
                              threads=30)

        filenames = [output_dir + 'processed_lcs/' + x + '_data.dat' for x in line_names]

        self.filenames = filenames
        self.line_names = line_names
        self.res = res

        self.fixed = javelin_params['fixed']
        self.p_fix = javelin_params['p_fix']


    #Make chain is only one value for sigma and tau
    def test_chain(self):

        for j in range(20*10):
            #Yelm
            self.assertAlmostEqual( self.res[0]['tau'][j], np.exp(self.p_fix[0][1]), places=6 )
            self.assertAlmostEqual( self.res[0]['tophat_params'][0][j], self.p_fix[0][2], places=6 )

            #Zing
            self.assertAlmostEqual( self.res[1]['tophat_params'][0][j], self.p_fix[1][2], places=6 )
            self.assertAlmostEqual( self.res[1]['tophat_params'][1][j], self.p_fix[1][3], places=6 )


    def tearDown(self):
        if os.path.exists('.tmp/') and os.path.isdir('.tmp/'):
            shutil.rmtree('.tmp/')


if __name__ == '__main__':
    unittest.main()
