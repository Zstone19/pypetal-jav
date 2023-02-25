import numpy as np




def make_directories(output_dir, line_names, together):

    #Create subdirectories for each line and javelin
    for i in range(len(line_names)):
        os.makedirs( output_dir + line_names[i], exist_ok=True )

    for i in range(len(line_names)-1):

        if together:
            os.makedirs( output_dir + 'javelin/', exist_ok=True )
        else:
            os.makedirs( output_dir + line_names[i+1] + '/javelin', exist_ok=True )

    return



def write_data(arr, fname, header=None):

    arr = np.array(arr, dtype=object)

    ndim = len( arr.shape )
    assert ndim <= 2


    if ndim == 2:
        cols = len(arr)
        rows = len(arr[0])

        with open(fname, "w") as file:

            if header is not None:
                file.write(header + "\n")

            for i in range(rows):

                string = "{},".format(arr[0][i])
                for j in range(1, cols-1):
                    string += "{},".format(arr[j][i])

                string += "{}\n".format(arr[-1][i])

                file.write(string)

    elif ndim == 1:
        rows = len(arr)

        with open(fname, "w") as file:

            if header is not None:
                file.write(header + "\n")

            for i in range(rows):
                file.write( "{}\n".format(arr[i]) )

    return
