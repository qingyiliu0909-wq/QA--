from typing import List, Dict

from analyzer import Analyzer
from calculator import *

from g4.CustomHLSLParser import CustomHLSLParser
from antlr4 import *


'''
    Current support:
        * check for the loops used in custom expression  
'''


class FunctionCallParamsResolver(CustomHLSLExpressionCalculator):
    def __init__(self, target_function_name: str) -> None:
        super().__init__()
        self.target_function_name = target_function_name
        self.params = []

    def visitBlockItemList(self, ctx: CustomHLSLParser.BlockItemListContext):
        print("visitBlockItemList")
        for blockItem in ctx.blockItem():
            text = blockItem.getText()
            if text.find(self.target_function_name) != -1:
                # self.visitCustomExpressionBlockItem(blockItem)
                self.visit(blockItem)
                break
            else:
                self.visit(blockItem)

    def visitPostfixExpression(self, ctx: CustomHLSLParser.PostfixExpressionContext):
        if ctx.argumentExpressionList():
            if ctx.primaryExpression().getText().find(self.target_function_name) != -1:
                for assignmentExpression in ctx.argumentExpressionList()[
                    0
                ].assignmentExpression():
                    param: CustomHLSLValue = self.visit(assignmentExpression)
                    self.show_variable_map()
                    if param.value_type == CustomHLSLValueType.VARIABLE:
                        param = self._get_variable_value(param.value)
                    self.params.append(param)
        return super().visitPostfixExpression(ctx)

    def get_params(self):
        return self.params


