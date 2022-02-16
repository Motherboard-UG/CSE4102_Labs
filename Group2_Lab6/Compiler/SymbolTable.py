class SymbolTable:
    def __init__(self):
        self.var_counter = 0
        self.argument_counter = 0
        self.static_counter = 0
        self.field_counter = 0
        self.if_counter = 0
        self.while_counter = 0
        self.global_scope = {}
        self.local_scope = {}
        self.current_scope = self.global_scope

    def count_var(self,kind):
        count = 0
        for i in self.current_scope.items():
            if i[1] == kind:
                count += 1
        return count

    def count_global(self,kind):
        count = 0
        for i in self.global_scope.items():
            if i[1] == kind:
                count += 1
        return count

    def define(self,name,type,kind):
        if(kind == "field"):
            self.global_scope[name] = (type, kind, self.field_counter)
            self.field_counter += 1

        elif (kind == "static"):
            self.global_scope[name] = (type, kind, self.static_counter)
            self.static_counter += 1

        elif (kind == "var"):
            self.current_scope[name] = (type, kind, self.var_counter)
            self.var_counter += 1

        elif (kind == "arg"):
            self.current_scope[name] = (type, kind, self.argument_counter)
            self.argument_counter +=1

    def kind_of(self,name):
        if name in self.current_scope:
            return self.current_scope[name][1]
        elif name in self.global_scope:
            return self.global_scope[name][1]
        else:
            return "NONE"

    def  type_of(self,name):
        if name in self.current_scope:
            return self.current_scope[name][0]
        elif name in self.global_scope:
            return self.global_scope[name][0]
        else:
            return "NONE"

    def index_of(self,name):
        if name in self.current_scope:
            return self.current_scope[name][2]
        elif name in self.global_scope:
            return self.global_scope[name][2]
        else:
            return "NONE"

    def set_scope(self, name):
        if (name == "global"):
            self.current_scope = self.global_scope
        else:
            self.current_scope = self.local_scope[name]

    def start_subroutine(self,name):
        self.local_scope[name] = {}
        self.argument_counter = 0
        self.var_counter = 0
        self.if_counter = 0
        self.while_counter = 0
