from rply import LexerGenerator, ParserGenerator
from objects import *

class Fern:
    @staticmethod
    def normalize_string(s: str): return s.removeprefix("\"").removesuffix("\"").replace("\\\"", "\"").replace("\\\\", "\\")
    
    def _build_lexer(self):
        lg = LexerGenerator()
        lg.add("CLASS", r"\.")
        lg.add("ID", r"\#")
        lg.add("CHILD", r"\>")
        lg.add("SIBLING", r"\+")
        lg.add("(", r"\(")
        lg.add(")", r"\)")
        lg.add("[", r"\[")
        lg.add("]", r"\]")
        lg.add("{", r"\{")
        lg.add("}", r"\}")
        lg.add("=", r"\=")
        lg.add("*", r"\*")
        lg.add("WORD", r"[A-Za-z0-9_-]+")
        lg.add("STRING", r"\"((?:\\.|[^\\\"])*)\"")
        lg.add(",", r",")
        lg.ignore(r"\s+")
        self.lexer = lg.build()
        return self.lexer

    def _build_parser(self):
        pg = ParserGenerator(["CLASS", "ID", "CHILD", "SIBLING", "WORD", "STRING", "(", ")", "[", "]", "{", "}", "=", ",", "*"], [
            ("right", ["CHILD"]),
            ("right", ["SIBLING"]),
            ("left", ["*"]),
            ("left", ["CLASS", "ID"]),
            ("left", ["{", "["])
        ])

        @pg.production("selector : ( selector )")
        def selector_parens(state, p):
            return p[1]

        @pg.production("selector : WORD")
        def selector_tag(state, p):
            return Element(p[0].getstr())

        @pg.production("attr : CLASS WORD")
        @pg.production("attr : CLASS STRING")
        def attr_class(state, p):
            return {"class": self.normalize_string(p[1].getstr())}

        @pg.production("attr : ID WORD")
        @pg.production("attr : ID STRING")
        def attr_id(state, p):
            return {"id": self.normalize_string(p[1].getstr())}

        @pg.production("attrlist : WORD = WORD")
        @pg.production("attrlist : WORD = STRING")
        def attrlist_single(state, p):
            return {p[0].getstr(): self.normalize_string(p[2].getstr())}

        @pg.production("attrlist : WORD")
        def attrlist_noval(state, p):
            return {p[0].getstr(): None}

        @pg.production("attrlist : attrlist , WORD = WORD")
        @pg.production("attrlist : attrlist , WORD = STRING")
        def attrlist_multiple(state, p):
            p[0] = {**p[0], p[2].getstr(): self.normalize_string(p[4].getstr())}
            return p[0]

        @pg.production("attrlist : attrlist , WORD")
        def attrlist_multiple_noval(state, p):
            p[0] = {**p[0], p[2].getstr(): None}
            return p[0]

        @pg.production("attr : [ attrlist ]", precedence="ID")
        def attr_list(state, p):
            return p[1]

        @pg.production("selector : selector attr")
        def selector_attr(state, p):
            for k, v in p[1].items():
                p[0].add_attr(k, v)
            return p[0]

        @pg.production("selector : selector CHILD selector")
        def selector_child(state, p):
            p[0].add_child(p[2])
            return p[0] # 2

        @pg.production("selector : selector SIBLING selector")
        def selector_next(state, p):
            p[0].add_next(p[2])
            return p[0] # 2

        @pg.production("selector : selector * WORD")
        def selector_mul(state, p):
            try:
                n = int(p[2].getstr())    
            except:
                raise TypeError("Not an integer.")
            p[0].duplicate()
            return p[0]

        @pg.production("selector : selector { WORD }")
        @pg.production("selector : selector { STRING }")
        def selector_innertext(state, p):
            p[0].innertext = self.normalize_string(p[2].getstr())
            return p[0]

        self.parser = pg.build()
        return self.parser
    
    def __init__(self):
        self._build_lexer()
        self._build_parser()
    
    def to_html(self, text) -> str:
        if text == "": return ""
        try:
            token = self.parser.parse(self.lexer.lex(text), state=[])
        except Exception as e:
            return str(e)
        self.last_token = token
        return token.repr()