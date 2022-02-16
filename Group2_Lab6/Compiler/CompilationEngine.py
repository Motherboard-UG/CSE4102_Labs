import Tokenizer
import SymbolTable
import VMWriter

class CompilationEngine:

    spl_char = { '<':'&lt;', '>':'&gt;', '"':'&quot;','&':'&amp;'}

    def __init__(self,file_in,file_out):
        self.tokenizer = Tokenizer.Tokenizer(file_in)
        self.symbol_table = SymbolTable.SymbolTable()
        self.vm_writer = VMWriter.VMWriter(file_out)
        self.f_new = file_out
        self.class_name = ""
        self.indent = ""
        self.function_type = ""
        self.keyword_consts = {"true", "false","null","this"}
        self.binary_op = {'+','-','*','|','<','>','=','/','&'}
        self.unary_op = {'-','~'}
        self.is_unary = False

    def advance(self):
        token = self.tokenizer.skim_lines()
        tok_type = self.tokenizer.token_type()

        if tok_type == "stringConstant":
            token = token[1:-1]

        if token in self.spl_char.keys():
            token = self.spl_char[token]
        return token

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
        var_type = self.advance()
        var_name = self.advance()
        self.symbol_table.define(var_name,var_type,"arg")
        if (self.next_token() == ","):
            self.advance()

    def eat(self,string):
        next_token = self.next_token()
        if next_token == string:
            self.advance()
        else:
            # print("ERROR: expected " + string + ", got: " + next_token)
            exit()

    def Push(self,first_name):
        if first_name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(first_name) == "var":
                self.vm_writer.write_push('local',self.symbol_table.index_of(first_name))
            elif self.symbol_table.kind_of(first_name) == "arg":
                self.vm_writer.write_push('argument',self.symbol_table.index_of(first_name))

        else:
            if self.symbol_table.kind_of(first_name) == "static":
                self.vm_writer.write_push('static',self.symbol_table.index_of(first_name))
            else:
                self.vm_writer.write_push('this',self.symbol_table.index_of(first_name))

    def Pop(self,first_name):
        if first_name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(first_name) == "var":
                self.vm_writer.write_pop('local', self.symbol_table.index_of(first_name))
            elif self.symbol_table.kind_of(first_name) == "arg":
                self.vm_writer.write_pop('argument', self.symbol_table.index_of(first_name))

        else:
            if self.symbol_table.kind_of(first_name) == "static":
                self.vm_writer.write_pop('static', self.symbol_table.index_of(first_name))
            else:
                self.vm_writer.write_pop('this', self.symbol_table.index_of(first_name))

    def compile_parameter_list(self):
        count = 0
        if self.function_type == "method":
            self.symbol_table.define("this","self","arg")
        while self.exist_parameter():
            self.write_parameter()
            count += 1
        return count

    def compile_class_var_dec(self):
        kind = ""

        if self.next_token() == "static":
            kind = "static"
            self.eat("static")
        else:
            kind = "field"
            self.eat("field")

        var_type = self.advance()
        var_name = self.advance()
        self.symbol_table.define(var_name,var_type,kind)

        while self.next_token() == ",":
            self.eat(",")
            var_name = self.advance()
            self.symbol_table.define(var_name,var_type,kind)

        self.eat(";")

    def compile_class(self):
        self.eat("class")
        self.class_name = self.advance()
        self.eat("{")
        while (self.exist_class_var_dec()):
            self.compile_class_var_dec()

        while (self.exist_subroutine_dec()):
            self.compile_subroutine_dec()

        self.eat("}")
        self.vm_writer.close()

    def compile_var_dec(self):
        self.eat("var")
        var_type = str(self.advance())
        var_name = self.advance()
        self.symbol_table.define(var_name,var_type,"var")
        while (self.next_token() == ","):
            self.eat(",")
            var_name = self.advance()
            self.symbol_table.define(var_name,var_type,"var")
        self.eat(";")

    def compile_subroutine_dec(self):
        if self.next_token() == "constructor" or self.next_token() == "function" or self.next_token() == "method":
            self.function_type = self.advance()
        else:
            # print("ERROR: keyword expected")
            return
        self.advance()
        self.n = self.advance()
        self.name = self.class_name + "." + self.n
        self.symbol_table.start_subroutine(self.name)
        self.symbol_table.set_scope(self.name)
        self.eat("(")
        n_args = self.compile_parameter_list()
        self.eat(")")
        self.compile_subroutine_body()

    def compile_subroutine_body(self):
        self.eat("{")
        while(self.exist_var_dec()):
            self.compile_var_dec()
        no_locals = self.symbol_table.count_var("var")
        self.vm_writer.write_function(self.name,no_locals)

        if self.function_type == "method":
            self.vm_writer.write_push("argument",0)
            self.vm_writer.write_pop("pointer",0)

        elif self.function_type == "constructor":
            no_globals = self.symbol_table.count_global("field")
            self.vm_writer.write_push("constant",no_globals)
            self.vm_writer.write_call("Memory.alloc",1)
            self.vm_writer.write_pop("pointer",0)

        self.compile_statements()
        self.eat("}")
        self.symbol_table.set_scope("global")

    def compile_statements(self):
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

    def compile_let(self):
        self.eat("let")
        arr_name = self.advance()
        is_array = False
        if self.next_token() == '[':
            is_array = True
            self.compile_array_index(arr_name)
        self.eat("=")
        self.compile_exp()

        if is_array:
            self.vm_writer.write_pop("temp",0)
            self.vm_writer.write_pop("pointer",1)
            self.vm_writer.write_push("temp",0)
            self.vm_writer.write_pop("that",0)
        else:
            self.Pop(arr_name)
        self.eat(";")

    def compile_if(self):
        curr_if_counter = self.symbol_table.if_counter
        self.symbol_table.if_counter += 1
        self.eat("if")
        self.eat("(")
        self.compile_exp()
        self.eat(")")
        self.vm_writer.write_if("IF_LABEL"+ str(curr_if_counter))
        self.vm_writer.write_goto("IF_FALSE" + str(curr_if_counter))
        self.vm_writer.write_label("IF_LABEL" + str(curr_if_counter))
        self.eat("{")
        self.compile_statements()
        self.eat("}")
        if self.next_token() == "else":
            self.eat("else")
            self.eat("{")
            self.vm_writer.write_goto("IF_END"+str(curr_if_counter))
            self.vm_writer.write_label("IF_FALSE" + str(curr_if_counter))
            self.compile_statements()
            self.eat("}")
            self.vm_writer.write_label("IF_END"+str(curr_if_counter))
        else:
            self.vm_writer.write_label("IF_FALSE"+str(curr_if_counter))

    def compile_while(self):
        curr_while_counter = self.symbol_table.while_counter
        self.symbol_table.while_counter += 1
        self.eat("while")
        self.eat("(")
        self.vm_writer.write_label("WHILE_LABEL"+str(curr_while_counter))
        self.compile_exp()
        self.eat(")")
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if("WHILE_END"+ str(curr_while_counter))
        self.eat("{")
        self.compile_statements()
        self.eat("}")
        self.vm_writer.write_goto("WHILE_LABEL"+str(curr_while_counter))
        self.vm_writer.write_label("WHILE_END"+str(curr_while_counter))

    def compile_do(self):
        first_name = last_name = do_statement = ''
        no_locals = 0
        self.eat("do")
        first_name = self.advance()
        if self.next_token() == ".":
            self.eat(".")
            last_name = self.advance()
            if first_name in self.symbol_table.current_scope or first_name in self.symbol_table.global_scope:
                self.Push(first_name)
                full_name = self.symbol_table.type_of(first_name)+"."+last_name
                no_locals +=1
            else:
                full_name = first_name+"."+last_name
        else:
            self.vm_writer.write_push('pointer',0)
            no_locals += 1
            full_name = self.class_name +"."+first_name
        self.eat("(")
        self.compile_exp_list()
        self.vm_writer.write_call(full_name,no_locals)
        self.vm_writer.write_pop("temp",0)
        self.eat(")")
        self.eat(";")

    def compile_return(self):
        self.eat("return")
        if self.next_token() != ";":
            self.compile_exp()
        else:
            self.vm_writer.write_push("constant",0)
        self.vm_writer.write_return()
        self.eat(";")

    def compile_exp_list(self):
        counter = 0
        if self.exist_expression():
            self.compile_exp()
            counter += 1
        while self.next_token() == ",":
            self.eat(",")
            if self.exist_expression():
                self.compile_exp()
                counter += 1
        return counter

    def compile_exp(self):
        self.compile_term()
        while (self.next_token() in self.binary_op):
            operator = self.advance()
            self.compile_term()
            if operator == "+":
                self.vm_writer.write_arithmetic("add")
            elif operator == "-":
                self.vm_writer.write_arithmetic("sub")
            elif operator == "=":
                self.vm_writer.write_arithmetic("eq")
            elif operator == "&gt;":
                self.vm_writer.write_arithmetic("gt")
            elif operator == "&lt;":
                self.vm_writer.write_arithmetic("lt")
            elif operator == "&amp;":
                self.vm_writer.write_arithmetic("and")
            elif operator == "|":
                self.vm_writer.write_arithmetic("or")
            elif operator == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif operator == "/":
                self.vm_writer.write_call("Math.divide", 2)

    def compile_subroutine_call(self):
        first_name = last_name = full_name = ""
        n_args = 0
        first_name = self.advance()
        if self.next_token() == ".":
            self.eat(".")
            last_name = self.advance()
            if first_name in self.symbol_table.local_scope or first_name in self.symbol_table.global_scope:
                self.Push(first_name)
                full_name = self.symbol_table.type_of(first_name) + last_name
                n_args += 1
            else:
                full_name = first_name + last_name
        else:
            self.vm_writer.write_push("pointer",0)
            n_args += 1
            full_name = self.class_name + first_name
        self.eat("(")
        self.compile_exp_list()
        self.vm_writer.write_call(full_name,n_args)
        self.eat(")")

    def compile_term(self):

        is_array  = False

        if self.next_value() == "integerConstant":
            const = self.advance()
            self.vm_writer.write_push("constant", const)

        elif self.next_value() == "stringConstant":
            str_value = self.advance()
            self.vm_writer.write_push("constant", len(str_value))
            self.vm_writer.write_call("String.new", 1)

            for s in str_value:
                self.vm_writer.write_push("constant", ord(s))
                self.vm_writer.write_call("String.appendChar", 2)


        elif (self.next_token() in self.keyword_consts):
            keyword = self.advance()

            if keyword == "true":
                self.vm_writer.write_push("constant", 0)
                self.vm_writer.write_arithmetic("not")

            elif keyword == "false" or keyword == "null":
                self.vm_writer.write_push("constant", 0)

            elif keyword == "this":
                self.vm_writer.write_push("pointer", 0)


        elif self.next_value() == "identifier":
            n_args = 0
            identif = self.advance()

            if self.next_token() == "[":
                is_array = True
                self.compile_array_index(identif)

            if self.next_token() == "(":
                n_args+=1
                self.vm_writer.write_push("pointer", 0)
                self.eat("(")
                n_args += self.compile_exp_list()
                self.eat(")")
                self.vm_writer.write_call(self.class_name+"."+identif, n_args)

            elif self.next_token() == ".":
                self.eat(".")
                sub_name = self.advance()
                if identif in self.symbol_table.current_scope or identif in self.symbol_table.global_scope:
                    self.Push(identif)
                    name = self.symbol_table.type_of(identif)+"."+ sub_name
                    n_args+=1
                else:
                    name = identif + "."+ sub_name
                self.eat("(")
                n_args += self.compile_exp_list()
                self.eat(")")
                self.vm_writer.write_call(name,n_args)

            else:
                if is_array:
                    self.vm_writer.write_pop("pointer", 1)
                    self.vm_writer.write_push("that", 0)

                elif identif in self.symbol_table.current_scope:
                    if self.symbol_table.kind_of(identif) == "var":
                        self.vm_writer.write_push("local",self.symbol_table.index_of(identif))

                    elif self.symbol_table.kind_of(identif) == "arg":
                        self.vm_writer.write_push("argument",self.symbol_table.index_of(identif))

                else:
                    if self.symbol_table.kind_of(identif) == "static":
                        self.vm_writer.write_push("static", self.symbol_table.index_of(identif))

                    else:
                        self.vm_writer.write_push("this", self.symbol_table.index_of(identif))

        elif (self.next_token() in self.unary_op):
            uop = self.advance()

            self.compile_term()
            if (uop == "-"):
                self.vm_writer.write_arithmetic("neg")

            elif (uop == "~"):
                self.vm_writer.write_arithmetic("not")

        elif self.next_token() == "(":
            self.eat("(")
            self.compile_exp()
            self.eat(")")

    def compile_array_index(self,name):
        self.write_array_index()
        if name in self.symbol_table.current_scope:
            if self.symbol_table.kind_of(name) == 'var':
                self.vm_writer.write_push('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.vm_writer.write_push('argument', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.vm_writer.write_push('static', self.symbol_table.index_of(name))
            else:
                self.vm_writer.write_push('this', self.symbol_table.index_of(name))
        self.vm_writer.write_arithmetic('add')
