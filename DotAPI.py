#DotAPI

vcount = -1             #global variable keeping track of how many vnodes made
cur_vnode = ""
cur_graph = ""          #current graph. Needed to keep multiple graphs separate

def _formatlabel(label):
    i=0
    line_list = label.split(" ")
    result=""
    for part in line_list:
        result += part
        if ((i%3)==0):
            result += "\\n"
        i+=1

    return result

#for setting current graph name (when requested by another module)
def set_cur_graph(name):
    global cur_graph
    cur_graph = name.partition('.')[0]

#for getting current vnode (when requested by another module)
def get_cur_vnode():
    return cur_vnode
    
#create_vnode()
#input : none
#output : vnode(vcount) [shape=circle,width=.01,height=0.01,label=""]\n
#Function : Uses global variable vcount to create a virtual node with width 0.01
#           and height 0.01 and no label so that it is represented as a dot in
#           the result graph. This is primarily used to join conditional paths
#           together ([el]if, else, while, for, switch, etc)
def create_vnode():
    global vcount
    global cur_vnode
    vcount += 1
    cur_vnode = "vnode"+str(vcount)
    return "\t"+cur_graph+"_"+cur_vnode+\
           " [shape=circle,width=.01,height=0.01,label=\"\"]\n"
#END create_node


#connect()
#input : fromnode, tonode, label
#output : fromnode -> tonode [label="label" style=bold weight=99];\n
#Function : Connects two nodes together with a label. If no label is desired
#           simply pass in an empty string "".
#       NOTE: If connecting to a vnode make sure there is a free vnode via
#             create_vnode() before calling this method!
def connect(fromnode,tonode,label):
    fnode = cur_graph+"_"+fromnode
    tnode = cur_graph+"_"+tonode
    return "\t"+fnode+" -> "+\
                         tnode+" [label=\""+_formatlabel(label)+\
                         "\" style=bold weight=99];\n"
#END connect


#create_node(name,xlabel)
#input : name, xlabel
#output : name [label="label" xlabel="xlabel"]
#Function : Creates a string that tells DOT interpreter to create a node with
#           given name, and an outside "x"label.
        #NOTE: This is NOT to be used for vnodes!
def create_node(name,xlabel):
    nodename = cur_graph+"_"+name
    return "\t"+nodename+" [label=\""+name+"\" xlabel=\""+xlabel+"\"]\n"

#init_header()
#input : name,size,center,ordering,orientation,ranksep,mindist,nodecolor
#output : many lines containing information about the graph appearance.
#Function : Starts off with header information. This MUST be called to set up
#           the output .dot file.
def init_header(name,size,center,ordering,orientation,ranksep,mindist,nodecolor):
    header = "subgraph "+name+" {\n"
    header += "\tsize=\""+size+"\";\n"
    header += "\tcenter = "+center+";\n"
    header += "\tordering = "+ordering+";\n"
    header += "\torientation = "+orientation+";\n"
    header += "\tranksep = "+str(ranksep)+";\n"
    header += "\tmindist = "+str(mindist)+";\n"
    header += "\tnode [color=\""+nodecolor+"\"];\n"
    header += "\tedge [arrowsize=\"0.5\"];\n"
    cur_graph = name
    return header
