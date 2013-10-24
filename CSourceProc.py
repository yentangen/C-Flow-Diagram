import re
import sys
import DotAPI
from DotAPI import *

#file_contents is a list with each entry containing two values: [0] being
#the name of the file, and [1] containing its formatted contents. Having this
#eliminates having to reprocess a file again but increases space required.
file_contents = []              #list of user *.c and *.h files accessed

#funct_stack is a list acting as a stack containing ordered user-defined
#function calls within the program. only append() and pop() should be used to
#manipulate it, although peeking through is allowed
funct_stack = []

#user_methods contains all the user-defined functions within the program.
#It also provides information about which file it is defined and line number
#(after stripping all formatting from the format_file() function.)
#It will primarily be used to build the graph. Main importance of this "list"
#is that it will find methods that may not be used throughout the entirety of
#the program, whereas funct_stack will only contain functions that are called.
#user_methods may or may not be ordered
user_methods = []

#The list below contains a list of "keywords", words the program will look for
#to process. As of now, it contains all conditional words (IF, ELSE IF, ELSE,
#WHILE, FOR, DO/WHILE, SWITCH), as well as user_defined functions (given by
#user_methods).
keywords = ["if","else","while","for","do","switch","case"]

#END variable declarations


#******methods for program are defined here

#input : startline, the starting line of the main function, and the filename
#        and level, which functions in formatting the output
#output : traceroute will be written to the file
def traceroute(startline,filename,level):
    first = True
    bracket_stack = []  #keeps track of brackets. empty means end of method
    tabs = ""
    root_method_name= ""
    for j in range(level):
        tabs+="\t"
    #uses file_contents
    fileindex = [index[0] for index in file_contents].index(filename)
    totallines = len(file_contents[fileindex][1])
    #starting from point specified by parameters
    while (startline < totallines):
        for word in re.split(" ",file_contents[fileindex][1][startline]):
            if "{" in word:
                bracket_stack.append("{")
            if "}" in word:
                bracket_stack.pop()
                if ( len(bracket_stack) == 0 ):
                    funct_stack.pop()
                    return
            if (word.partition("(")[0] in \
               [methods[0] for methods in user_methods]):
                if (first):
                    root_method_name = word.partition("(")[0]
                    funct_stack.append(root_method_name)
                    first = False
                    continue
                #now recursively go into user_method.
                i = user_methods[[linenum[0] for linenum in \
                              user_methods].index(word.partition("(")[0])][2]
                filen = user_methods[[linenum[0] for linenum in user_methods]\
                                     .index(word.partition("(")[0])][1]
                traceroute(i,filen,level+1)
        startline+=1
#END traceroute()
    

#input : filetext is the raw text from opening file
#output : returns list containing individual lines with formatting removed

#Since all programmers coding practices *may* not be neat, program must render
#and eliminate most file formatting. This includes eliminating all leading and
#trailing whitespaces and tabs, as well as all line and block comments.
#The program (and me, the author) will assume that the programmer is decent
#enough to vertically format his code using LF carriers, as it is necessary
#for defines and includes.
def format_file(filetext):
    block_comment = 0               #flag for block comments
    outp_list = [" \n"]                  #output for returning list
    filetext = filetext.replace('\t','')    #eliminates all tabs
    #read line by line, splitting by LF..
    for line in re.split('\n',filetext):
        #for neatness sake remove previous line if only newline
        if (outp_list[-1].replace("\n","") == ""):
            outp_list.pop()
        #strips leading and trailing whitespaces
        line = line.strip()
        #check for block_comment flag; ignore line if still part of block
        if (block_comment):
            if ("*/" not in line):   #not end of block comment yet
                continue
            else:
                block_comment = 0
                outp_list.append(line.partition("*/")[-1])
                continue
                
        if ("/*" in line):  #identified block comment within current line
            if ("*/" not in line):
                block_comment = 1
            outp_list.append(line.partition("/*")[0])
            continue
        elif ("//" in line):  #identified line comment within current line
            outp_list.append(line.partition("//")[0])
            continue
        
        #regular line without comments at this point, hopefully!
        outp_list.append(line)

    return outp_list