class CustomExpressionLoopCalculator(CustomHLSLExpressionCalculator):
    def __init__(self, params: List[CustomHLSLValue]) -> None:
        self.params = params
        self.current_for_init_variable: CustomHLSLValue = None
        self.current_for_init_value: CustomHLSLValue = None
        self.current_for_condition_variable: CustomHLSLValue = None
        self.current_for_condition_value: CustomHLSLValue = None
        self.current_for_condition_operator = None
        self.current_for_iteration_variable: CustomHLSLValue = None
        self.current_for_iteration_value: CustomHLSLValue = None
        self.wait_for_init = False
        self.wait_for_declaration = False
        self.wait_for_condition = False
        self.wait_for_iteration = False
        self.max_loop_count = 8
        self.nest_loop_stack = [1]
        self._error_message: List[str] = list()
        super().__init__()

    def visitForDeclaration(self, ctx: CustomHLSLParser.ForDeclarationContext):
        self.wait_for_declaration = True
        self.visit(ctx.forInitDeclaratorList())
        self.wait_for_declaration = False

    def visitForInitExpression(self, ctx: CustomHLSLParser.ForInitExpressionContext):
        self.wait_for_init = True
        # result = super().visitForInitExpression(ctx)
        # self.current_for_init_variable, self.current_for_init_value = (
        #     self.extractor.get_variable_and_value_from_for_init_expression(ctx)
        # )
        result = self.visit(ctx.expression())
        self.wait_for_init = False
        return result

    def visitForConditionExpression(
        self, ctx: CustomHLSLParser.ForConditionExpressionContext
    ):
        relationalExpression: CustomHLSLParser.RelationalExpressionContext = (
            ctx.forExpression()
            .assignmentExpression(0)
            .conditionalExpression()
            .logicalOrExpression()
            .logicalAndExpression(0)
            .inclusiveOrExpression(0)
            .exclusiveOrExpression(0)
            .andExpression(0)
            .equalityExpression(0)
            .relationalExpression(0)
        )
        self.current_for_condition_variable = self.visit(
            relationalExpression.shiftExpression(0)
        )
        self.current_for_condition_operator = operator_text_2_enum(
            relationalExpression.getChild(1).getText()
        )
        self.current_for_condition_value = self.visit(
            relationalExpression.shiftExpression(1)
        )

    def visitForIterationExpression(
        self, ctx: CustomHLSLParser.ForIterationExpressionContext
    ):
        (
            self.current_for_iteration_variable,
            self.current_for_iteration_value,
        ) = self.extractor.get_variable_and_value_from_for_iteration_expression(ctx)

    def visitAssignmentExpression(
        self, ctx: CustomHLSLParser.AssignmentExpressionContext
    ):
        result = None
        if ctx.conditionalExpression():
            result = self.visit(ctx.conditionalExpression())
        elif ctx.assignmentOperator():
            variable = self.visit(ctx.unaryExpression())
            value = self.visit(ctx.assignmentExpression())
            self._set_variable_value(variable, value)
            if self.wait_for_declaration or self.wait_for_init:
                self.current_for_init_variable = variable
                self.current_for_init_value = value
        else:
            raise Exception("Invalid assignment expression")
        print("assignment", ctx.getText(), result)
        return result

    def _calculate_multiple_loop_count(self, current_loop_count: int):
        result = current_loop_count
        for i in self.nest_loop_stack:
            result *= i
        return result

    def _check_loop_count_valid(self, text: str, loop_count: int):
        print("loop_count", loop_count, self.max_loop_count)
        if loop_count > self.max_loop_count:
            # raise Exception(
            #     "Loop count is too high, loop_count: {}, max_loop_count: {}, code: {}".format(
            #         loop_count, self.max_loop_count, text
            #     )
            # )
            error_text = "Loop count is too high, loop_count: {}, max_loop_count: {}, code: {}".format(
                loop_count, self.max_loop_count, text
            )
            self._error_message.append(error_text)

    def _check_for_expression_name_same(self):
        if (
            self.current_for_init_variable.value
            != self.current_for_condition_variable.value
            or self.current_for_condition_variable.value
            != self.current_for_iteration_variable.value
        ):
            raise Exception(
                "Invalid loop, init: {}, condition: {}, iteration: {}".format(
                    self.current_for_init_variable.value,
                    self.current_for_condition_variable.value,
                    self.current_for_iteration_variable.value,
                )
            )

    def _calculate_loop_count(
        self,
        init_value: CustomHLSLValue,
        condition_value: CustomHLSLValue,
        condition_operator: ConditionOperator,
        step: CustomHLSLValue,
    ):
        print(
            "init_value",
            init_value,
            "condition_value",
            condition_value,
            "condition_operator",
            condition_operator,
            "step",
            step,
        )
        if condition_value.value_type == CustomHLSLValueType.VARIABLE:
            condition_value = self._get_variable_value(condition_value.value)
        if condition_value.value_type == CustomHLSLValueType.UNKNOWN_VARIABLE:
            raise Exception(
                "Can't find variable value, variable: {}, probably it's a runtime parameter.".format(
                    condition_value.value
                )
            )

        if init_value.value_type == CustomHLSLValueType.VARIABLE:
            init_value.value = self._get_variable_value(init_value.value).value
        if init_value.value_type == CustomHLSLValueType.UNKNOWN_VARIABLE:
            raise Exception(
                "Can't find variable value, variable: {}, probably it's a runtime parameter.".format(
                    init_value.value
                )
            )

        if condition_operator == ConditionOperator.EQ:
            raise Exception("Unsupported condition operator")
        elif condition_operator == ConditionOperator.NE:
            raise Exception("Unsupported condition operator")
        elif condition_operator == ConditionOperator.LE:
            return (
                (condition_value.value - init_value.value) // step.value + 1
                if step.value > 0
                else -1
            )
        elif condition_operator == ConditionOperator.LT:
            if step.value <= 0:
                raise Exception(
                    "Invalid step value, init_value: {}, condition_value: {}, step: {}, condition_operator: {}".format(
                        init_value.value,
                        condition_value.value,
                        step.value,
                        condition_operator,
                    )
                )
            has_remainder = (condition_value.value - init_value.value) % step.value >= 1
            quotient = (condition_value.value - init_value.value) // step.value + 1
            return quotient if has_remainder else quotient - 1
        elif condition_operator == ConditionOperator.GE:
            return (
                (init_value.value - condition_value.value) // abs(step.value) + 1
                if step.value < 0
                else -1
            )
        elif condition_operator == ConditionOperator.GT:
            if step.value >= 0:
                raise Exception(
                    "Invalid step value, init_value: {}, condition_value: {}, step: {}, condition_operator: {}".format(
                        init_value, condition_value, step, condition_operator
                    )
                )
            has_remainder = (init_value.value - condition_value.value) % abs(
                step.value
            ) >= 1
            quotient = (init_value.value - condition_value.value) // abs(step.value) + 1
            return quotient if has_remainder else quotient - 1
        else:
            raise Exception("Invalid condition operator")

    def visitParameterList(self, ctx: CustomHLSLParser.ParameterListContext):
        for i in range(len(ctx.parameterDeclaration())):
            param_declaration: CustomHLSLParser.ParameterDeclarationContext = (
                ctx.parameterDeclaration(i)
            )
            variable = self.visit(param_declaration.declarator())
            if self.params[i].value_type == CustomHLSLValueType.UNKNOWN_VARIABLE:
                self._set_variable_value(
                    variable,
                    CustomHLSLValue(
                        CustomHLSLValueType.UNKNOWN_VARIABLE, variable.value
                    ),
                )
            else:
                self._set_variable_value(variable, self.params[i])
            self.show_variable_map()

    def visitForIterationStatement(
        self, ctx: CustomHLSLParser.ForIterationStatementContext
    ):
        self.visitForCondition(ctx.forCondition())
        self._check_for_expression_name_same()
        loop_count = self._calculate_multiple_loop_count(
            self._calculate_loop_count(
                self.current_for_init_value,
                self.current_for_condition_value,
                self.current_for_condition_operator,
                self.current_for_iteration_value,
            )
        )
        self._check_loop_count_valid(ctx.getText(), loop_count)
        self.nest_loop_stack.append(loop_count)
        self.visitForStatement(ctx.forStatement())
        self.nest_loop_stack.pop()

    def visitWhileIterationStatement(
        self, ctx: CustomHLSLParser.WhileIterationStatementContext
    ):
        relationalExpression: CustomHLSLParser.RelationalExpressionContext = (
            ctx.expression()
            .assignmentExpression(0)
            .conditionalExpression()
            .logicalOrExpression()
            .logicalAndExpression(0)
            .inclusiveOrExpression(0)
            .exclusiveOrExpression(0)
            .andExpression(0)
            .equalityExpression(0)
            .relationalExpression(0)
        )
        current_while_condition_variable = self.visit(
            relationalExpression.shiftExpression(0)
        )
        current_while_condition_operator = operator_text_2_enum(
            relationalExpression.getChild(1).getText()
        )
        current_while_condition_value = self.visit(
            relationalExpression.shiftExpression(1)
        )
        loop_count = self._calculate_multiple_loop_count(
            self._calculate_loop_count(
                current_while_condition_variable,
                current_while_condition_value,
                current_while_condition_operator,
                CustomHLSLValue(CustomHLSLValueType.VALUE, 1),
            )
        )
        self.nest_loop_stack.append(loop_count)
        self.visit(ctx.statement())
        self.nest_loop_stack.pop()
    
    def getErrorMessage(self):
        return self._error_message


