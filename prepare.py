import os

# on the server end
os.system("tar -xvf file_to_send.tar.gz")
os.system("rm file_to_send.tar.gz")

#when to send files to mac
os.system("tar -czvf data/output/output.tar.gz data/output/*.csv data/datasets/*.pdf data/datasets/*.png data/output/*.pkl")