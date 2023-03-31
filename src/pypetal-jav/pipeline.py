import os
import glob

import numpy as np

import pypetal_jav.modules as modules

from pypetal_jav import defaults
from pypetal_jav.petalio import make_directories
from pypetal_jav.utils import fix_jav_params_after_ufj



def run_pipeline(output_dir, line_names=None,
                 javelin_params={}, use_for_javelin=False, 
                 drw_rej_res={}, **kwargs):


    output_dir = os.path.abspath(output_dir) + r'/'

    #pyPetal will create the output directory if it doesn't exist
    #Also will create the javelin subdirectories
    if not os.path.exists(output_dir):
        raise Exception('This assumes that pypetal.pipeline.run_pipeline has already been run.')

    if line_names is None:
        light_curve_fnames = glob.glob(output_dir + 'light_curves/*.dat')
        line_names = [os.path.basename(fname).split('.')[0] for fname in light_curve_fnames]


    #Look for light curve filenames
    line_fnames = []
    if output_dir + 'processed_lcs/' in glob.glob(output_dir +'*/'):
        fnames = [output_dir + 'processed_lcs/' + name + '_data.dat' for name in line_names]
    else:
        fnames = [output_dir + 'light_curves/' + name + '.dat' for name in line_names]

    cont_fname = fnames[0]
    line_fnames = fnames[1:]


    if type(line_fnames) is str:
        line_fnames = [line_fnames]


    #Read in general kwargs
    general_kwargs = defaults.set_general(kwargs, fnames)

    #Get "together"
    _, _, _, _, _, _, _, _, _, _, _, _, together, _ = defaults.set_javelin(javelin_params, len(fnames) )

    make_directories(output_dir, line_names, together)

    #Name lines if unnamed
    if line_names is None:
        line_names = np.zeros( len(line_fnames), dtype=str )
        for i in range(len(line_fnames)):
            line_names.append('Line {}'.format(i+1))


    if use_for_javelin:
        javelin_params = fix_jav_params_after_ufj(javelin_params, drw_rej_res)

    javelin_res = modules.javelin_tot(cont_fname, line_fnames, line_names, output_dir, general_kwargs, javelin_params)

    return javelin_res
