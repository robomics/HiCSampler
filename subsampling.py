#!usr/bin/env python
import numpy as np
import os
import hictkpy
import pandas as pd
import sys
import argparse

# Using the argparse library to take in user inputs and making it user friendly
parser = argparse.ArgumentParser()
parser.add_argument("-hic", "--hicfile", dest="hic", help="input .hic file\n\n", metavar="HiC File", required=True)
parser.add_argument("-res", dest="res", help="input the resolutions to process the HiC file, can be comma spearated list\n\n", metavar="LIST", required=True)
parser.add_argument("-ratio", dest="ratio", help="input the ratio for subsampling\n\n", metavar="FLOAT", default="1.0",  required=True)
parser.add_argument("-o", dest="output", help="path to output files\n\n", metavar="OUTPUT PATH", required=True)
parser.add_argument("-juicer", dest="juicer", help="path to juicer tools\n\n", metavar="JUICER_TOOLS PATH", required=True)
parser.add_argument("-sizes", dest="sizes", help="chromosome size file with two columns corresponding to chromosome and size respectively\n\n", metavar="SIZE FILE")
parser.add_argument("-cpu", dest="cpu", help="number of Gigs of RAM to use; default is 4GB\n\n", metavar="INT", default=4)

args = parser.parse_args()

# Creating an ouput directory
if not os.path.exists(args.output):
    os.mkdir(args.output)
    
# List of chromosomes
# Calculating the highest resolution from the set of resolutions entered by the user
inputres = args.res
myres = inputres.split(",")
myres = list(map(int, myres))
highres = min(myres)


# Parsing through each chromosome from the chromosome list
file = hictkpy.File(args.hic, highres)
for curchrom in file.chromosomes().keys():
    if curchrom.lower() == "all":
        continue
    # Using the straw library to dump the intra chromosomal raw reads from HiC file

    df = file.fetch(curchrom)
    rowidxs = df["bin1_id"].to_numpy()
    colidxs = df["bin2_id"].to_numpy()
    scores = df["count"].to_numpy()

    #rowidxs = np.array(dumped[0][:])
    #colidxs = np.array(dumped[1][:])
    #scores = np.array(dumped[2][:])
    length = len(scores)
    str1 = list(); frag1=list(); frag2=list(); chr_ls = list()
    
    # Subsampling the HiC file using the random.random_sample function
    # Adding values to the str1, frag1, frag2, chr_ls lists to create short score fomrat file
    for idx in range(length):
        rand_reads = np.random.random_sample(int(scores[idx]))
        read_count = len(np.where(rand_reads <= float(args.ratio))[0])
        scores[idx] = read_count
        str1.append(0)
        frag1.append(1)
        frag2.append(2)
        chr_ls.append(curchrom)
   
    # Creating a dataframe of the subsampled HiC file in short score format with values
    data = {"rowidxs":rowidxs, "colidxs":colidxs, "scores":scores}
    df = pd.DataFrame(data)
    # inserting the columns in the dataframe in such way to represent the short score with values format
    df.insert(0, "str1", str1, True)
    df.insert(1, "chr1", chr_ls, True)
    df.insert(3, "frag1", frag1, True)
    df.insert(4, "str2", str1, True)
    df.insert(5, "chr2", chr_ls, True)
    df.insert(7, "frag2", frag2, True)
    output_path = os.path.join(args.output, curchrom+".ssfv")
    # creating a space separated values files which represents the short score format
    df.to_csv(sys.stdout, sep=" ", header=False, index=False)

