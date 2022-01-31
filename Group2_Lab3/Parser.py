import sys
import os

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
            "lt" : "arithmetic",
            "and" : "arithmetic",
            "or" : "arithmetic",
            "not" : "arithmetic",
            "push" : "push",
            "pop" : "pop",
            "label" : "branch",
            "goto" : "branch",
            "if-goto" : "branch",
            "function" : "function",
            "call" : "call",
            "return" : "return",
            "EOF" : "EOF"
            }

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
