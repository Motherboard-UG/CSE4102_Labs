import sys
import os
import glob
import errno
import Tokenizer
import CompilationEngine

def main():

    user_input = sys.argv[1]

    if os.path.isfile(user_input):
        analyse(user_input)
    elif os.path.isdir(user_input):
        dir_path = "./" + user_input + "/*.jack"
        files = glob.glob(dir_path)
        for f in files:
            try:
                analyse(f)
            except IOError as e:
                if e.errno != errno.EISDIR:
                    raise
    else:
        return

def analyse(file_in):
    file_out = open( file_in[:-5] + ".vm",'w+')
    write = CompilationEngine.CompilationEngine(file_in,file_out)
    write.compile_class()
    file_out.close()

def get_root_name(filename):
    f_name_split = filename.split('.')
    return f_name_split[0]

if __name__ == "__main__":
    main()
