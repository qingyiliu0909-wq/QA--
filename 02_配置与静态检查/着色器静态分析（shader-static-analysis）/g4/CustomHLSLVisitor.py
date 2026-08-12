# Generated from CustomHLSL.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CustomHLSLParser import CustomHLSLParser
else:
    from CustomHLSLParser import CustomHLSLParser

# This class defines a complete generic visitor for a parse tree produced by CustomHLSLParser.

class CustomHLSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CustomHLSLParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:CustomHLSLParser.PrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#genericSelection.
    def visitGenericSelection(self, ctx:CustomHLSLParser.GenericSelectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#genericAssocList.
    def visitGenericAssocList(self, ctx:CustomHLSLParser.GenericAssocListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#genericAssociation.
    def visitGenericAssociation(self, ctx:CustomHLSLParser.GenericAssociationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#postfixExpression.
    def visitPostfixExpression(self, ctx:CustomHLSLParser.PostfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#argumentExpressionList.
    def visitArgumentExpressionList(self, ctx:CustomHLSLParser.ArgumentExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#unaryExpression.
    def visitUnaryExpression(self, ctx:CustomHLSLParser.UnaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#unaryOperator.
    def visitUnaryOperator(self, ctx:CustomHLSLParser.UnaryOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#castExpression.
    def visitCastExpression(self, ctx:CustomHLSLParser.CastExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:CustomHLSLParser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#additiveExpression.
    def visitAdditiveExpression(self, ctx:CustomHLSLParser.AdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#shiftExpression.
    def visitShiftExpression(self, ctx:CustomHLSLParser.ShiftExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#relationalExpression.
    def visitRelationalExpression(self, ctx:CustomHLSLParser.RelationalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#equalityExpression.
    def visitEqualityExpression(self, ctx:CustomHLSLParser.EqualityExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#andExpression.
    def visitAndExpression(self, ctx:CustomHLSLParser.AndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#exclusiveOrExpression.
    def visitExclusiveOrExpression(self, ctx:CustomHLSLParser.ExclusiveOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#inclusiveOrExpression.
    def visitInclusiveOrExpression(self, ctx:CustomHLSLParser.InclusiveOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:CustomHLSLParser.LogicalAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx:CustomHLSLParser.LogicalOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#conditionalExpression.
    def visitConditionalExpression(self, ctx:CustomHLSLParser.ConditionalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx:CustomHLSLParser.AssignmentExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx:CustomHLSLParser.AssignmentOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#expression.
    def visitExpression(self, ctx:CustomHLSLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#constantExpression.
    def visitConstantExpression(self, ctx:CustomHLSLParser.ConstantExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#declaration.
    def visitDeclaration(self, ctx:CustomHLSLParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#declarationSpecifiers.
    def visitDeclarationSpecifiers(self, ctx:CustomHLSLParser.DeclarationSpecifiersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#declarationSpecifiers2.
    def visitDeclarationSpecifiers2(self, ctx:CustomHLSLParser.DeclarationSpecifiers2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#declarationSpecifier.
    def visitDeclarationSpecifier(self, ctx:CustomHLSLParser.DeclarationSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#initDeclaratorList.
    def visitInitDeclaratorList(self, ctx:CustomHLSLParser.InitDeclaratorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#initDeclarator.
    def visitInitDeclarator(self, ctx:CustomHLSLParser.InitDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forInitDeclaratorList.
    def visitForInitDeclaratorList(self, ctx:CustomHLSLParser.ForInitDeclaratorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forInitDeclarator.
    def visitForInitDeclarator(self, ctx:CustomHLSLParser.ForInitDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#storageClassSpecifier.
    def visitStorageClassSpecifier(self, ctx:CustomHLSLParser.StorageClassSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#typeSpecifier.
    def visitTypeSpecifier(self, ctx:CustomHLSLParser.TypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structOrUnionSpecifier.
    def visitStructOrUnionSpecifier(self, ctx:CustomHLSLParser.StructOrUnionSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structOrUnion.
    def visitStructOrUnion(self, ctx:CustomHLSLParser.StructOrUnionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDeclarationList.
    def visitStructDeclarationList(self, ctx:CustomHLSLParser.StructDeclarationListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDeclaration.
    def visitStructDeclaration(self, ctx:CustomHLSLParser.StructDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#specifierQualifierList.
    def visitSpecifierQualifierList(self, ctx:CustomHLSLParser.SpecifierQualifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDeclaratorList.
    def visitStructDeclaratorList(self, ctx:CustomHLSLParser.StructDeclaratorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDeclarator.
    def visitStructDeclarator(self, ctx:CustomHLSLParser.StructDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#enumSpecifier.
    def visitEnumSpecifier(self, ctx:CustomHLSLParser.EnumSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#enumeratorList.
    def visitEnumeratorList(self, ctx:CustomHLSLParser.EnumeratorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#enumerator.
    def visitEnumerator(self, ctx:CustomHLSLParser.EnumeratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#enumerationConstant.
    def visitEnumerationConstant(self, ctx:CustomHLSLParser.EnumerationConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#atomicTypeSpecifier.
    def visitAtomicTypeSpecifier(self, ctx:CustomHLSLParser.AtomicTypeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#typeQualifier.
    def visitTypeQualifier(self, ctx:CustomHLSLParser.TypeQualifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#functionSpecifier.
    def visitFunctionSpecifier(self, ctx:CustomHLSLParser.FunctionSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#alignmentSpecifier.
    def visitAlignmentSpecifier(self, ctx:CustomHLSLParser.AlignmentSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#declarator.
    def visitDeclarator(self, ctx:CustomHLSLParser.DeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#directDeclarator.
    def visitDirectDeclarator(self, ctx:CustomHLSLParser.DirectDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#vcSpecificModifer.
    def visitVcSpecificModifer(self, ctx:CustomHLSLParser.VcSpecificModiferContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#gccDeclaratorExtension.
    def visitGccDeclaratorExtension(self, ctx:CustomHLSLParser.GccDeclaratorExtensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#gccAttributeSpecifier.
    def visitGccAttributeSpecifier(self, ctx:CustomHLSLParser.GccAttributeSpecifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#gccAttributeList.
    def visitGccAttributeList(self, ctx:CustomHLSLParser.GccAttributeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#gccAttribute.
    def visitGccAttribute(self, ctx:CustomHLSLParser.GccAttributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#nestedParenthesesBlock.
    def visitNestedParenthesesBlock(self, ctx:CustomHLSLParser.NestedParenthesesBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#pointer.
    def visitPointer(self, ctx:CustomHLSLParser.PointerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#typeQualifierList.
    def visitTypeQualifierList(self, ctx:CustomHLSLParser.TypeQualifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#parameterTypeList.
    def visitParameterTypeList(self, ctx:CustomHLSLParser.ParameterTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#parameterList.
    def visitParameterList(self, ctx:CustomHLSLParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#parameterDeclaration.
    def visitParameterDeclaration(self, ctx:CustomHLSLParser.ParameterDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#identifierList.
    def visitIdentifierList(self, ctx:CustomHLSLParser.IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#typeName.
    def visitTypeName(self, ctx:CustomHLSLParser.TypeNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#abstractDeclarator.
    def visitAbstractDeclarator(self, ctx:CustomHLSLParser.AbstractDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#directAbstractDeclarator.
    def visitDirectAbstractDeclarator(self, ctx:CustomHLSLParser.DirectAbstractDeclaratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#typedefName.
    def visitTypedefName(self, ctx:CustomHLSLParser.TypedefNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#initializer.
    def visitInitializer(self, ctx:CustomHLSLParser.InitializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#initializerList.
    def visitInitializerList(self, ctx:CustomHLSLParser.InitializerListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#designation.
    def visitDesignation(self, ctx:CustomHLSLParser.DesignationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#designatorList.
    def visitDesignatorList(self, ctx:CustomHLSLParser.DesignatorListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#designator.
    def visitDesignator(self, ctx:CustomHLSLParser.DesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#staticAssertDeclaration.
    def visitStaticAssertDeclaration(self, ctx:CustomHLSLParser.StaticAssertDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#statement.
    def visitStatement(self, ctx:CustomHLSLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#labeledStatement.
    def visitLabeledStatement(self, ctx:CustomHLSLParser.LabeledStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#compoundStatement.
    def visitCompoundStatement(self, ctx:CustomHLSLParser.CompoundStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#blockItemList.
    def visitBlockItemList(self, ctx:CustomHLSLParser.BlockItemListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#blockItem.
    def visitBlockItem(self, ctx:CustomHLSLParser.BlockItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#expressionStatement.
    def visitExpressionStatement(self, ctx:CustomHLSLParser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#selectionStatement.
    def visitSelectionStatement(self, ctx:CustomHLSLParser.SelectionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#iterationStatement.
    def visitIterationStatement(self, ctx:CustomHLSLParser.IterationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#whileIterationStatement.
    def visitWhileIterationStatement(self, ctx:CustomHLSLParser.WhileIterationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forIterationStatement.
    def visitForIterationStatement(self, ctx:CustomHLSLParser.ForIterationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forStatement.
    def visitForStatement(self, ctx:CustomHLSLParser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forCondition.
    def visitForCondition(self, ctx:CustomHLSLParser.ForConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forInitExpression.
    def visitForInitExpression(self, ctx:CustomHLSLParser.ForInitExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forConditionExpression.
    def visitForConditionExpression(self, ctx:CustomHLSLParser.ForConditionExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forIterationExpression.
    def visitForIterationExpression(self, ctx:CustomHLSLParser.ForIterationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forDeclaration.
    def visitForDeclaration(self, ctx:CustomHLSLParser.ForDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#forExpression.
    def visitForExpression(self, ctx:CustomHLSLParser.ForExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#jumpStatement.
    def visitJumpStatement(self, ctx:CustomHLSLParser.JumpStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#compilationUnit.
    def visitCompilationUnit(self, ctx:CustomHLSLParser.CompilationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#translationUnit.
    def visitTranslationUnit(self, ctx:CustomHLSLParser.TranslationUnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDefinition.
    def visitStructDefinition(self, ctx:CustomHLSLParser.StructDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDefinationList.
    def visitStructDefinationList(self, ctx:CustomHLSLParser.StructDefinationListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#structDefination.
    def visitStructDefination(self, ctx:CustomHLSLParser.StructDefinationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#externalDeclaration.
    def visitExternalDeclaration(self, ctx:CustomHLSLParser.ExternalDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#functionDefinition.
    def visitFunctionDefinition(self, ctx:CustomHLSLParser.FunctionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CustomHLSLParser#declarationList.
    def visitDeclarationList(self, ctx:CustomHLSLParser.DeclarationListContext):
        return self.visitChildren(ctx)



del CustomHLSLParser