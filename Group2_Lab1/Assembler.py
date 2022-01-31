import sys
import re
from tables import *

prog = sys.argv[1]

a_ref, l_ref, c_ref = {}, {}, {}

def main():
    f = read_file(prog)
    create_l_ref(f)
    create_a_ref(f)
    create_c_ref(f)
    results = assemble(f)
    create_new_file(results)

def read_file(prog):
    f_clean = []
    f = open(prog,"r")
    for l in f.readlines():
        comment_pos = l.find("//")
        if comment_pos != -1:
            l = l[:comment_pos]
        if re.search(r'\S',l):
            l = l.strip()
            f_clean.append(l)
    f.close()
    return f_clean

def create_l_ref(f):
    l_num = 0
    for l in f:
        l_num += 1
        if is_l_command(l):
            l_num -= 1
            l_ref[l[1:-1]] = dec_to_bin(int(l_num))

def create_a_ref(f):
    r_address = 16

    for l in f:
        if is_a_command(l):
            value = l[1:]
            if value.isdigit():
                a_ref[l] = dec_to_bin(int(value))
            elif value in predef_table.keys():
                a_ref[l] = dec_to_bin(predef_table[value])
            elif value in l_ref.keys():
                a_ref[l] = l_ref[value]
            elif l in a_ref.keys():
                continue
            else:
                a_ref[l] = dec_to_bin(r_address)
                r_address += 1

def create_c_ref(f):

    for l in f:
        if is_c_command(l):
            equal_pos = l.find('=')
            sem_col_pos = l.find(';')

            if equal_pos != -1 and sem_col_pos != -1:
                comp = l[equal_pos+1:sem_col_pos]
                dest = l[:equal_pos]
                jump = l[sem_col_pos+1:]
            elif equal_pos != -1:
                comp = l[equal_pos+1:]
                dest = l[:equal_pos]
                jump = "null"
            elif sem_col_pos != -1:
                comp = l[:sem_col_pos]
                dest = "null"
                jump = l[sem_col_pos+1:]

            c_ref[l] = "111" + comp_table[comp] + dest_table[dest] + jump_table[jump]

def assemble(f):
    f_machine = []
    for l in f:
        if is_a_command(l):
            f_machine.append(a_ref[l])
        elif is_c_command(l):
            f_machine.append(c_ref[l])
    return f_machine

def create_new_file(f):
    dot_pos = prog.find('.')
    name = prog[:dot_pos]
    name = name+".hack"
    new_file = open(name,'w')
    for l in f:
        new_file.write(l+"\n")
    new_file.close()

dec_to_bin = lambda x : bin(x)[2:].zfill(16)

is_l_command = lambda i : i.find('(') != -1
is_a_command = lambda i : i.find('@') != -1
is_c_command = lambda i : i.find('(') == -1 and i.find('@') == -1

if __name__ == '__main__':
    main()
