from typing import List,Dict

from analyzer import Analyzer
from g4.CustomHLSLParser import CustomHLSLParser
from g4.CustomHLSLVisitor import CustomHLSLVisitor


'''
    Current support:
        * check for the functions not be supported on mobile  
'''


class CustomExpressionDeprecatedFunctionVisitor(CustomHLSLVisitor):
    def __init__(self, deprecated_functions):
        self._error_message: List[str] = list()
        self._deprecated_functions = deprecated_functions
    
    def getErrorMessage(self):
        return self._error_message
    
    # Fuzzy Search
    # def visitDeclaration(self, ctx: CustomHLSLParser.DeclarationContext):
    #     orign_code = ctx.getText()
    #     self.__check_whether_deprecated(function, orign_code)
    
    # Fuzzy Search
    # def visitExpressionStatement(self, ctx: CustomHLSLParser.ExpressionStatementContext):
    #     orign_code = ctx.getText()
    #     self.__check_whether_deprecated(function, orign_code)

    # Precision Search
    def visitPostfixExpression(self, ctx: CustomHLSLParser.PostfixExpressionContext):
        orign_code = ctx.getText()
        if ctx.primaryExpression():
            function = ctx.primaryExpression().getText()
            self.__check_whether_deprecated(function, orign_code)

    def __check_whether_deprecated(self, function: str, orign_code:str):
        for target_function in self._deprecated_functions:
            if target_function == function:
                    error_text = "{} can not be supported in mobile platform, Please use it\'s mobile version. The origin code is {}".format(target_function, orign_code)
                    print(error_text)
                    self._error_message.append(error_text)
    

class FunctionAnalyzer(Analyzer):
    def __init__(self) -> None:
        super().__init__()
        # Non-supported functions should be add to this list
        self._deprecated_functions = [
            "SceneTextureLookup",
        ]

    def analyze(self, file_name: str, output_csv: Dict):
        self._init_context(file_name, output_csv)
        custom_expression_source_code_map = self._custom_expression_source_code_map
        for custom_expression_name, custom_expression_code in custom_expression_source_code_map.items():
            visitor = CustomExpressionDeprecatedFunctionVisitor(self._deprecated_functions)
            self._visit_HLSL(custom_expression_code, visitor)
            if visitor.getErrorMessage():
                self._error_logger[custom_expression_name] = visitor.getErrorMessage()
        self._logInCSV()        