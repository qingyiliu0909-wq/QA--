from enum import Enum
from g4.CustomHLSLVisitor import CustomHLSLVisitor
from g4.CustomHLSLParser import CustomHLSLParser

class CustomHLSLValueType(Enum):
    VALUE = 1
    VARIABLE = 2
    UNKNOWN_VARIABLE = 3

class CustomHLSLValue:
    def __init__(self, value_type: CustomHLSLValueType, value: int | str) -> None:
        self.value_type = value_type
        self.value = value

    def __str__(self) -> str:
        return "value_type: {}, value: {}".format(self.value_type, self.value)

    def __add__(self, other: "CustomHLSLValue") -> "CustomHLSLValue":
        if (
            self.value_type == CustomHLSLValueType.VALUE
            and other.value_type == CustomHLSLValueType.VALUE
        ):
            return CustomHLSLValue(CustomHLSLValueType.VALUE, self.value + other.value)
        else:
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE,
                "{} + {}".format(self.value, other.value),
            )

    def __sub__(self, other: "CustomHLSLValue") -> "CustomHLSLValue":
        if (
            self.value_type == CustomHLSLValueType.VALUE
            and other.value_type == CustomHLSLValueType.VALUE
        ):
            return CustomHLSLValue(CustomHLSLValueType.VALUE, self.value - other.value)
        else:
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE,
                "{} - {}".format(self.value, other.value),
            )

    def __mul__(self, other: "CustomHLSLValue") -> "CustomHLSLValue":
        if (
            self.value_type == CustomHLSLValueType.VALUE
            and other.value_type == CustomHLSLValueType.VALUE
        ):
            return CustomHLSLValue(CustomHLSLValueType.VALUE, self.value * other.value)
        elif (
            (
                self.value_type == CustomHLSLValueType.UNKNOWN_VARIABLE
                or other.value_type == CustomHLSLValueType.UNKNOWN_VARIABLE
            )
            and self.value_type != CustomHLSLValueType.VARIABLE
            and other.value_type != CustomHLSLValueType.VARIABLE
        ):
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE,
                "{} * {}".format(self.value, other.value),
            )
        else:
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE,
                "{} * {}".format(self.value, other.value),
            )

    def __truediv__(self, other: "CustomHLSLValue") -> "CustomHLSLValue":
        if (
            self.value_type == CustomHLSLValueType.VALUE
            and other.value_type == CustomHLSLValueType.VALUE
        ):
            return CustomHLSLValue(CustomHLSLValueType.VALUE, self.value / other.value)
        else:
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE,
                "{} / {}".format(self.value, other.value),
            )

    def __mod__(self, other: "CustomHLSLValue") -> "CustomHLSLValue":
        if (
            self.value_type == CustomHLSLValueType.VALUE
            and other.value_type == CustomHLSLValueType.VALUE
        ):
            return CustomHLSLValue(CustomHLSLValueType.VALUE, self.value % other.value)
        else:
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE,
                "{} % {}".format(self.value, other.value),
            )

    def __neg__(self) -> "CustomHLSLValue":
        if self.value_type == CustomHLSLValueType.VALUE:
            return CustomHLSLValue(CustomHLSLValueType.VALUE, -self.value)
        else:
            return CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE, "-{}".format(self.value)
            )

class PositiveOrNegative(Enum):
    POSITIVE = 1
    NEGATIVE = -1

