#!/usr/bin/env python

import os
import argparse
import json
from pprint import pprint
from glob import glob

def main(args):
    # print(args.suffix)

    main_list = []
    wing_list = []

    for filename in glob(args.wildcard[0]):
        if filename.endswith(args.main + args.suffix):
            main_list.append(filename)
        elif filename.endswith(args.wing + args.suffix):
            wing_list.append(filename)

    for m in main_list:
        prefix = m.split(args.main + args.suffix)[0]
        for w in wing_list:
            if w == prefix + args.wing + args.suffix:
                # print(m,w)
                outfile_str = os.path.join(args.output_directory,
                    prefix + args.full + args.suffix)
                print("Concatenating: {} + {}. Writing to: {}".format(m, w, outfile_str))
                with open(outfile_str, 'w') as outfile, open(m) as mfile, open(w) as wfile:
                     outfile.write(mfile.read())
                     for wline in wfile.readlines()[2:]:
                        outfile.write(wline)
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Concatenate two Iqxqy.dat files into one. Expecting as input'
        ' *_m_Iqxy.dat and *_w_Iqxy.dat files. Outputs *_f_Iqxy.dat file.'
        ' This can be changed with the arguments below',
        add_help=True
    )
    parser.add_argument('--suffix', '-s', nargs='?', default='Iqxy.dat',
                        help="default: %(default)s")
    parser.add_argument('--main', '-m', nargs='?', default="_m_",
                        help="default: %(default)s")
    parser.add_argument('--wing', '-w', nargs='?', default="_w_",
                        help="default: %(default)s")
    parser.add_argument('--full', '-f', nargs='?', default="_f_",
                        help="default: %(default)s")
    parser.add_argument('--output-directory', '-o', nargs='?', default="{}".format(
                            os.path.abspath(os.path.curdir)),
                        help="default: %(default)s")

    parser.add_argument('wildcard', nargs=1, help='File wildcards. E.g.: BioSANS*')
    
    args = parser.parse_args()
   
    main(args)
 