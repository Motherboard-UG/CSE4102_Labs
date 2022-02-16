import sys
import re

class Tokenizer:

    symbols = r'()[]{},;=.+-*/&|~<>'
    re_symbol = '\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|-|\*|/|&|\||\<|\>|=|_|~'
    re_string = '"[^"]*"'
    #delimiters = r'([\(\)\[\]\{\}\,\;\=\.\+\-\*\/\&\|\~\<\>]|(?:"[^"]*")|)'
    keywords = ('class','constructor','method','function','int','boolean','char','void','var','static','field','let','do','if','else','while','return','true','false','null','this')

    def __init__(self,file_in):
        self.f_in = open(file_in,'r')

        self.tokens = self.f_in.read()
        self.token = ""

        self.rm_comments(self.tokens)
        self.tokenize(self.tokens)
        print(self.tokens)

    def tokenize(self,lines):
        regex = '('+'|'.join(exp for exp in[self.re_symbol,self.re_string]) + ')|\s+'
        toks = re.split(regex,lines)
        toks = filter(None, toks)
        self.tokens = list(toks)

    def rm_comments(self,lines):
        uncommented = re.sub('//.*?\n', '', lines)
        uncommented = re.sub('/\*.*?\*/', '', uncommented, flags=re.DOTALL)
        self.tokens = uncommented

    def has_more_tokens(self):
        if len(self.tokens) > 0:
            return True
        return False

    def skim_lines(self):
        if self.has_more_tokens():
            self.token = self.tokens[0]
            print("token: " + str(self.token)+" type: " + self.token_type())
            print( self.token)
            self.tokens = self.tokens[1:]

        return self.token

    def next_token(self):
        if self.has_more_tokens():
            return self.tokens[0]
        else:
            return ("ERROR")

    def next_value(self):
        el = self.next_token()
        if el in self.keywords:
            return 'keyword'
        elif re.match(self.re_symbol,el):
            return 'symbol'
        elif el.isdigit():
            if int(el)>=0 and int(el)<=32767:
                return 'integerConstant'
            else:
                raise Exception("Integer should be between 0 and 32767")
        elif re.match(r'(?:"[^"]*")',el):
            return 'stringConstant'
        elif re.match(r'^[\w\d_]*$',el) and not el[0].isdigit() and el not in self.keywords:
            return 'identifier'
        else:
            raise Exception('Illegal Token: %s'%self.token)

    def token_type(self):
        if self.token in self.keywords:
            return 'keyword'
        elif re.match(self.re_symbol,self.token):
            return 'symbol'
        elif self.token.isdigit():
            if int(self.token)>=0 and int(self.token)<=32767:
                return 'integerConstant'
            else:
                raise Exception("Integer should be between 0 and 32767")
        elif re.match(r'(?:"[^"]*")',self.token):
            return 'stringConstant'
        elif re.match(r'^[\w\d_]*$',self.token) and not self.token[0].isdigit() and self.token not in self.keywords:
            return 'identifier'
        else:
            raise Exception('Illegal Token: %s'%self.token)

    def write_file(self,file_out):
        self.f_new = file_out
        self.f_new.write("<tokens>\n")
        while(self.has_more_tokens()):
            token = self.skim_lines()
            token_type = self.token_type()
            self.write_term(token,token_type)
        self.f_new.write("</tokens>")

    def write_term(self,token,tok_type):
        self.f_new.write("<" + tok_type + ">" + token + "</" + tok_type + ">\n")
