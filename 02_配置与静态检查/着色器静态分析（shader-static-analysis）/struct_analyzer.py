from typing import List,Dict

from analyzer import Analyzer
from g4.CustomHLSLParser import CustomHLSLParser
from g4.CustomHLSLVisitor import CustomHLSLVisitor


'''
    Current support:
        * check for functions defined in Struct (should not be defined)
'''


class CustomExpressionStructVisitor(CustomHLSLVisitor):
    def __init__(self):
        self.__error_message: List[str] = list()

    def getErrorMessage(self):
        return self.__error_message
    
    # prune
    def visitBlockItemList(self, ctx: CustomHLSLParser.BlockItemListContext):
        for block_item in ctx.blockItem():
            if block_item.structDefinition():
                self.visit(block_item.structDefinition())

    def visitStructDefinationList(self, ctx:CustomHLSLParser.StructDefinationListContext):
        for struct_defination in ctx.structDefination():
            self.__check_whether_has_function_defination(struct_defination)

    def __check_whether_has_function_defination(self, struct_defination):
        if struct_defination.functionDefinition():
                function_name = struct_defination.functionDefinition().declarator().directDeclarator().directDeclarator().getText()
                error_text =  "Struct should not have function member {}".format(function_name) 
                print(error_text)
                self.__error_message.append(error_text)


class StructAnalyzer(Analyzer):
    def analyze(self, file_name: str, output_csv: Dict):
        self._init_context(file_name, output_csv)
        custom_expression_source_code_map = self._custom_expression_source_code_map
        for custom_expression_name, custom_expression_code in custom_expression_source_code_map.items():
            visitor = CustomExpressionStructVisitor()
            self._visit_HLSL(custom_expression_code, visitor)
            if visitor.getErrorMessage():
                self._error_logger[custom_expression_name] = visitor.getErrorMessage()
        self._logInCSV()        