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
        print(files)
        for f in files:
            try:
                analyse(f)
            except IOError as e:
                if e.errno != errno.EISDIR:
                    raise
    else:
        return

def analyse(file_in):
    file_out_t = open( file_in[:-5] + "_T.xml",'w+')
    write_t = Tokenizer.Tokenizer(file_in)
    write_t.write_file(file_out_t)
    file_out_t.close()

    file_out_ce = open( file_in[:-5] + "_C.xml",'w+')
    write_ce = CompilationEngine.CompilationEngine(file_in,file_out_ce)
    write_ce.compile_class()
    file_out_ce.close()

def get_root_name(filename):
    f_name_split = filename.split('.')
    return f_name_split[0]

if __name__ == "__main__":
    main()
