import glob
import os
import shutil
import unittest

import javelin.lcmodel
import javelin.zylc
import numpy as np

import pypetal_jav.pipeline as pl


class TestJAVELIN(unittest.TestCase):

    def setUp(self):

        output_dir_og = 'for_jav/pypetal_out1/'
        output_dir = '.tmp/'
        line_names = ['continuum', 'yelm', 'zing']
        
        #Copy to new directory
        shutil.copytree( output_dir_og, output_dir)

        params = {
            'nchain': 20,
            'nburn': 10,
            'nwalker': 10
        }
        lag_bounds = [ [-1000, 1000], [-500, 500] ]

        #Run pypetal
        res = pl.run_pipeline(output_dir, line_names,
                            javelin_params=params,
                            lag_bounds=lag_bounds,
                            file_fmt='ascii')

        filenames = [output_dir + 'processed_lcs/' + x + '_data.dat' for x in line_names]


        self.filenames = filenames
        self.line_names = line_names
        self.res = res




    def test_all(self):

        #################################################################################################
        # RES
        #################################################################################################
        #Make sure the lengths and keys of each of the resulting arrays are correct

        expected_keys = ['cont_hpd', 'tau', 'sigma', 'tophat_params', 'hpd',
                         'cont_model', 'rmap_model', 'cont_dat', 'tot_dat', 'bestfit_model']

        num_dicts = len(self.line_names) - 1
        self.assertEqual( num_dicts, len(self.res) )

        mc_length = 20*10

        #Make sure the keys of the output are correct
        for i in range(num_dicts):
            res_keys = list(self.res[i].keys())
            for key in expected_keys:
                self.assertIn( key, res_keys )


        #Make sure data types are correct
        for i in range(num_dicts):

            for j, key in enumerate(expected_keys):

                if key == 'cont_model':
                    self.assertIs( type(self.res[i][key]), javelin.lcmodel.Cont_Model )
                elif key == 'rmap_model':
                    self.assertIs( type(self.res[i][key]), javelin.lcmodel.Rmap_Model )
                elif (key == 'cont_dat') or (key == 'tot_dat') or (key == 'bestfit_model'):
                    self.assertIs( type(self.res[i][key]), javelin.zylc.LightCurve )
                else:
                    self.assertIs( self.res[i][key].dtype.type, np.float64 )


        #Make sure lengths of arrays are correct
        for i in range(num_dicts):
            self.assertEqual( len(self.res[i]['tau']), mc_length )
            self.assertEqual( len(self.res[i]['sigma']), mc_length )

            self.assertEqual( len(self.res[i]['tophat_params']), 3 )
            self.assertEqual( len(self.res[i]['tophat_params'][0]), mc_length )
            self.assertEqual( len(self.res[i]['tophat_params'][1]), mc_length )
            self.assertEqual( len(self.res[i]['tophat_params'][2]), mc_length )

            self.assertEqual( len(self.res[i]['cont_hpd']), 3 )
            self.assertEqual( len(self.res[i]['cont_hpd'][0]), 2 )

            self.assertEqual( len(self.res[i]['hpd']), 3 )
            self.assertEqual( len(self.res[i]['hpd'][0]), 5 )


        #Make sure that the LC objetcs have the right light curves
        x_cont, y_cont, yerr_cont = np.loadtxt( self.filenames[0], unpack=True, usecols=[0,1,2], delimiter=',' )
        for i in range(num_dicts):
            x, y, yerr = np.loadtxt(self.filenames[i+1], unpack=True, usecols=[0,1,2], delimiter=',' )

            for key in ['cont', 'tot']:

                #Continuum
                jav_x = self.res[i][ key + '_dat'].jlist[0]
                jav_y = self.res[i][ key + '_dat'].mlist[0] + self.res[i][ key + '_dat'].blist[0]
                jav_yerr = self.res[i][ key + '_dat'].elist[0]

                self.assertListEqual( list(x_cont), list(jav_x) )
                self.assertListEqual( list(yerr_cont), list(jav_yerr) )

                for j in range(len(y_cont)):
                    self.assertAlmostEqual( y_cont[j], jav_y[j], places=6 )


                #Line
                if key == 'tot':
                    jav_x = self.res[i][ key + '_dat'].jlist[1]
                    jav_y = self.res[i][ key + '_dat'].mlist[1] + + self.res[i][ key + '_dat'].blist[1]
                    jav_yerr = self.res[i][ key + '_dat'].elist[1]

                    self.assertListEqual( list(x), list(jav_x) )
                    self.assertListEqual( list(yerr), list(jav_yerr) )

                    for j in range(len(y)):
                        self.assertAlmostEqual( y[j], jav_y[j], places=6 )




        #Make sure that the LCModel objects have the right light curves
        for i in range(num_dicts):
            x, y, yerr = np.loadtxt(self.filenames[i+1], unpack=True, usecols=[0,1,2], delimiter=',')

            for key in ['cont', 'rmap']:

                #Continuum
                jav_x = self.res[i][ key + '_model'].zydata.jlist[0]
                jav_y = self.res[i][ key + '_model'].zydata.mlist[0] + self.res[i][ key + '_model'].zydata.blist[0]
                jav_yerr = self.res[i][ key + '_model'].zydata.elist[0]

                self.assertListEqual( list(x_cont), list(jav_x) )
                self.assertListEqual( list(yerr_cont), list(jav_yerr) )
                for j in range(len(y_cont)):
                    self.assertAlmostEqual( y_cont[j], jav_y[j], places=6 )


                #Line
                if key == 'rmap':
                    jav_x = self.res[i][ key + '_model'].zydata.jlist[1]
                    jav_y = self.res[i][ key + '_model'].zydata.mlist[1] + self.res[i][ key + '_model'].zydata.blist[1]
                    jav_yerr = self.res[i][ key + '_model'].zydata.elist[1]

                    self.assertListEqual( list(x), list(jav_x) )
                    self.assertListEqual( list(yerr), list(jav_yerr) )
                    for j in range(len(y)):
                        self.assertAlmostEqual( y[j], jav_y[j], places=6 )



        lag_bounds = [ [-1000, 1000], [-500, 500] ]
        #Make sure lag bounds worked
        for i in range(num_dicts):
            self.assertGreaterEqual( np.min(self.res[i]['tophat_params'][0]), lag_bounds[i][0] )
            self.assertLessEqual( np.max(self.res[i]['tophat_params'][0]), lag_bounds[i][1] )


        #################################################################################################
        # FILE LAYOUT
        #################################################################################################
        #Make sure the layout of the files is correct

        main_directories = glob.glob('.tmp/*/')
        subdirs = ['.tmp/continuum/', '.tmp/yelm/', '.tmp/zing/']

        mc_length = 20*10
        burn_length = 10*10

        #Make sure each line has a "javelin" subdirectory
        for fdir in subdirs[1:]:
            subdir_dirs = glob.glob(fdir + '*')
            self.assertIn( fdir + 'javelin' , subdir_dirs )

        #Make sure each "javelin" subdirectory has a ccf and dist file
        for i, fdir in zip([1,2], subdirs[1:]):
            files = glob.glob(fdir + 'javelin/*')
            for x in ['cont', 'rmap']:
                self.assertIn( fdir + 'javelin/' + 'burn_' + x + '.txt', files )
                self.assertIn( fdir + 'javelin/' + 'chain_' + x + '.txt', files )
                self.assertIn( fdir + 'javelin/' + 'logp_' + x + '.txt', files )

            self.assertIn( fdir + 'javelin/continuum_lc_fits.dat', files )
            self.assertIn( fdir + 'javelin/' + self.line_names[i] + '_lc_fits.dat', files )

            self.assertIn( fdir + 'javelin/cont_lcfile.dat', files )
            self.assertIn( fdir + 'javelin/' + self.line_names[i] + '_lcfile.dat', files )

            self.assertIn( fdir + 'javelin/javelin_bestfit.pdf', files )
            self.assertIn( fdir + 'javelin/javelin_corner.pdf', files )
            self.assertIn( fdir + 'javelin/javelin_histogram.pdf', files )




            #Make sure the lc files are correct
            xcont, ycont, yerrcont = np.loadtxt( self.filenames[0], unpack=True, usecols=[0,1,2], delimiter=',' )
            xline, yline, yerrline = np.loadtxt( self.filenames[i], unpack=True, usecols=[0,1,2], delimiter=',' )

            cont_dat = javelin.zylc.get_data( fdir + 'javelin/cont_lcfile.dat' )
            jav_x = cont_dat.jlist[0]
            jav_y = cont_dat.mlist[0] + cont_dat.blist[0]
            jav_yerr = cont_dat.elist[0]

            self.assertListEqual( list(xcont), list(jav_x) )
            self.assertListEqual( list(yerrcont), list(jav_yerr) )
            for j in range(len(ycont)):
                self.assertAlmostEqual( ycont[j], jav_y[j], places=6 )



            line_dat = javelin.zylc.get_data( fdir + 'javelin/' + self.line_names[i] + '_lcfile.dat' )
            jav_x = line_dat.jlist[0]
            jav_y = line_dat.mlist[0] + line_dat.blist[0]
            jav_yerr = line_dat.elist[0]

            self.assertListEqual( list(xline), list(jav_x) )
            self.assertListEqual( list(yerrline), list(jav_yerr) )
            for j in range(len(jav_x)):
                self.assertAlmostEqual( yline[j], jav_y[j], places=6 )


            #Make sure chain and burn files have correct length
            for x in ['cont', 'rmap']:
                for prefix in ['burn', 'chain', 'logp']:
                    chain = np.loadtxt( fdir + 'javelin/' + prefix + '_' + x + '.txt' )
                    self.assertEqual( len(chain), burn_length if prefix == 'burn' else mc_length )


        #Make sure the light curves get saved
        self.assertIn( '.tmp/light_curves/', main_directories )

        lc_files = glob.glob('.tmp/light_curves/*')
        for name in self.line_names:
            self.assertIn( '.tmp/light_curves/' + name + '.dat', lc_files )




        #################################################################################################
        # RES FILE MATCH
        #################################################################################################

        #Match dists
        for i in range(2):

            file_sig, file_tau, t, w, s = np.loadtxt( '.tmp/' + self.line_names[i+1] + '/javelin/chain_rmap.txt', unpack=True )
            file_sig = np.exp(file_sig)
            file_tau = np.exp(file_tau)
            file_tophat = [t, w, s]

            self.assertListEqual( list(file_sig), list(self.res[i]['sigma']) )
            self.assertListEqual( list(file_tau), list(self.res[i]['tau']) )
            for j in range(3):
                self.assertListEqual( list(file_tophat[j]), list(self.res[i]['tophat_params'][j]) )


    def tearDown(self):
        if os.path.exists('.tmp/') and os.path.isdir('.tmp/'):
            shutil.rmtree('.tmp/')


if __name__ == '__main__':
    unittest.main()
