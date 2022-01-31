import sys
import os
import glob
import HackWriter
import Parser

def main():

    user_input = sys.argv[1]

    def global_write(file):

        parser = Parser.Parser(file)

        writer.write_init()

        while parser.has_more_cmds():
            parser.skim_file()
            cmd_type = parser.get_cmd_type()

            if cmd_type == "arithmetic":
                writer.write_arithmetic(parser.cmd[0])
            elif cmd_type == "push" or cmd_type == "pop":
                writer.write_push_pop(cmd_type,parser.seg(),parser.seg_index())
            elif cmd_type == "branch":
                writer.write_branching(parser.cmd[0],parser.seg())
            elif cmd_type == "function":
                writer.write_function(parser.seg(),parser.seg_index())
            elif cmd_type == "call":
                writer.write_call(parser.seg(),parser.seg_index())
            elif cmd_type == "return":
                writer.write_return()

    if is_vm_file(user_input):
        writer = HackWriter.HackWriter(get_root_name(user_input) + ".asm")
        global_write(user_input)
    elif os.path.isdir(user_input):
        writer = HackWriter.HackWriter(user_input + ".asm")
        dir_path = "./" + user_input + "/*.vm"
        files = glob.glob(dir_path)
        for f in files:
            writer.set_filename(f)
            global_write(f)
    else:
        return

def is_vm_file(user_input):
        if not os.path.isfile(user_input):
            return False
        f_name_split = user_input.split('.')
        if f_name_split[1] != "vm":
            print("Error: Only .vm files can be used.")
            return False
        else:
            return True

def get_root_name(filename):
    f_name_split = filename.split('.')
    return f_name_split[0]

if __name__ == "__main__":
    main()