class LoopAnalyzer(Analyzer):
    def analyze(self, file_name: str, output_csv: Dict):
        self._init_context(file_name, output_csv)
        function_define_source_code_map = self._custom_expression_source_code_map
        function_call_source_code_map = self._function_call_source_code_map
        for (
            custom_expression_function_name,
            custom_expression_function_code,
        ) in function_define_source_code_map.items():
            for (
                call_context_function_name,
                call_context_function_code,
            ) in function_call_source_code_map.items():
                if self._call_function_or_not(
                    custom_expression_function_name, call_context_function_code
                ):
                    visitor = CustomExpressionLoopCalculator(
                                self._resolve_params(
                                custom_expression_function_name,
                                call_context_function_code,
                                )
                            )
                    self._visit_HLSL(custom_expression_function_code, visitor)
                    if visitor.getErrorMessage():
                        self._error_logger[custom_expression_function_name] = visitor.getErrorMessage()
        self._logInCSV()

    def _resolve_params(
        self, custom_expression_function_name, call_context_function_code
    ):
        param_resolver = FunctionCallParamsResolver(custom_expression_function_name)
        self._visit_HLSL(call_context_function_code, param_resolver)
        params = param_resolver.get_params()
        return params

    def _call_function_or_not(
        self, custom_expression_function_name, call_context_function_code
    ):
        return call_context_function_code.find(custom_expression_function_name) != -1