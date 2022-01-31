class HackWriter:
    def __init__(self,dest):
        self.f_output = open(dest,'w')
        self.new_label = 0

    def set_filename(self,dest):
        self.source = dest[:-3]

    def write_init(self):
        new_asm = "//bootstrap\n\n"
        new_asm += "@256\n"
        new_asm += "D = A\n"
        new_asm += "@SP\n"
        new_asm += "M = D\n"
        self.f_output.write(new_asm)
        self.write_call('Sys.init','0')

    def write_arithmetic(self,cmd):
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

    def write_push_pop(self,cmd,segment,index):
        new_asm = ""
        if cmd == "push":
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

        elif cmd == "pop":
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

    def write_label(self,txt):
        new_asm = "(" + txt + ")"
        self.f_output.write(new_asm)

    def write_goto(self,txt):
        new_asm = ""
        new_asm += "@" + txt + "\n"
        new_asm += "0;JMP\n"
        self.f_output.write("//goto\n" + new_asm)

    def write_if(self,string):
        new_asm = ""
        new_asm += "@SP\n"
        new_asm += "AM = M -1\n"
        new_asm += "D = M\n"
        new_asm += "@"+string+"\n"
        new_asm += "D;JNE\n"
        self.f_output.write("//if statement\n" + new_asm)

    def write_branching(self,cmd,location):
        if cmd == "label":
            self.write_label(location)
        elif cmd == "goto":
            self.write_goto(location)
        elif cmd == "if-goto":
            self.write_if(location)
        else:
            self.f_output.write("Not implemented: " + cmd)

    def write_function(self,funcName,nVar):
        self.write_label(funcName + "$label")
        new_asm = ""
        for i in range(int(nVar)):
            new_asm += "D = 0\n"
            new_asm += "@SP\n"
            new_asm += "A = M\n"
            new_asm += "M = D\n"
            new_asm += "@SP\n"
            new_asm += "M = M + 1\n"
        self.f_output.write("//function "+funcName+" "+nVar+"\n" + new_asm)

    def write_call(self,funcName,nVar):
        new_asm = ""
        self.new_label +=1
        new_asm += "@" + funcName+"$ret." + str(self.new_label) + "\n"
        new_asm += "D = A\n"
        new_asm += "@SP\n"
        new_asm += "A = M\n"
        new_asm += "M = D\n"
        new_asm += "@SP\n"
        new_asm += "M = M + 1\n"

        new_asm += "@LCL\n"
        new_asm += "D = M\n"
        new_asm += "@SP\n"
        new_asm += "A = M\n"
        new_asm += "M = D\n"
        new_asm += "@SP\n"
        new_asm += "M = M + 1\n"

        new_asm += "@ARG\n"
        new_asm += "D = M\n"
        new_asm += "@SP\n"
        new_asm += "A = M\n"
        new_asm += "M = D\n"
        new_asm += "@SP\n"
        new_asm += "M = M + 1\n"

        new_asm += "@THIS\n"
        new_asm += "D = M\n"
        new_asm += "@SP\n"
        new_asm += "A = M\n"
        new_asm += "M = D\n"
        new_asm += "@SP\n"
        new_asm += "M = M + 1\n"

        new_asm += "@THAT\n"
        new_asm += "D = M\n"
        new_asm += "@SP\n"
        new_asm += "A = M\n"
        new_asm += "M = D\n"
        new_asm += "@SP\n"
        new_asm += "M = M + 1\n"


        new_asm += "@SP\n"
        new_asm += "D = M\n"
        new_asm += "@LCL\n"
        new_asm += "M = D\n"

        new_asm += "@" + str(5+int(nVar)) + "\n"
        new_asm += "D = D - A\n"
        new_asm += "@ARG\n"
        new_asm += "M = D\n"

        new_asm += "@" + funcName + "$label\n"
        new_asm += "0;JMP\n"

        new_asm += "(" + funcName + "$ret." + str(self.new_label) + ")\n"

        self.f_output.write("//call " + funcName+" " + nVar + "\n" + new_asm)

    def write_return(self):
        endFrame = 'R13'
        retAddr = 'R14'
        new_asm = ""
        new_asm += "@LCL\n"
        new_asm += "D = M\n"
        new_asm += "@" + endFrame + "\n"
        new_asm += "M = D\n"

        new_asm += "@" + endFrame + "\n"
        new_asm += "D = M\n"
        new_asm += "@5\n"
        new_asm += "D = D - A\n"
        new_asm += "A = D\n"
        new_asm += "D = M\n"
        #retAddr = *(endFrame)
        new_asm += "@" + retAddr + "\n"
        new_asm += "M = D\n"

        new_asm += "@SP\n"
        new_asm += "AM = M - 1\n"
        new_asm += "D = M\n"
        new_asm += "@ARG\n"
        new_asm += "A = M\n"
        new_asm += "M = D\n"

        new_asm += "@ARG\n"
        new_asm += "D = M + 1\n"
        new_asm += "@SP\n"
        new_asm += "M = D\n"

        retset = 1
        for addr in ["@THAT", "@THIS", "@ARG", "@LCL"]:

            new_asm += "@" + endFrame + "\n"
            new_asm += "D = M\n"
            new_asm += "@" + str(retset) + "\n"
            new_asm += "D = D - A\n"
            new_asm += "A = D\n"
            new_asm += "D = M\n"
            new_asm += addr + "\n"
            new_asm += "M = D\n"
            retset += 1

        new_asm += "@" + retAddr + "\n"
        new_asm += "A = M\n"
        new_asm += "0;JMP\n"

        self.f_output.write("//return\n" + new_asm)
