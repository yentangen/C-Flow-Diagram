import re
import sys
import CSourceProc
import DotAPI
from CSourceProc import *
from DotAPI import *

#for all conditional statements and loops:
#1. if find ";" before open bracket "{", consider only one-liner
#2. if "{" before ";" then block statement. Push and pop bracket as necessary.
#Then, put edge label from cond to ")"


#inp = str(sys.argv[1])          #1st argument (filepath to "main" C file)
#outp = str(sys.argv[2])         #2nd argument (desired output file and filepath)


inp = str("D:\misc programs\C Flow Diagram Creator\snake.c")          #1st argument (filepath to "main" C file)
outp = str("testout.dot")         #2nd argument (desired output file and filepath)
dirparts = []                   #Splits directory for building root dir
rootdirec = ""                    #root directory
rootfile = ""                   #root (starting) file from root directory
color = ["red","blue","green","purple","black"]
cindex = 0      #cycles through 0 - 4 for color scheme for graph

#if len(sys.argv) != 3:
#    print "Too many or too few arguments!\n"
#    exit(-1)

#building the root directory
inp = inp.replace('\\','/')
dirparts = re.split('/',inp)

rootfile = dirparts[-1]
if ".c" not in rootfile:
    print "Input file is not a .c file. Please check argument parameters"
    exit(-1)
#lets check output file validity now while we're at it
if ".dot" not in outp:
    print "Output file is not a .dot file. Please check argument parameters"
    exit(-1)

for part in dirparts[:-1]:
    rootdirec += (part+"\\")

#opens input and output file readers
inptext = open(inp).read()
out = open(outp, 'w')

ftext = format_file(inptext)
file_contents.append([rootfile,ftext])
#lets grab all user-defined methods in other included files
preprocess(ftext,rootfile,rootdirec)

#Create Global Graph:
out.write("digraph "+rootfile.partition(".")[0]+" {\n\n")

#initial .dot file formatting
out.write(init_header("G","10,7.5","true","out","landscape",1.25,3.0,color[cindex%5]))
cindex += 1
i = user_methods[[linenum[0] for linenum in user_methods].index("main")][2]
#traceroute(i,rootfile,1)
outp = trace_method(i,rootfile,"main")
out.write(outp)
out.write("}\n\n")


out.write("}")
out.close()
#exit(0)
