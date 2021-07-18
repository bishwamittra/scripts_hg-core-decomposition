import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--token", help="token of dir", default="", type=str)
# parser.add_argument("--mpi", action='store_true')
parser.add_argument("--all", action='store_true')
args = parser.parse_args()


os.system("./clean.sh")

# if(args.mpi):
path="nscc:/home/projects/11000744/bishwa/hg_decompose/" 
if(args.all):
    os.system("tar -czvf file_to_send.tar.gz hgDecompose/* data/* HyperNetX/* *.py *sh *md")
else:
    os.system("tar -czvf file_to_send.tar.gz hgDecompose/* *.py *sh *md")
os.system("rsync -vaP file_to_send.tar.gz "+path)


os.system("rm file_to_send.tar.gz")