class ConditionOperator(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="


def operator_text_2_enum(operator_text: str) -> ConditionOperator:
    if operator_text == "==":
        return ConditionOperator.EQ
    elif operator_text == "!=":
        return ConditionOperator.NE
    elif operator_text == "<":
        return ConditionOperator.LT
    elif operator_text == "<=":
        return ConditionOperator.LE
    elif operator_text == ">":
        return ConditionOperator.GT
    elif operator_text == ">=":
        return ConditionOperator.GE
    else:
        raise Exception("Invalid operator text")

def convert_cpp_float_to_python(cpp_float_str):
    try:
        python_float = float(cpp_float_str)
    except ValueError as e:
        if "f" in cpp_float_str:
            cpp_float_str = cpp_float_str.rstrip("f")
        try:
            python_float = float(cpp_float_str)
        except ValueError:
            return None
    return python_float

class CustomHLSLNodeExtractor:
    def __init__(self) -> None:
        pass

    def get_variable_identifier_from_expression(
        expression: CustomHLSLParser.ExpressionContext,
    ):
        return (
            expression.assignment_expression()
            .constant_expression()
            .binary_expression()
            .unary_expression()
            .postfix_expression()
            .postfix_expression()
            .primary_expression()
            .variable_identifier()
        )

    def get_variable_or_const_value_from_unary_expression(
        self,
        unary_expression: CustomHLSLParser.UnaryExpressionContext,
    ):
        positive_or_negative = PositiveOrNegative.POSITIVE
        if unary_expression.getChildCount() == 1:
            primary_expression: CustomHLSLParser.PrimaryExpressionContext = (
                unary_expression.postfixExpression().primaryExpression()
            )
        else:
            primary_expression: CustomHLSLParser.PrimaryExpressionContext = (
                unary_expression.castExpression()
                .unaryExpression()
                .postfixExpression()
                .primaryExpression()
            )
            positive_or_negative = PositiveOrNegative.NEGATIVE
        if primary_expression.Identifier() is None:
            return positive_or_negative, CustomHLSLValue(
                CustomHLSLValueType.VALUE, int(primary_expression.getText())
            )
        else:
            variable_identifier = primary_expression.Identifier().getText()
            raise Exception(
                "Unsupported condition expression, variable_identifier: {}".format(
                    variable_identifier
                )
            )

    def get_value_from_initializer(initializer: CustomHLSLParser.InitializerContext):
        unary_expression: CustomHLSLParser.Unary_expressionContext = (
            initializer.assignment_expression()
            .constant_expression()
            .binary_expression()
            .unary_expression()
        )
        positive_or_negative, value = self.get_variable_or_const_value_from_unary_expression(
            unary_expression
        )
        if positive_or_negative == PositiveOrNegative.POSITIVE:
            return value
        else:
            return -value

    def get_variable_and_value_from_for_init_expression(
        self,
        for_init_expression: CustomHLSLParser.ForInitExpressionContext,
    ) -> tuple[str, int]:
        assignment_expression: CustomHLSLParser.AssignmentExpressionContext = (
            for_init_expression.expression().assignmentExpression(0)
        )
        variable = (
            assignment_expression.unaryExpression()
            .postfixExpression()
            .primaryExpression()
            .Identifier()
            .getText()
        )
        unary_expression: CustomHLSLParser.UnaryExpressionContext = (
            assignment_expression.assignmentExpression()
            .conditionalExpression()
            .logicalOrExpression()
            .logicalAndExpression(0)
            .inclusiveOrExpression(0)
            .exclusiveOrExpression(0)
            .andExpression(0)
            .equalityExpression(0)
            .relationalExpression(0)
            .shiftExpression(0)
            .additiveExpression(0)
            .multiplicativeExpression(0)
            .castExpression(0)
            .unaryExpression()
        )
        positive_or_negative, value = (
            self.get_variable_or_const_value_from_unary_expression(unary_expression)
        )
        return variable, (
            value if positive_or_negative == PositiveOrNegative.POSITIVE else -value
        )

    def get_variable_and_value_from_for_declaration(
        self,
        for_declaration: CustomHLSLParser.ForDeclarationContext,
    ) -> tuple[str, int]:
        initDeclarator: CustomHLSLParser.InitDeclaratorContext = (
            for_declaration.initDeclaratorList().initDeclarator(0)
        )
        variable = initDeclarator.declarator().directDeclarator().Identifier().getText()
        unary_expression: CustomHLSLParser.UnaryExpressionContext = (
            initDeclarator.initializer()
            .assignmentExpression()
            .conditionalExpression()
            .logicalOrExpression()
            .logicalAndExpression(0)
            .inclusiveOrExpression(0)
            .exclusiveOrExpression(0)
            .andExpression(0)
            .equalityExpression(0)
            .relationalExpression(0)
            .shiftExpression(0)
            .additiveExpression(0)
            .multiplicativeExpression(0)
            .castExpression(0)
            .unaryExpression()
        )
        positive_or_negative, value = (
            self.get_variable_or_const_value_from_unary_expression(unary_expression)
        )
        return variable, (
            value if positive_or_negative == PositiveOrNegative.POSITIVE else -value
        )

    def get_variable_operator_and_value_from_for_condition(
        self,
        for_condition_expression: CustomHLSLParser.ForConditionExpressionContext,
    ) -> tuple[str, ConditionOperator, int]:
        relationalExpression: CustomHLSLParser.RelationalExpressionContext = (
            for_condition_expression.forExpression()
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
        variable = (
            relationalExpression.shiftExpression(0)
            .additiveExpression(0)
            .multiplicativeExpression(0)
            .castExpression(0)
            .unaryExpression()
            .postfixExpression()
            .primaryExpression()
            .Identifier()
            .getText()
        )
        operator = operator_text_2_enum(relationalExpression.getChild(1).getText())
        castExpression: CustomHLSLParser.CastExpressionContext = (
            relationalExpression.shiftExpression(1)
            .additiveExpression(0)
            .multiplicativeExpression(0)
            .castExpression(0)
        )
        if castExpression.getChildCount() == 1:
            primary_expression: CustomHLSLParser.PrimaryExpressionContext = (
                castExpression.unaryExpression().postfixExpression().primaryExpression()
            )

            if primary_expression.Identifier() is None:
                return variable, operator, int(primary_expression.getText())
            else:
                variable_identifier = primary_expression.Identifier().getText()
                raise Exception(
                    "Unsupported condition expression, variable_identifier: {}".format(
                        variable_identifier
                    )
                )
        else:
            raise Exception(
                "Unsupported condition expression, castExpression: {}".format(
                    castExpression.getText()
                )
            )

    def get_variable_and_value_from_for_iteration_expression(
        self,
        for_iteration_expression: CustomHLSLParser.ForIterationExpressionContext,
    ) -> tuple[str, int]:
        unary_expression: CustomHLSLParser.UnaryExpressionContext = (
            for_iteration_expression.forExpression()
            .assignmentExpression(0)
            .conditionalExpression()
            .logicalOrExpression()
            .logicalAndExpression(0)
            .inclusiveOrExpression(0)
            .exclusiveOrExpression(0)
            .andExpression(0)
            .equalityExpression(0)
            .relationalExpression(0)
            .shiftExpression(0)
            .additiveExpression(0)
            .multiplicativeExpression(0)
            .castExpression(0)
            .unaryExpression()
        )

        # x++
        if unary_expression.getChildCount() == 1:
            postfix_expression: CustomHLSLParser.PostfixExpressionContext = (
                unary_expression.postfixExpression()
            )
            variable = CustomHLSLValue(
                CustomHLSLValueType.VARIABLE,
                postfix_expression.primaryExpression().Identifier().getText(),
            )
            if postfix_expression.getChild(1).getText() == "++":
                value = CustomHLSLValue(CustomHLSLValueType.VALUE, 1)
            elif postfix_expression.getChild(1).getText() == "--":
                value = CustomHLSLValue(CustomHLSLValueType.VALUE, -1)
            else:
                raise Exception("Invalid step expression")
            return variable, value
        else:
            # ++x
            if unary_expression.getChild(0).getText() == "++":
                value = CustomHLSLValue(CustomHLSLValueType.VALUE, 1)
            elif unary_expression.getChild(0).getText() == "--":
                value = CustomHLSLValue(CustomHLSLValueType.VALUE, -1)
            else:
                raise Exception("Invalid step expression")

            variable = CustomHLSLValue(
                CustomHLSLValueType.VARIABLE,
                unary_expression.postfixExpression()
                .primaryExpression()
                .Identifier()
                .getText(),
            )
            return variable, value

    # def get_variable_operator_and_value_from_for_condition(
    #     for_condition: CustomHLSLParser.ConditionContext,
    # ) -> tuple[str, ConditionOperator, int]:
    #     binary_expression: CustomHLSLParser.Binary_expressionContext = (
    #         for_condition.expression()
    #         .assignment_expression()
    #         .constant_expression()
    #         .binary_expression()
    #     )
    #     variable = (
    #         binary_expression.binary_expression()[0]
    #         .unary_expression()
    #         .postfix_expression()
    #         .primary_expression()
    #         .variable_identifier()
    #         .getText()
    #     )
    #     operator = operator_text_2_enum(binary_expression.getChild(1).getText())
    #     primary_expression: CustomHLSLParser.Primary_expressionContext = (
    #         binary_expression.binary_expression()[1]
    #         .unary_expression()
    #         .postfix_expression()
    #         .primary_expression()
    #     )
    #     # 如果是常量
    #     if primary_expression.variable_identifier() is None:
    #         return variable, operator, int(primary_expression.getText())
    #     else:
    #         variable_identifier = primary_expression.variable_identifier().getText()
    #         raise Exception(
    #             "Unsupported condition expression, variable_identifier: {}".format(
    #                 variable_identifier
    #             )
    #         )

    # def get_variable_and_value_from_for_step_expression(
    #     for_step_expression: CustomHLSLParser.ExpressionContext,
    # ) -> tuple[str, int]:
    #     unary_expression: CustomHLSLParser.Unary_expressionContext = (
    #         for_step_expression.assignment_expression()
    #         .constant_expression()
    #         .binary_expression()
    #         .unary_expression()
    #     )

    #     # x++
    #     if unary_expression.getChildCount() == 1:
    #         postfix_expression: CustomHLSLParser.Postfix_expressionContext = (
    #             unary_expression.postfix_expression()
    #         )
    #         variable = (
    #             postfix_expression.postfix_expression()
    #             .primary_expression()
    #             .variable_identifier()
    #             .getText()
    #         )
    #         if postfix_expression.getChild(1).getText() == "++":
    #             value = 1
    #         elif postfix_expression.getChild(1).getText() == "--":
    #             value = -1
    #         else:
    #             raise Exception("Invalid step expression")
    #         return variable, value
    #     else:
    #         # ++x
    #         if unary_expression.getChild(0).getText() == "++":
    #             value = 1
    #         elif unary_expression.getChild(0).getText() == "--":
    #             value = -1
    #         else:
    #             raise Exception("Invalid step expression")

    #         variable = (
    #             unary_expression.unary_expression()
    #             .postfix_expression()
    #             .primary_expression()
    #             .variable_identifier()
    #             .getText()
    #         )
    #         return variable, value

class CustomHLSLExpressionCalculator(CustomHLSLVisitor):
    def __init__(self) -> None:
        self.extractor = CustomHLSLNodeExtractor()
        self.value_map = {}

    def _set_variable_value(self, variable: CustomHLSLValue, value: CustomHLSLValue):
        print("set_variable_value", variable, value)
        self.value_map[variable.value] = value

    def _get_variable_value(self, name: str) -> CustomHLSLValue:
        if name not in self.value_map:
            return CustomHLSLValue(CustomHLSLValueType.UNKNOWN_VARIABLE, name)
        return self.value_map[name]

    def show_variable_map(self):
        print("variable_map_start")
        for k, v in self.value_map.items():
            print(k, v)
        print("variable_map_end")

    def visitForDeclaration(self, ctx: CustomHLSLParser.ForDeclarationContext):
        self.visit(ctx.forInitDeclaratorList())

    def visitInitDeclarator(self, ctx: CustomHLSLParser.InitDeclaratorContext):
        result = None
        value = None
        if ctx.initializer():
            value = self.visit(ctx.initializer())
        variable = self.visit(ctx.declarator())
        if value and variable:
            self._set_variable_value(variable, value)
        print("init declarator", ctx.getText(), result)
        return result

    def visitDeclarator(self, ctx: CustomHLSLParser.DeclaratorContext):
        result = None
        if ctx.getChildCount() == 1:
            result = self.visit(ctx.directDeclarator())
        else:
            raise Exception("Invalid declarator")
        print("declarator", ctx.getText(), result)
        return result

    def visitDirectDeclarator(self, ctx: CustomHLSLParser.DirectDeclaratorContext):
        result = None
        if ctx.Identifier():
            result = CustomHLSLValue(
                CustomHLSLValueType.VARIABLE, ctx.Identifier().getText()
            )
        else:
            return self.visitChildren(ctx)
        print("direct declarator", ctx.getText(), result)
        return result

    def visitForInitExpression(self, ctx: CustomHLSLParser.ForInitExpressionContext):
        result = self.visit(ctx.expression())
        return result

    def visitForStatement(self, ctx: CustomHLSLParser.ForStatementContext):
        return super().visitForStatement(ctx)

    def visitInitializer(self, ctx: CustomHLSLParser.InitializerContext):
        result = None
        if ctx.assignmentExpression():
            result = self.visit(ctx.assignmentExpression())
        else:
            result = CustomHLSLValue(
                CustomHLSLValueType.UNKNOWN_VARIABLE, ctx.getText()
            )
        print("initializer", ctx.getText(), result)
        return result

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
        else:
            raise Exception("Invalid assignment expression")
        print("assignment", ctx.getText(), result)
        return result

    def visitConditionalExpression(
        self, ctx: CustomHLSLParser.ConditionalExpressionContext
    ):
        result = self.visit(ctx.logicalOrExpression())
        print("conditional", ctx.getText(), result)
        return result

    def visitLogicalOrExpression(
        self, ctx: CustomHLSLParser.LogicalOrExpressionContext
    ):
        result = self.visit(ctx.logicalAndExpression(0))
        print("logical or", ctx.getText(), result)
        return result

    def visitLogicalAndExpression(
        self, ctx: CustomHLSLParser.LogicalAndExpressionContext
    ):
        result = self.visit(ctx.inclusiveOrExpression(0))
        print("logical and", ctx.getText(), result)
        return result

    def visitInclusiveOrExpression(
        self, ctx: CustomHLSLParser.InclusiveOrExpressionContext
    ):
        result = self.visit(ctx.exclusiveOrExpression(0))
        print("inclusive or", ctx.getText(), result)
        return result

    def visitExclusiveOrExpression(
        self, ctx: CustomHLSLParser.ExclusiveOrExpressionContext
    ):
        result = self.visit(ctx.andExpression(0))
        print("exclusive or", ctx.getText(), result)
        return result

    def visitAndExpression(self, ctx: CustomHLSLParser.AndExpressionContext):
        result = self.visit(ctx.equalityExpression(0))
        print("and", ctx.getText(), result)
        return result

    def visitEqualityExpression(self, ctx: CustomHLSLParser.EqualityExpressionContext):
        result = self.visit(ctx.relationalExpression(0))
        print("equality", ctx.getText(), result)
        return result

    def visitRelationalExpression(
        self, ctx: CustomHLSLParser.RelationalExpressionContext
    ):
        result = self.visit(ctx.shiftExpression(0))
        print("relational", ctx.getText(), result)
        return result

    def visitShiftExpression(self, ctx: CustomHLSLParser.ShiftExpressionContext):
        result = self.visit(ctx.additiveExpression(0))
        print("shift", ctx.getText(), result)
        return result

    def visitAdditiveExpression(self, ctx: CustomHLSLParser.AdditiveExpressionContext):
        result = 0
        a = self.visit(ctx.getChild(0))
        if ctx.getChildCount() > 1:
            operator = ctx.getChild(1).getText()
            b = self.visit(ctx.getChild(2))
            if operator == "+":
                result = a + b
            elif operator == "-":
                result = a - b
            else:
                raise Exception("Invalid operator")
        else:
            result = a
        print("add", ctx.getText(), result)
        return result

    def visitMultiplicativeExpression(
        self, ctx: CustomHLSLParser.MultiplicativeExpressionContext
    ):
        result = 0
        a = self.visit(ctx.getChild(0))
        if ctx.getChildCount() > 1:
            operator = ctx.getChild(1).getText()
            b = self.visit(ctx.getChild(2))
            if operator == "*":
                result = a * b
            elif operator == "/":
                result = a / b
            elif operator == "%":
                result = a % b
            else:
                raise Exception("Invalid operator")
        else:
            result = a
        print("mul", ctx.getText(), result)
        return result

    def visitCastExpression(self, ctx: CustomHLSLParser.CastExpressionContext):
        result = None
        if ctx.castExpression():
            result = self.visit(ctx.castExpression())
        elif ctx.unaryExpression():
            result = self.visit(ctx.unaryExpression())
        elif ctx.conditionalExpression():
            result = self.visit(ctx.conditionalExpression())
        else:
            raise Exception("Invalid cast expression")
        print("cast", ctx.getText(), result)
        return result

    def visitUnaryExpression(self, ctx: CustomHLSLParser.UnaryExpressionContext):
        result = None
        if ctx.postfixExpression():
            post_expression_result = self.visit(ctx.postfixExpression())
            if ctx.PlusPlus():
                result = post_expression_result + 1
            elif ctx.MinusMinus():
                result = post_expression_result - 1
            else:
                result = post_expression_result
        elif ctx.unaryOperator():
            if ctx.unaryOperator().getText() == "-":
                result = -self.visit(ctx.castExpression())
            else:
                raise Exception(
                    "Invalid unary expression, text: {}".format(ctx.getText())
                )
        else:
            raise Exception("Invalid unary expression, text: {}".format(ctx.getText()))
        print("unary", ctx.getText(), result)
        return result

    def visitPostfixExpression(self, ctx: CustomHLSLParser.PostfixExpressionContext):
        result = None
        if ctx.getChildCount() > 1:
            # raise Exception("Invalid postfix expression,text: {}".format(ctx.getText()))
            return CustomHLSLValue(CustomHLSLValueType.UNKNOWN_VARIABLE, ctx.getText())
        if ctx.primaryExpression():
            result = self.visit(ctx.primaryExpression())
        else:
            raise Exception("Invalid postfix expression")
        print("postfix", ctx.getText(), result)
        return result

    def visitPrimaryExpression(self, ctx: CustomHLSLParser.PrimaryExpressionContext):
        result = None
        if ctx.Identifier():
            return CustomHLSLValue(
                CustomHLSLValueType.VARIABLE, ctx.Identifier().getText()
            )
        elif ctx.Constant():
            text: str = ctx.Constant().getText()
            if text.isdigit():
                result = CustomHLSLValue(CustomHLSLValueType.VALUE, int(text))
            elif "." in text:
                result = CustomHLSLValue(
                    CustomHLSLValueType.VALUE, convert_cpp_float_to_python(text)
                )
        elif ctx.StringLiteral():
            result = CustomHLSLValue(
                CustomHLSLValueType.VALUE, ctx.StringLiteral().getText()
            )
        elif ctx.expression():
            result = self.visit(ctx.expression())
        else:
            raise Exception("Invalid primary expression")
        print("primary", ctx.getText(), result)
        return result

