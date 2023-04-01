import glob
import os
import shutil
import unittest

import numpy as np

import javelin.lcmodel
import pypetal_jav.pipeline as pl


class TestJAVELIN(unittest.TestCase):

    def setUp(self):

        output_dir_og = 'for_jav/pypetal_out1/'
        output_dir = '.tmp/'
        line_names = ['continuum', 'yelm', 'zing']
        
        #Copy to new directory
        shutil.copytree( output_dir_og, output_dir)


        params = {
            'nchain': 40,
            'nburn': 20,
            'nwalker': 20,
            'rm_type': "phot",
            'together': True
        }

        lag_bounds = [-500, 500]

        #Run pypetal
        res = pl.run_pipeline(output_dir, line_names,
                              javelin_params=params,
                              lag_bounds=lag_bounds,
                              file_fmt='ascii',
                              threads=40)

        filenames = [output_dir + 'processed_lcs/' + x + '_data.dat' for x in line_names]

        self.filenames = filenames
        self.line_names = line_names
        self.res = res

        self.mc_length = params['nchain'] * params['nwalker']



    def test_pmap(self):

        #Make sure it sets together=False
        self.assertNotIn( '.tmp/javelin/', glob.glob('.tmp/*/') )

        #Make sure it returns a Pmap_Model object
        for i in range(len(self.line_names[1:])):
            self.assertIs( type(self.res[i]['rmap_model']), javelin.lcmodel.Pmap_Model)

        #Make sure there are 4 tophat parameters
        for i in range(len(self.line_names[1:])):
            self.assertEqual( len(self.res[i]['tophat_params']), 4)
            for j in range(4):
                self.assertEqual( len(self.res[i]['tophat_params'][j]), self.mc_length)


        #Make sure chain file is right
        for i in range(len(self.line_names[1:])):
            file_sig, file_tau, t, w, s, a = np.loadtxt( '.tmp/' + self.line_names[i+1] + '/javelin/chain_rmap.txt', unpack=True )
            file_sig = np.exp(file_sig)
            file_tau = np.exp(file_tau)
            file_tophat = [t, w, s, a]

            self.assertListEqual( list(file_sig), list(self.res[i]['sigma']) )
            self.assertListEqual( list(file_tau), list(self.res[i]['tau']) )
            for j in range(len(file_tophat)):
                self.assertListEqual( list(file_tophat[j]), list(self.res[i]['tophat_params'][j]) )



    def tearDown(self):
        if os.path.exists('.tmp/') and os.path.isdir('.tmp/'):
            shutil.rmtree('.tmp/')


if __name__ == '__main__':
    unittest.main()