from typing import List,Dict

from singleton import Singleton
from g4.CustomHLSLParser import CustomHLSLParser
from g4.CustomHLSLLexer import CustomHLSLLexer
from g4.CustomHLSLVisitor import CustomHLSLVisitor
from antlr4 import *
from antlr4.error import ErrorListener


class Analyzer(metaclass = Singleton):
    # static value
    _custom_expression_source_code_map: Dict[str,str] = dict()
    _function_call_source_code_map: Dict[str,str] = dict()
    _is_init = False

    def __init__(self) -> None:
        self._error_logger: Dict[str, List] = dict()
        self._file_name = str()
        self._output_csv: Dict = dict()
    
    @classmethod
    def init_code_map(cls, code: str):
        if not cls._is_init:
            cls._custom_expression_source_code_map, cls._function_call_source_code_map = cls.__retrieval_source_code_map(code)
            cls._is_init = True

    @classmethod
    def reset_code_map(cls):
        cls._custom_expression_source_code_map = dict()
        cls._function_call_source_code_map = dict()
        cls._is_init = False

    @classmethod
    def __retrieval_source_code_map(cls, code):
        function_source_code_retrieval = FunctionSourceCodeRetrieval()
        cls.__visit_HLSL(code, function_source_code_retrieval)
        custom_expression_function_source_code_map = (
            function_source_code_retrieval.get_custom_expression_function_source_code()
        )
        function_call_source_code_map = (
            function_source_code_retrieval.get_function_call_source_code()
        )
        return custom_expression_function_source_code_map, function_call_source_code_map
    
    @staticmethod
    def __visit_HLSL(code: str, visitor: CustomHLSLVisitor):
        input_stream = InputStream(code)
        lexer = CustomHLSLLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = CustomHLSLParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(CustomHLSLErrorListener())
        tree = parser.compilationUnit()
        visitor.visit(tree)

    def analyze(self, file_name: str, output_csv: Dict):
        pass
    
    def _init_context(self, file_name: str, output_csv: Dict):
        self._file_name = file_name
        self._output_csv: Dict = output_csv
        self._error_logger: Dict[str, List] = dict()

    def _logInCSV(self):
        if self._error_logger:
            if self._output_csv.get(self._file_name):
                for expression_name in self._error_logger.keys():
                    if self._output_csv[self._file_name].get(expression_name):
                        self._output_csv[self._file_name][expression_name].extend(self._error_logger[expression_name])
                    else:
                        self._output_csv[self._file_name][expression_name] = self._error_logger[expression_name]
            else:
                self._output_csv[self._file_name] = self._error_logger

    def _visit_HLSL(self, code: str, visitor: CustomHLSLVisitor):
        self.__visit_HLSL(code, visitor)
    

class CustomHLSLErrorListener(ErrorListener.ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception(
            "Syntax error at line: {}, column: {}, offendingSymbol: {}, msg: {}".format(
                line, column, offendingSymbol, msg
            )
        )


class FunctionSourceCodeRetrieval(CustomHLSLVisitor):
    def __init__(self) -> None:
        self.__function_define_source_code_map = {}
        self.__function_call_source_code_map = {}

    # prune
    def visitExternalDeclaration(self, ctx: CustomHLSLParser.ExternalDeclarationContext):
        if ctx.functionDefinition():
            self.visit(ctx.functionDefinition())

    def visitFunctionDefinition(self, ctx: CustomHLSLParser.FunctionDefinitionContext):
        token_source = ctx.start.getTokenSource()
        input_stream = token_source.inputStream
        start, stop = ctx.start.start, ctx.stop.stop
        code = input_stream.getText(start, stop)

        function_name: str = (
            ctx.declarator().directDeclarator().directDeclarator().getText()
        )
        # start with CustomExpression
        if function_name.startswith("CustomExpression"):
            self.__function_define_source_code_map[function_name] = code
        elif code.find("CustomExpression") != -1:
            self.__function_call_source_code_map[function_name] = code
        # return super().visitFunctionDefinition(ctx)

    def get_custom_expression_function_source_code(self) -> Dict[str, str]:
        return self.__function_define_source_code_map

    def get_function_call_source_code(self) -> Dict[str, str]:
        return self.__function_call_source_code_map