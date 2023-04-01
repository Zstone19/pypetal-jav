import glob
import os
import shutil
import unittest

import javelin.lcmodel
import javelin.zylc
import numpy as np

import pypetal_jav.pipeline as pl


class TestJavelinTogether(unittest.TestCase):

    def setUp(self):

        output_dir_og = 'for_jav/pypetal_out1/'
        output_dir = '.tmp/'
        line_names = ['continuum', 'yelm', 'zing']
        
        #Copy to new directory
        shutil.copytree( output_dir_og, output_dir)

        params = {
            'nchain': 30,
            'nburn': 20,
            'nwalker': 20,
            'together': True
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

        mc_length = 30*20

        #Make sure the keys of the output are correct
        res_keys = list(self.res.keys())
        for key in expected_keys:
            self.assertIn( key, res_keys )


        #Make sure data types are correct
        for j, key in enumerate(expected_keys):
            if key == 'cont_model':
                self.assertIs( type(self.res[key]), javelin.lcmodel.Cont_Model )
            elif key == 'rmap_model':
                self.assertIs( type(self.res[key]), javelin.lcmodel.Rmap_Model )
            elif (key == 'cont_dat') or (key == 'tot_dat') or (key == 'bestfit_model'):
                self.assertIs( type(self.res[key]), javelin.zylc.LightCurve )
            else:
                self.assertIs( self.res[key].dtype.type, np.float64 )


        #Make sure lengths of arrays are correct
        self.assertEqual( len(self.res['tau']), mc_length )
        self.assertEqual( len(self.res['sigma']), mc_length )

        self.assertEqual( len(self.res['tophat_params']), 6 )
        for i in range(6):
            self.assertEqual( len(self.res['tophat_params'][i]), mc_length )

        self.assertEqual( len(self.res['cont_hpd']), 3 )
        self.assertEqual( len(self.res['cont_hpd'][0]), 2 )

        self.assertEqual( len(self.res['hpd']), 3 )
        self.assertEqual( len(self.res['hpd'][0]), 8 )






        #Make sure that the LC objetcs have the right light curves
        x_cont, y_cont, yerr_cont = np.loadtxt( self.filenames[0], unpack=True, usecols=[0,1,2], delimiter=',' )

        #cont_dat
        jav_x = self.res['cont_dat'].jlist[0]
        jav_y = self.res['cont_dat'].mlist[0] + self.res[ 'cont_dat'].blist[0]
        jav_yerr = self.res['cont_dat'].elist[0]

        self.assertListEqual( list(x_cont), list(jav_x) )
        self.assertListEqual( list(yerr_cont), list(jav_yerr) )
        for j in range(len(y_cont)):
            self.assertAlmostEqual( y_cont[j], jav_y[j], places=6 )


        #Tot_dat
        jav_x = self.res['tot_dat'].jlist[0]
        jav_y = self.res['tot_dat'].mlist[0] + self.res[ 'tot_dat'].blist[0]
        jav_yerr = self.res['tot_dat'].elist[0]

        self.assertListEqual( list(x_cont), list(jav_x) )
        self.assertListEqual( list(yerr_cont), list(jav_yerr) )
        for j in range(len(y_cont)):
            self.assertAlmostEqual( y_cont[j], jav_y[j], places=6 )

        for i in range(1, len(self.filenames)):
            x, y, yerr = np.loadtxt(self.filenames[i], unpack=True, usecols=[0,1,2], delimiter=',')

            jav_x = self.res['tot_dat'].jlist[i]
            jav_y = self.res['tot_dat'].mlist[i] + + self.res[ 'tot_dat'].blist[i]
            jav_yerr = self.res['tot_dat'].elist[i]

            self.assertListEqual( list(x), list(jav_x) )
            self.assertListEqual( list(yerr), list(jav_yerr) )

            for j in range(len(y)):
                self.assertAlmostEqual( y[j], jav_y[j], places=6 )







        #Make sure that the LCModel objects have the right light curves

        #Cont_Model
        jav_x = self.res[ 'cont_model'].zydata.jlist[0]
        jav_y = self.res[ 'cont_model'].zydata.mlist[0] + self.res[ 'cont_model'].zydata.blist[0]
        jav_yerr = self.res[ 'cont_model'].zydata.elist[0]

        self.assertListEqual( list(x_cont), list(jav_x) )
        self.assertListEqual( list(yerr_cont), list(jav_yerr) )
        for j in range(len(y_cont)):
            self.assertAlmostEqual( y_cont[j], jav_y[j], places=6 )


        #Rmap_Model
        jav_x = self.res[ 'rmap_model'].zydata.jlist[0]
        jav_y = self.res[ 'rmap_model'].zydata.mlist[0] + self.res[ 'rmap_model'].zydata.blist[0]
        jav_yerr = self.res[ 'rmap_model'].zydata.elist[0]

        self.assertListEqual( list(x_cont), list(jav_x) )
        self.assertListEqual( list(yerr_cont), list(jav_yerr) )
        for j in range(len(y_cont)):
            self.assertAlmostEqual( y_cont[j], jav_y[j], places=6 )



        for i in range(1, len(self.filenames)):
            x, y, yerr = np.loadtxt(self.filenames[i], unpack=True, usecols=[0,1,2], delimiter=',')

            jav_x = self.res[ 'rmap_model'].zydata.jlist[i]
            jav_y = self.res[ 'rmap_model'].zydata.mlist[i] + self.res[ 'rmap_model'].zydata.blist[i]
            jav_yerr = self.res[ 'rmap_model'].zydata.elist[i]

            self.assertListEqual( list(x), list(jav_x) )
            self.assertListEqual( list(yerr), list(jav_yerr) )
            for j in range(len(y)):
                self.assertAlmostEqual( y[j], jav_y[j], places=6 )



        lag_bounds = [ [-1000, 1000], [-500, 500] ]
        #Make sure lag bounds worked
        for i in range(len(self.filenames)-1):
            self.assertGreaterEqual( np.min(self.res['tophat_params'][3*i]), lag_bounds[i][0] )
            self.assertLessEqual( np.max(self.res['tophat_params'][3*i]), lag_bounds[i][1] )



        #################################################################################################
        # FILE LAYOUT
        #################################################################################################
         #Make sure the layout of the files is correct

        main_directories = glob.glob('.tmp/*/')

        mc_length = 30*20
        burn_length = 20*20

        #Make sure "javelin" subdirectory has chain and burn files
        files = glob.glob('.tmp/javelin/*')
        for x in ['cont', 'rmap']:
            self.assertIn( '.tmp/javelin/burn_' + x + '.txt', files )
            self.assertIn( '.tmp/javelin/chain_' + x + '.txt', files )
            self.assertIn( '.tmp/javelin/logp_' + x + '.txt', files )

        for name in self.line_names:
            self.assertIn( '.tmp/javelin/' + name + '_lc_fits.dat', files )

        self.assertIn( '.tmp/javelin/cont_lcfile.dat', files )
        for name in self.line_names[1:]:
            self.assertIn( '.tmp/javelin/' + name + '_lcfile.dat', files )

        self.assertIn( '.tmp/javelin/javelin_bestfit.pdf', files )
        self.assertIn( '.tmp/javelin/javelin_corner.pdf', files )
        self.assertIn( '.tmp/javelin/javelin_histogram.pdf', files )




        #Make sure the lc files are correct
        xcont, ycont, yerrcont = np.loadtxt( self.filenames[0], unpack=True, usecols=[0,1,2], delimiter=',' )

        cont_dat = javelin.zylc.get_data( '.tmp/javelin/cont_lcfile.dat' )
        jav_x = cont_dat.jlist[0]
        jav_y = cont_dat.mlist[0] + cont_dat.blist[0]
        jav_yerr = cont_dat.elist[0]

        self.assertListEqual( list(xcont), list(jav_x) )
        self.assertListEqual( list(yerrcont), list(jav_yerr) )
        for j in range(len(ycont)):
            self.assertAlmostEqual( ycont[j], jav_y[j], places=6 )





        for i in range(1, len(self.filenames)):
            xline, yline, yerrline = np.loadtxt( self.filenames[i], unpack=True, usecols=[0,1,2], delimiter=',' )
            line_dat = javelin.zylc.get_data( '.tmp/javelin/' + self.line_names[i] + '_lcfile.dat' )

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
                chain = np.loadtxt( '.tmp/javelin/' + prefix + '_' + x + '.txt' )
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
        file_sig, file_tau, t1, w1, s1, t2, w2, s2 = np.loadtxt( '.tmp/javelin/chain_rmap.txt', unpack=True )
        file_sig = np.exp(file_sig)
        file_tau = np.exp(file_tau)
        file_tophat = [t1, w1, s1, t2, w2, s2]

        self.assertListEqual( list(file_sig), list(self.res['sigma']) )
        self.assertListEqual( list(file_tau), list(self.res['tau']) )
        for j in range(6):
            self.assertListEqual( list(file_tophat[j]), list(self.res['tophat_params'][j]) )


    def tearDown(self):
        if os.path.exists('.tmp/') and os.path.isdir('.tmp/'):
            shutil.rmtree('.tmp/')


if __name__ == '__main__':
    unittest.main()