#END format_file()


#input : filetext contains text for an entire file
#output : updates global variables "file_contents" and "user_methods"
def preprocess(finput,filename,rootdir):
    linecount=-1
    linebuf = ""        #buffer for holding a line
    for lines in finput:
        linecount+=1
        #recursively step through includes
        if (("#include" in lines) and ("\"" in lines)): #user-defined file.
            tempfilename=re.split('"',lines)[1]
            if tempfilename in [name[0] for name in file_contents]:
                continue
            #updates list of accessed user-created files
            tempfilepath = rootdir+tempfilename
            tempinp = open(tempfilepath).read()
            tmptext = format_file(tempinp)

            file_contents.append([tempfilename,tmptext])
            preprocess(tmptext,tempfilename,rootdir)
        #now recognizes user method declarations
            #condition:
            #Find a bracket "{", then backtrace for immediate ")"
            #excluding whitespaces and formatting
            #NOTE: may span multiple lines!
        elif "{" in lines:
            #now the method name could either be in same line or line before...
            
            #if in same line....
            #assignment. ignore.
            method_line = linecount
            if ( (len(lines) > 1) and (lines.replace(" ","")[-2] == '=') ):
                linebuf = lines
                continue
            elif ( (len(lines) > 1) and (lines.replace(" ","")[-2] == ')') ):
                templine = lines
            #if in previous line...
            #with formatting and comments removed, funct name SHOULD be in
            #the line before current one.
            else:
                method_line -= 1
                templine = linebuf

            #1. strip spaces and create a list
            #2. find FIRST parenthesis
            #   a. if parenthesis is first letter of word, name = previous one
            #   b. if parenthesis not first, then split by ( and choose [0]
            i=-1
            stripped = re.split(" ",templine)
            for word in stripped:
                i+=1
                if "(" in word:
                    if (word.find('(') > 0):
                        funct_name = re.split('\(',word)[0]
                        bracket_found = 0
                    else:
                        funct_name = stripped[i-1]
            if ((funct_name in ["while","do","if","for",\
                               "else if","else","switch"]) or
                 (funct_name in [methods[0] for methods in user_methods]) or
                 (not funct_name[0].isalpha() )):
                continue
            #print lines+" : "+funct_name
            user_methods.append([funct_name,filename,method_line])
            keywords.append(funct_name)
            
        linebuf = lines     #save current line before moving on
        
    
#END preprocess()


#_sunder_formatting is used for trace_method ONLY, and removes all newlines,
#blank lines, and trailing/leading whitespaces in-between semicolons. The input
#is file_contents[*][1][x to y], where x is start of function call and y is the
#closing bracket signalling the end of the method
    #given a string, return a list with all char delimited
def _partition(string,char):
    templist = string.partition(char)
    retlist = [templist[0]]
    retlist.append(char)
    if (char in templist[2]):
        tmpbuf = _partition(templist[2],char)
        for element in tmpbuf:
            retlist.append(element)
    else:
        retlist.append(templist[2])
    return retlist

def _sunder_formatting(lcode,start,end):
    ret_string=""
    ret_list = []
    for line in lcode:
        if (line == ""):
            continue
        ret_string+=line.strip()

    #now lets space out all ('s, )'s, {'s, }'s, nad ;'s, since the C compilers do
    #not do it for us. This allows us to compile a list of words.
    ret_list = [ret_string]
    tmp_buf = ret_list
    
    for symbol in ['(',')','{','}',';']:
        ret_list = []
        for clause in tmp_buf:
            if symbol in clause:
                ret_list.extend(_partition(clause,symbol))
            else:
                ret_list.append(clause)
        tmp_buf = ret_list

    return ret_list
                
        

def _find_end_of_method(lstart,lcode):
    bstack = []
    count = lstart
    for line in lcode:
        for word in line:
            for char in word:
                #brackets. Main purpose is to determine end of method
                if (char=='{'):
                    bstack.append("{")
                elif (char=='}'):
                    bstack.pop()
                    if ( len(bstack) == 0 ):
                        return count

        count+=1

