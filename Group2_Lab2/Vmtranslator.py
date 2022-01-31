import sys

def main():

    f = sys.argv[1]

    parser = Parser(f)

    if not parser.is_vm_file():
        return

    writer = HackWriter(parser.get_root_name() + ".asm")

    while parser.has_more_cmds():
        parser.skim_file()
        cmd_type = parser.get_cmd_type()

        if cmd_type == "arithmetic":
            writer.writeArithmetic(parser.cmd[0])
        elif cmd_type == "push" or cmd_type == "pop":
            writer.writePushPop(cmd_type,parser.seg(),parser.seg_index())


class Parser:

    def __init__(self,file):
        try:
            self.f = open(file,'r')
        except OSError:
            print("Could not open file: ", file)
            sys.exit()
        self.cmd = [""]
        self.cursor_eof = False

        self.cmd_type = {
            "add" : "arithmetic",
            "sub" : "arithmetic",
            "neg" : "arithmetic",
            "eq" : "arithmetic",
            "gt" : "arithmetic",
            "ls" : "arithmetic",
            "and" : "arithmetic",
            "or" : "arithmetic",
            "not" : "arithmetic",
            "push" : "push",
            "pop" : "pop",
            "EOF" : "EOF",
            }

    def is_vm_file(self):
        f_name_split = self.f.name.split('.')
        if f_name_split[1] != "vm":
            print("Error: Only .vm files can be used.")
            return False
        else:
            return True

    def get_root_name(self):
        f_name_split = self.f.name.split('.')
        return f_name_split[0]

    def has_more_cmds(self):
        cursor_pos = self.f.tell()
        self.skim_file()
        self.f.seek(cursor_pos)
        return not self.cursor_eof

    def skim_file(self):
        l = self.f.readline()

        if l == "":
            self.cursor_eof = True
        else:
            necessary_line = l.split('/')[0].strip()
            if necessary_line == "":
                self.skim_file()
            else:
                self.cmd = necessary_line.split()

    def get_cmd_type(self):
        return self.cmd_type.get(self.cmd[0], "Invalid cmd type")

    def seg(self):
        return self.cmd[1]

    def seg_index(self):
        return self.cmd[2]


class HackWriter:
    def __init__(self,dest):
        self.f_output = open(dest,'w')
        self.new_label = 0

    def set_filename(self,dest):
        self.source = dest[:-3]

    def writeArithmetic(self,cmd):
        new_asm = ""

        if cmd == "add":
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "M=D+M\n"
            new_asm += "@SP\n"
            new_asm += "M=M+1\n"
        elif cmd == "sub":
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "M=M-D\n"
            new_asm += "@SP\n"
            new_asm += "M=M+1\n"
        elif cmd == "neg":
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=-M\n"
        elif cmd == "not":
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=!M\n"
        elif cmd == "or":
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=D|M\n"
        elif cmd == "and":
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=D&M\n"
        elif cmd == "eq":
            label = str(self.new_label)
            self.new_label += 1
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "D=M-D\n"
            new_asm += "M=-1\n"
            new_asm += "@eqTrue" + label + "\n"
            new_asm += "D;JEQ\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=0\n"
            new_asm += "(eqTrue" + label + ")\n"
        elif cmd == "gt":
            label = str(self.new_label)
            self.new_label += 1
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "D=M-D\n"
            new_asm += "M=-1\n"
            new_asm += "@gtTrue" + label + "\n"
            new_asm += "D;JGT\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=0\n"
            new_asm += "(gtTrue" + label + ")\n"
        elif cmd == "lt":
            label = str(self.new_label)
            self.new_label += 1
            new_asm += "@SP\n"
            new_asm += "AM=M-1\n"
            new_asm += "D=M\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "D=M-D\n"
            new_asm += "M=-1\n"
            new_asm += "@ltTrue" + label + "\n"
            new_asm += "D;JLT\n"
            new_asm += "@SP\n"
            new_asm += "A=M-1\n"
            new_asm += "M=0\n"
            new_asm += "(ltTrue" + label + ")\n"
        else:
            new_asm = cmd + " not implemented yet\n"

        self.f_output.write("// " + cmd + "\n" + new_asm)

    def writePushPop(self, command, segment, index):
        new_asm = ""
        if command == "push":
            new_asm += "// push " + segment + index + "\n"
            if segment == "constant":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "static":
                new_asm += "@" + self.source + "." + index + "\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "this":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@THIS\n"
                new_asm += "A=M+D\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "that":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@THAT\n"
                new_asm += "A=M+D\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "argument":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@ARG\n"
                new_asm += "A=M+D\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "local":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@LCL\n"
                new_asm += "A=M+D\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "temp":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@5\n"
                new_asm += "A=A+D\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            elif segment == "pointer":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@3\n"
                new_asm += "A=A+D\n"
                new_asm += "D=M\n"
                new_asm += "@SP\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "M=M+1\n"
            else:
                new_asm += segment + " not implemented yet, can't push\n"

        elif command == "pop":
            new_asm += "// pop " + segment + index + "\n"
            if segment == "static":
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@" + self.source + "." + index + "\n"
                new_asm += "M=D\n"
            elif segment == "this":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@THIS\n"
                new_asm += "D=M+D\n"
                new_asm += "@R13\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@R13\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
            elif segment == "that":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@THAT\n"
                new_asm += "D=M+D\n"
                new_asm += "@R13\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@R13\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
            elif segment == "argument":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@ARG\n"
                new_asm += "D=M+D\n"
                new_asm += "@R13\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@R13\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
            elif segment == "local":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@LCL\n"
                new_asm += "D=M+D\n"
                new_asm += "@R13\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@R13\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
            elif segment == "pointer":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@3\n"
                new_asm += "D=A+D\n"
                new_asm += "@R13\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@R13\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
            elif segment == "temp":
                new_asm += "@" + index + "\n"
                new_asm += "D=A\n"
                new_asm += "@5\n"
                new_asm += "D=A+D\n"
                new_asm += "@R13\n"
                new_asm += "M=D\n"
                new_asm += "@SP\n"
                new_asm += "AM=M-1\n"
                new_asm += "D=M\n"
                new_asm += "@R13\n"
                new_asm += "A=M\n"
                new_asm += "M=D\n"
            else:
                new_asm += segment + " not implemented yet, cannot pop\n"

        self.f_output.write(new_asm)

    def writeError(self):
        self.f_output.write("Error: Command not recognised.\n")


if __name__ == "__main__":
    main()
