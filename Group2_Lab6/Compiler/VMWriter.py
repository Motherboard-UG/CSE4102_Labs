class VMWriter:
    def __init__(self,file_out):
        self.f_out = file_out

    def write_push(self,segment,index):
        self.f_out.write("push " + segment + " " + str(index) + "\n")

    def write_pop(self,segment,index):
        self.f_out.write("pop " + segment + " " + str(index) + "\n")

    def write_arithmetic(self,command):
        self.f_out.write(command + "\n")

    def write_label(self,label):
        self.f_out.write("label " + label + "\n")

    def write_goto(self,label):
        self.f_out.write("goto " + label + "\n")

    def write_if(self,label):
        self.f_out.write("if-goto " + label + "\n")

    def write_call(self,name,nArgs):
        self.f_out.write("call " + name + " " + str(nArgs) + "\n")

    def write_function(self,name,no_locals):
        self.f_out.write("function " + name + " " + str(no_locals) + "\n")

    def write_return(self):
        self.f_out.write("return\n")

    def close(self):
        self.f_out.close()
