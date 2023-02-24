import os

import numpy as np
from astropy.table import Table

import pypetal-jav.detrending as dtr
import pypetal-jav.modules as modules

from pypetal-jav import defaults, weighting
from pypetal-jav.petalio import make_directories, write_data
from pypetal-jav.utils import fix_jav_params_after_ufj



def run_pipeline(output_dir, arg2, line_names=None,
                 javelin_params={}, use_for_javelin=False, 
                 drw_rej_res={}, **kwargs):


    output_dir = os.path.abspath(output_dir) + r'/'

    if arg2 is None:
        raise Exception('Please provide a list of light curve filenames or the light curves themselves')


    if not isinstance(arg2[0], str):
        os.makedirs( output_dir + 'input_lcs/', exist_ok=True )
        fnames = []

        for i in range( len(arg2) ):

            if i == 0:
                name = 'continuum'
            else:
                name = 'line{}'.format(i+1)

            write_data( arg2[i], output_dir + 'input_lcs/' + name + '.dat' )
            fnames.append( output_dir + 'input_lcs/' + name + '.dat' )

        fnames = np.array(fnames)
        kwargs['file_fmt'] = 'csv'
    else:
        fnames = arg2




    if len(fnames) < 2:
        print('ERROR: Requires at least two light curves to run pipeline.')
        return {}

    if len(line_names) != len(fnames):
        print('ERROR: Must have the same number of line names as light curves.')
        return {}


    cont_fname = fnames[0]
    line_fnames = fnames[1:]

    if type(line_fnames) is str:
        line_fnames = [line_fnames]


    #Read in general kwargs
    general_kwargs = defaults.set_general(kwargs, fnames)



    #Get "together"
    _, fixed, p_fix, _, _, _, _, _, _, _, _, _, together, rm_type = defaults.set_javelin(javelin_params, fnames)


    javelin_params['fixed'] = fixed
    javelin_params['p_fix'] = p_fix

    if rm_type == 'spec':
        if together:
            nfixed = 2 + 3*( len(fnames)-1 )
        else:
            nfixed = 5
    elif rm_type == 'phot':
        nfixed = 6



    #Name lines if unnamed
    if line_names is None:
        line_names = np.zeros( len(line_fnames), dtype=str )
        for i in range(len(line_fnames)):
            line_names.append('Line {}'.format(i+1))


    if use_for_javelin:
        javelin_params = fix_jav_params_after_ufj(javelin_params, drw_rej_res)


    javelin_res = modules.javelin_tot(cont_fname, line_fnames, line_names, output_dir, general_kwargs, javelin_params)

    return javelin_res