#input : start of function, and filename
#output : massive string of trace through method.
def trace_method(startline,filename,start_method):
    set_cur_graph(filename)
    word_buf = ""
    counter = 0
    output_trace = ""
    first = True
    prevnode = start_method
    BRACK_stack = []    #keeps track of brackets. empty means end of method
    node_stack = []     #keeps track of nodes to return to
    i = startline

    #uses file_contents
    fileindex = [index[0] for index in file_contents].index(filename)
    totallines = len(file_contents[fileindex][1])
    
    #create a string containing entire function:
    #for identifying brackets signaling end of function
    endline = _find_end_of_method(startline,file_contents[fileindex][1][startline:])
    codestring=_sunder_formatting(file_contents[fileindex][1][startline:],startline,endline)
    
    #print codestring
    i=0
    tempstack = []      #for counting parentheses
    tempstring = ""     #for storing temporary conditional info
    #starting from point specified by parameters
    while (i < len(codestring)):
        #do brackets first
        if (codestring[i].strip() == "{"):
            BRACK_stack.append("{")
            node_stack.append(prevnode)
        elif (codestring[i].strip() == "}"):
            BRACK_stack.pop()
            if (len(BRACK_stack) == 0):  #done with function.
                output_trace += create_node("END","")
                output_trace += connect(node_stack.pop(),"END","")
                return output_trace
            else:   #we want to link back to previous node in stack
                if (prevnode != node_stack[len(node_stack)-1]):
                    output_trace += connect(prevnode,node_stack.pop(),"")
                else:
                    node_stack.pop()
                
        #function name came up. Create nodes, connect, push onto applicable stacks
        if (codestring[i].strip() in [methods[0] for methods in user_methods]):
            output_trace += create_node(codestring[i].strip(),"")
            output_trace += connect(prevnode,codestring[i].strip(),"")
            prevnode = codestring[i].strip()
            #node_stack.append(prevnode)
        tempstring = ""
        #else block
        if ( codestring[i].strip() == "else" ):
            #next element is an "if". If so, ignore and continue
            if (codestring[i+1].strip() == "if"):
                continue
            output_trace += create_vnode()
            output_trace += connect(prevnode,get_cur_vnode(),"ELSE")
            prevnode = get_cur_vnode()
        #if block. This includes "else if"'s too. Always print condition
        elif ( codestring[i].strip() == "if"):
            j=i+1
            #count for nested parenthesis. Once tempstack is empty, break out of loop
            tempstack.append(codestring[j])   #must be (
            while (True):
                j+=1
                if (codestring[j] == "("):
                    tempstack.append(codestring[j])
                elif (codestring[j] == ")"):
                    tempstack.pop()
                    if (len(tempstack) == 0):
                        break
                tempstring += codestring[j]
            output_trace += create_vnode()
            output_trace += connect(prevnode,get_cur_vnode(),"IF "+tempstring)
            prevnode = get_cur_vnode()

        #while or do/while loops            
        elif ( (codestring[i].strip() == "while") or (codestring[i].strip() == "do")
               or (codestring[i].strip() == "for")):
            j=i+1
            #count for nested parenthesis. Once tempstack is empty, break out of loop
            tempstack.append(codestring[j])   #must be (
            while (True):
                j+=1
                if (codestring[j] == "("):
                    tempstack.append(codestring[j])
                elif (codestring[j] == ")"):
                    tempstack.pop()
                    if (len(tempstack) == 0):
                        break
                tempstring += codestring[j]
            output_trace += create_vnode()
            if (codestring[i].strip() == "for"):
                output_trace += connect(prevnode,get_cur_vnode(),"FOR "+tempstring)
            else:
                output_trace += connect(prevnode,get_cur_vnode(),"WHILE "+tempstring)
            #node_stack.append(prevnode)
            prevnode = get_cur_vnode()

        #switch statements... uhh to be implemented later...
        elif (codestring[i].strip() == "switch" ):
               first = True
        i+=1
               
#END trace_method()


#END defined methods
