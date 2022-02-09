import Tokenizer

class CompilationEngine:

    spl_char = { '<':'&lt;', '>':'&gt;', '"':'&quot;','&':'&amp;'}

    def __init__(self,file_in,file_out):
        self.tokenizer = Tokenizer.Tokenizer(file_in)
        self.f_new = file_out
        self.indent = ""
        self.mStack =[]
        self.keyword_consts = {"true", "false","null","this"}
        self.binary_op = {'+','-','*','|','<','>','=','/','&'}
        self.unary_op = {'-','~'}

    def add_indent(self):
        self.indent += "    "

    def rm_indent(self):
        self.indent = self.indent[:-4]

    def write_term(self,token,tok_type):
        self.f_new.write(self.indent + "<" + tok_type + ">" + token + "</" + tok_type + ">\n")

    def start_non_term(self,rule):
        self.f_new.write(self.indent + "<" + rule + ">\n")
        self.add_indent()
        self.mStack.append(rule)

    def end_non_term(self):
        rule = self.mStack.pop()
        self.rm_indent()
        self.f_new.write(self.indent + "</" + rule + ">\n")

    def advance(self):
        token = self.tokenizer.skim_lines()
        tok_type = self.tokenizer.token_type()

        if tok_type == "stringConstant":
            token = token[1:-1]

        if token in self.spl_char.keys():
            token = self.spl_char[token]
        self.write_term(token,tok_type)

    def next_value(self):
        value = self.tokenizer.next_value()
        return value

    def next_token(self):
        return self.tokenizer.next_token()

    def write_array_index(self):
        self.advance()
        self.compile_exp()
        self.advance()

    def exist_expression(self):
        return self.exist_term()

    def exist_term(self):
        token = self.next_token()
        tok_type = self.next_value()

        return (tok_type == "integerConstant" or tok_type == "stringConstant" or tok_type == "identifier" or token in self.unary_op or token in self.keyword_consts or token == "(")

    def exist_statement(self):
        return (self.next_token() == "do") \
               or (self.next_token() == "let") \
               or (self.next_token() == "if") \
               or (self.next_token() == "while") \
               or (self.next_token() == "return") \

    def exist_var_dec(self):
        return (self.next_token() == "var")

    def exist_class_var_dec(self):
        return (self.next_token() == "static" or self.next_token() == "field")

    def exist_subroutine_dec(self):
        return (self.next_token() == "constructor" or self.next_token() == "function" or self.next_token() == "method")

    def exist_parameter(self):
        return not (self.next_value() == "symbol")

    def write_parameter(self):
        self.advance()
        self.advance()
        if (self.next_token() == ","):
            self.advance()

    def eat(self,string):
        next_token = self.next_token()
        print("!!" + next_token + "!")
        if next_token == string:
            self.advance()
        else:
            print("ERROR: expected " + string + ", got: " + next_token)
            exit()

    def compile_parameter_list(self):
        self.start_non_term("parameterList")
        while self.exist_parameter():
            self.write_parameter()
        self.end_non_term()

    def compile_class_var_dec(self):
        self.start_non_term("classVarDec")

        if self.next_token() == "static":
            self.eat("static")
        else:
            self.eat("field")

        self.advance()
        self.advance()

        while self.next_token() == ",":
            self.eat(",")
            self.advance()

        self.eat(";")
        self.end_non_term()

    def compile_class(self):
        self.start_non_term("class")
        self.eat("class")
        self.advance()
        self.eat("{")
        while (self.exist_class_var_dec()):
            self.compile_class_var_dec()

        while (self.exist_subroutine_dec()):
            self.compile_subroutine_dec()

        self.eat("}")
        self.end_non_term()

    def compile_var_dec(self):
        self.start_non_term("varDec")
        self.eat("var")
        self.advance()
        self.advance()
        while (self.next_token() == ","):
            self.eat(",")
            self.advance()
        self.eat(";")
        self.end_non_term()

    def compile_subroutine_dec(self):
        self.start_non_term("subroutineDec")
        if self.next_token() == "constructor" or self.next_token() == "function" or self.next_token() == "method":
            self.advance()
        else:
            print("ERROR: keyword expected")
            return
        self.advance()
        self.advance()
        self.eat("(")
        self.compile_parameter_list()
        self.eat(")")
        self.compile_subroutine_body()
        self.end_non_term()

    def compile_subroutine_body(self):
        self.start_non_term("subroutineBody")
        self.eat("{")
        while(self.exist_var_dec()):
            self.compile_var_dec()
        self.compile_statements()
        self.eat("}")
        self.end_non_term()

    def compile_statements(self):
        self.start_non_term("statements")
        while self.exist_statement():
            if self.next_token() == "do":
                self.compile_do()
            elif self.next_token() == "let":
                self.compile_let()
            elif self.next_token() == "while":
                self.compile_while()
            elif self.next_token() == "if":
                self.compile_if()
            elif self.next_token() == "return":
                self.compile_return()
        self.end_non_term()

    def compile_let(self):
        self.start_non_term('letStatement')
        self.eat("let")
        self.advance()
        if self.next_token() == '[':
            self.write_array_index()
        self.eat("=")
        self.compile_exp()
        self.eat(";")
        self.end_non_term()

    def compile_if(self):
        self.start_non_term('ifStatement')
        self.eat("if")
        self.eat("(")
        self.compile_exp()
        self.eat(")")
        self.eat("{")
        self.compile_statements()
        self.eat("}")
        if self.next_token() == "else":
            self.eat("else")
            self.eat("{")
            self.compile_statements()
            self.eat("}")
        self.end_non_term()

    def compile_while(self):
        self.start_non_term("whileStatement")
        self.eat("while")
        self.eat("(")
        self.compile_exp()
        self.eat(")")
        self.eat("{")
        self.compile_statements()
        self.eat("}")
        self.end_non_term()

    def compile_do(self):
        self.start_non_term("doStatement")
        self.eat("do")
        self.advance()
        if self.next_token() == ".":
            self.eat(".")
            self.advance()
        self.eat("(")
        self.compile_exp_list();
        self.eat(")")
        self.eat(";")
        self.end_non_term()

    def compile_return(self):
        self.start_non_term("returnStatement")
        self.eat("return")
        if self.next_token() != ";":
            self.compile_exp()
        self.eat(";")
        self.end_non_term()

    def compile_exp_list(self):
        self.start_non_term('expressionList')
        if self.exist_expression():
            self.compile_exp()
        while self.next_token() == ",":
            self.eat(",")
            if self.exist_expression():
                self.compile_exp()
        self.end_non_term()

    def compile_exp(self):
        self.start_non_term('expression')
        self.compile_term()
        while (self.next_token() in self.binary_op):
            self.advance()
            self.compile_term()
        self.end_non_term()

    def compile_subroutine_call(self):
        self.start_non_term("subroutineCall")
        self.advance()
        if self.next_token() == ".":
            self.eat(".")
            self.advance()
        self.eat("(")
        self.compile_exp_list()
        self.eat(")")
        self.end_non_term()

    def compile_term(self):
        self.start_non_term("term")

        print("compiling term" + self.next_value())
        if self.next_value() == "integerConstant" or self.next_value() == "stringConstant" or (self.next_token() in self.keyword_consts):
            self.advance()
        elif self.next_value() == "identifier":
            self.advance()

            if self.next_token() == "[":
                self.write_array_index()

            if self.next_token() == "(":
                self.eat("(")
                self.compile_exp_list()
                self.eat(")")

            if self.next_token() == ".":
                self.eat(".")
                self.advance()
                self.eat("(")
                self.compile_exp_list()
                self.eat(")")

        elif (self.next_token() in self.unary_op):
            self.advance()
            self.compile_term()

        elif self.next_token() == "(":
            self.eat("(")
            self.compile_exp()
            self.eat(")")

        self.end_non_term()
