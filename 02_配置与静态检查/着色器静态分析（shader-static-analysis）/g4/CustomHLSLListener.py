# Generated from CustomHLSL.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CustomHLSLParser import CustomHLSLParser
else:
    from CustomHLSLParser import CustomHLSLParser

# This class defines a complete listener for a parse tree produced by CustomHLSLParser.
class CustomHLSLListener(ParseTreeListener):

    # Enter a parse tree produced by CustomHLSLParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:CustomHLSLParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:CustomHLSLParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#genericSelection.
    def enterGenericSelection(self, ctx:CustomHLSLParser.GenericSelectionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#genericSelection.
    def exitGenericSelection(self, ctx:CustomHLSLParser.GenericSelectionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#genericAssocList.
    def enterGenericAssocList(self, ctx:CustomHLSLParser.GenericAssocListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#genericAssocList.
    def exitGenericAssocList(self, ctx:CustomHLSLParser.GenericAssocListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#genericAssociation.
    def enterGenericAssociation(self, ctx:CustomHLSLParser.GenericAssociationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#genericAssociation.
    def exitGenericAssociation(self, ctx:CustomHLSLParser.GenericAssociationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#postfixExpression.
    def enterPostfixExpression(self, ctx:CustomHLSLParser.PostfixExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#postfixExpression.
    def exitPostfixExpression(self, ctx:CustomHLSLParser.PostfixExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#argumentExpressionList.
    def enterArgumentExpressionList(self, ctx:CustomHLSLParser.ArgumentExpressionListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#argumentExpressionList.
    def exitArgumentExpressionList(self, ctx:CustomHLSLParser.ArgumentExpressionListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#unaryExpression.
    def enterUnaryExpression(self, ctx:CustomHLSLParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#unaryExpression.
    def exitUnaryExpression(self, ctx:CustomHLSLParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#unaryOperator.
    def enterUnaryOperator(self, ctx:CustomHLSLParser.UnaryOperatorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#unaryOperator.
    def exitUnaryOperator(self, ctx:CustomHLSLParser.UnaryOperatorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#castExpression.
    def enterCastExpression(self, ctx:CustomHLSLParser.CastExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#castExpression.
    def exitCastExpression(self, ctx:CustomHLSLParser.CastExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:CustomHLSLParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:CustomHLSLParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:CustomHLSLParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:CustomHLSLParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#shiftExpression.
    def enterShiftExpression(self, ctx:CustomHLSLParser.ShiftExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#shiftExpression.
    def exitShiftExpression(self, ctx:CustomHLSLParser.ShiftExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#relationalExpression.
    def enterRelationalExpression(self, ctx:CustomHLSLParser.RelationalExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#relationalExpression.
    def exitRelationalExpression(self, ctx:CustomHLSLParser.RelationalExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#equalityExpression.
    def enterEqualityExpression(self, ctx:CustomHLSLParser.EqualityExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#equalityExpression.
    def exitEqualityExpression(self, ctx:CustomHLSLParser.EqualityExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#andExpression.
    def enterAndExpression(self, ctx:CustomHLSLParser.AndExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#andExpression.
    def exitAndExpression(self, ctx:CustomHLSLParser.AndExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#exclusiveOrExpression.
    def enterExclusiveOrExpression(self, ctx:CustomHLSLParser.ExclusiveOrExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#exclusiveOrExpression.
    def exitExclusiveOrExpression(self, ctx:CustomHLSLParser.ExclusiveOrExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#inclusiveOrExpression.
    def enterInclusiveOrExpression(self, ctx:CustomHLSLParser.InclusiveOrExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#inclusiveOrExpression.
    def exitInclusiveOrExpression(self, ctx:CustomHLSLParser.InclusiveOrExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#logicalAndExpression.
    def enterLogicalAndExpression(self, ctx:CustomHLSLParser.LogicalAndExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#logicalAndExpression.
    def exitLogicalAndExpression(self, ctx:CustomHLSLParser.LogicalAndExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#logicalOrExpression.
    def enterLogicalOrExpression(self, ctx:CustomHLSLParser.LogicalOrExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#logicalOrExpression.
    def exitLogicalOrExpression(self, ctx:CustomHLSLParser.LogicalOrExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#conditionalExpression.
    def enterConditionalExpression(self, ctx:CustomHLSLParser.ConditionalExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#conditionalExpression.
    def exitConditionalExpression(self, ctx:CustomHLSLParser.ConditionalExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#assignmentExpression.
    def enterAssignmentExpression(self, ctx:CustomHLSLParser.AssignmentExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#assignmentExpression.
    def exitAssignmentExpression(self, ctx:CustomHLSLParser.AssignmentExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#assignmentOperator.
    def enterAssignmentOperator(self, ctx:CustomHLSLParser.AssignmentOperatorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#assignmentOperator.
    def exitAssignmentOperator(self, ctx:CustomHLSLParser.AssignmentOperatorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#expression.
    def enterExpression(self, ctx:CustomHLSLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#expression.
    def exitExpression(self, ctx:CustomHLSLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#constantExpression.
    def enterConstantExpression(self, ctx:CustomHLSLParser.ConstantExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#constantExpression.
    def exitConstantExpression(self, ctx:CustomHLSLParser.ConstantExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#declaration.
    def enterDeclaration(self, ctx:CustomHLSLParser.DeclarationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#declaration.
    def exitDeclaration(self, ctx:CustomHLSLParser.DeclarationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#declarationSpecifiers.
    def enterDeclarationSpecifiers(self, ctx:CustomHLSLParser.DeclarationSpecifiersContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#declarationSpecifiers.
    def exitDeclarationSpecifiers(self, ctx:CustomHLSLParser.DeclarationSpecifiersContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#declarationSpecifiers2.
    def enterDeclarationSpecifiers2(self, ctx:CustomHLSLParser.DeclarationSpecifiers2Context):
        pass

    # Exit a parse tree produced by CustomHLSLParser#declarationSpecifiers2.
    def exitDeclarationSpecifiers2(self, ctx:CustomHLSLParser.DeclarationSpecifiers2Context):
        pass


    # Enter a parse tree produced by CustomHLSLParser#declarationSpecifier.
    def enterDeclarationSpecifier(self, ctx:CustomHLSLParser.DeclarationSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#declarationSpecifier.
    def exitDeclarationSpecifier(self, ctx:CustomHLSLParser.DeclarationSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#initDeclaratorList.
    def enterInitDeclaratorList(self, ctx:CustomHLSLParser.InitDeclaratorListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#initDeclaratorList.
    def exitInitDeclaratorList(self, ctx:CustomHLSLParser.InitDeclaratorListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#initDeclarator.
    def enterInitDeclarator(self, ctx:CustomHLSLParser.InitDeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#initDeclarator.
    def exitInitDeclarator(self, ctx:CustomHLSLParser.InitDeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forInitDeclaratorList.
    def enterForInitDeclaratorList(self, ctx:CustomHLSLParser.ForInitDeclaratorListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forInitDeclaratorList.
    def exitForInitDeclaratorList(self, ctx:CustomHLSLParser.ForInitDeclaratorListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forInitDeclarator.
    def enterForInitDeclarator(self, ctx:CustomHLSLParser.ForInitDeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forInitDeclarator.
    def exitForInitDeclarator(self, ctx:CustomHLSLParser.ForInitDeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#storageClassSpecifier.
    def enterStorageClassSpecifier(self, ctx:CustomHLSLParser.StorageClassSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#storageClassSpecifier.
    def exitStorageClassSpecifier(self, ctx:CustomHLSLParser.StorageClassSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#typeSpecifier.
    def enterTypeSpecifier(self, ctx:CustomHLSLParser.TypeSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#typeSpecifier.
    def exitTypeSpecifier(self, ctx:CustomHLSLParser.TypeSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structOrUnionSpecifier.
    def enterStructOrUnionSpecifier(self, ctx:CustomHLSLParser.StructOrUnionSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structOrUnionSpecifier.
    def exitStructOrUnionSpecifier(self, ctx:CustomHLSLParser.StructOrUnionSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structOrUnion.
    def enterStructOrUnion(self, ctx:CustomHLSLParser.StructOrUnionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structOrUnion.
    def exitStructOrUnion(self, ctx:CustomHLSLParser.StructOrUnionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDeclarationList.
    def enterStructDeclarationList(self, ctx:CustomHLSLParser.StructDeclarationListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDeclarationList.
    def exitStructDeclarationList(self, ctx:CustomHLSLParser.StructDeclarationListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDeclaration.
    def enterStructDeclaration(self, ctx:CustomHLSLParser.StructDeclarationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDeclaration.
    def exitStructDeclaration(self, ctx:CustomHLSLParser.StructDeclarationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#specifierQualifierList.
    def enterSpecifierQualifierList(self, ctx:CustomHLSLParser.SpecifierQualifierListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#specifierQualifierList.
    def exitSpecifierQualifierList(self, ctx:CustomHLSLParser.SpecifierQualifierListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDeclaratorList.
    def enterStructDeclaratorList(self, ctx:CustomHLSLParser.StructDeclaratorListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDeclaratorList.
    def exitStructDeclaratorList(self, ctx:CustomHLSLParser.StructDeclaratorListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDeclarator.
    def enterStructDeclarator(self, ctx:CustomHLSLParser.StructDeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDeclarator.
    def exitStructDeclarator(self, ctx:CustomHLSLParser.StructDeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#enumSpecifier.
    def enterEnumSpecifier(self, ctx:CustomHLSLParser.EnumSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#enumSpecifier.
    def exitEnumSpecifier(self, ctx:CustomHLSLParser.EnumSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#enumeratorList.
    def enterEnumeratorList(self, ctx:CustomHLSLParser.EnumeratorListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#enumeratorList.
    def exitEnumeratorList(self, ctx:CustomHLSLParser.EnumeratorListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#enumerator.
    def enterEnumerator(self, ctx:CustomHLSLParser.EnumeratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#enumerator.
    def exitEnumerator(self, ctx:CustomHLSLParser.EnumeratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#enumerationConstant.
    def enterEnumerationConstant(self, ctx:CustomHLSLParser.EnumerationConstantContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#enumerationConstant.
    def exitEnumerationConstant(self, ctx:CustomHLSLParser.EnumerationConstantContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#atomicTypeSpecifier.
    def enterAtomicTypeSpecifier(self, ctx:CustomHLSLParser.AtomicTypeSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#atomicTypeSpecifier.
    def exitAtomicTypeSpecifier(self, ctx:CustomHLSLParser.AtomicTypeSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#typeQualifier.
    def enterTypeQualifier(self, ctx:CustomHLSLParser.TypeQualifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#typeQualifier.
    def exitTypeQualifier(self, ctx:CustomHLSLParser.TypeQualifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#functionSpecifier.
    def enterFunctionSpecifier(self, ctx:CustomHLSLParser.FunctionSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#functionSpecifier.
    def exitFunctionSpecifier(self, ctx:CustomHLSLParser.FunctionSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#alignmentSpecifier.
    def enterAlignmentSpecifier(self, ctx:CustomHLSLParser.AlignmentSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#alignmentSpecifier.
    def exitAlignmentSpecifier(self, ctx:CustomHLSLParser.AlignmentSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#declarator.
    def enterDeclarator(self, ctx:CustomHLSLParser.DeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#declarator.
    def exitDeclarator(self, ctx:CustomHLSLParser.DeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#directDeclarator.
    def enterDirectDeclarator(self, ctx:CustomHLSLParser.DirectDeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#directDeclarator.
    def exitDirectDeclarator(self, ctx:CustomHLSLParser.DirectDeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#vcSpecificModifer.
    def enterVcSpecificModifer(self, ctx:CustomHLSLParser.VcSpecificModiferContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#vcSpecificModifer.
    def exitVcSpecificModifer(self, ctx:CustomHLSLParser.VcSpecificModiferContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#gccDeclaratorExtension.
    def enterGccDeclaratorExtension(self, ctx:CustomHLSLParser.GccDeclaratorExtensionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#gccDeclaratorExtension.
    def exitGccDeclaratorExtension(self, ctx:CustomHLSLParser.GccDeclaratorExtensionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#gccAttributeSpecifier.
    def enterGccAttributeSpecifier(self, ctx:CustomHLSLParser.GccAttributeSpecifierContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#gccAttributeSpecifier.
    def exitGccAttributeSpecifier(self, ctx:CustomHLSLParser.GccAttributeSpecifierContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#gccAttributeList.
    def enterGccAttributeList(self, ctx:CustomHLSLParser.GccAttributeListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#gccAttributeList.
    def exitGccAttributeList(self, ctx:CustomHLSLParser.GccAttributeListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#gccAttribute.
    def enterGccAttribute(self, ctx:CustomHLSLParser.GccAttributeContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#gccAttribute.
    def exitGccAttribute(self, ctx:CustomHLSLParser.GccAttributeContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#nestedParenthesesBlock.
    def enterNestedParenthesesBlock(self, ctx:CustomHLSLParser.NestedParenthesesBlockContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#nestedParenthesesBlock.
    def exitNestedParenthesesBlock(self, ctx:CustomHLSLParser.NestedParenthesesBlockContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#pointer.
    def enterPointer(self, ctx:CustomHLSLParser.PointerContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#pointer.
    def exitPointer(self, ctx:CustomHLSLParser.PointerContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#typeQualifierList.
    def enterTypeQualifierList(self, ctx:CustomHLSLParser.TypeQualifierListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#typeQualifierList.
    def exitTypeQualifierList(self, ctx:CustomHLSLParser.TypeQualifierListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#parameterTypeList.
    def enterParameterTypeList(self, ctx:CustomHLSLParser.ParameterTypeListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#parameterTypeList.
    def exitParameterTypeList(self, ctx:CustomHLSLParser.ParameterTypeListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#parameterList.
    def enterParameterList(self, ctx:CustomHLSLParser.ParameterListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#parameterList.
    def exitParameterList(self, ctx:CustomHLSLParser.ParameterListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#parameterDeclaration.
    def enterParameterDeclaration(self, ctx:CustomHLSLParser.ParameterDeclarationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#parameterDeclaration.
    def exitParameterDeclaration(self, ctx:CustomHLSLParser.ParameterDeclarationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#identifierList.
    def enterIdentifierList(self, ctx:CustomHLSLParser.IdentifierListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#identifierList.
    def exitIdentifierList(self, ctx:CustomHLSLParser.IdentifierListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#typeName.
    def enterTypeName(self, ctx:CustomHLSLParser.TypeNameContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#typeName.
    def exitTypeName(self, ctx:CustomHLSLParser.TypeNameContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#abstractDeclarator.
    def enterAbstractDeclarator(self, ctx:CustomHLSLParser.AbstractDeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#abstractDeclarator.
    def exitAbstractDeclarator(self, ctx:CustomHLSLParser.AbstractDeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#directAbstractDeclarator.
    def enterDirectAbstractDeclarator(self, ctx:CustomHLSLParser.DirectAbstractDeclaratorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#directAbstractDeclarator.
    def exitDirectAbstractDeclarator(self, ctx:CustomHLSLParser.DirectAbstractDeclaratorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#typedefName.
    def enterTypedefName(self, ctx:CustomHLSLParser.TypedefNameContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#typedefName.
    def exitTypedefName(self, ctx:CustomHLSLParser.TypedefNameContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#initializer.
    def enterInitializer(self, ctx:CustomHLSLParser.InitializerContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#initializer.
    def exitInitializer(self, ctx:CustomHLSLParser.InitializerContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#initializerList.
    def enterInitializerList(self, ctx:CustomHLSLParser.InitializerListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#initializerList.
    def exitInitializerList(self, ctx:CustomHLSLParser.InitializerListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#designation.
    def enterDesignation(self, ctx:CustomHLSLParser.DesignationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#designation.
    def exitDesignation(self, ctx:CustomHLSLParser.DesignationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#designatorList.
    def enterDesignatorList(self, ctx:CustomHLSLParser.DesignatorListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#designatorList.
    def exitDesignatorList(self, ctx:CustomHLSLParser.DesignatorListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#designator.
    def enterDesignator(self, ctx:CustomHLSLParser.DesignatorContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#designator.
    def exitDesignator(self, ctx:CustomHLSLParser.DesignatorContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#staticAssertDeclaration.
    def enterStaticAssertDeclaration(self, ctx:CustomHLSLParser.StaticAssertDeclarationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#staticAssertDeclaration.
    def exitStaticAssertDeclaration(self, ctx:CustomHLSLParser.StaticAssertDeclarationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#statement.
    def enterStatement(self, ctx:CustomHLSLParser.StatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#statement.
    def exitStatement(self, ctx:CustomHLSLParser.StatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#labeledStatement.
    def enterLabeledStatement(self, ctx:CustomHLSLParser.LabeledStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#labeledStatement.
    def exitLabeledStatement(self, ctx:CustomHLSLParser.LabeledStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#compoundStatement.
    def enterCompoundStatement(self, ctx:CustomHLSLParser.CompoundStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#compoundStatement.
    def exitCompoundStatement(self, ctx:CustomHLSLParser.CompoundStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#blockItemList.
    def enterBlockItemList(self, ctx:CustomHLSLParser.BlockItemListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#blockItemList.
    def exitBlockItemList(self, ctx:CustomHLSLParser.BlockItemListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#blockItem.
    def enterBlockItem(self, ctx:CustomHLSLParser.BlockItemContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#blockItem.
    def exitBlockItem(self, ctx:CustomHLSLParser.BlockItemContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#expressionStatement.
    def enterExpressionStatement(self, ctx:CustomHLSLParser.ExpressionStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#expressionStatement.
    def exitExpressionStatement(self, ctx:CustomHLSLParser.ExpressionStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#selectionStatement.
    def enterSelectionStatement(self, ctx:CustomHLSLParser.SelectionStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#selectionStatement.
    def exitSelectionStatement(self, ctx:CustomHLSLParser.SelectionStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#iterationStatement.
    def enterIterationStatement(self, ctx:CustomHLSLParser.IterationStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#iterationStatement.
    def exitIterationStatement(self, ctx:CustomHLSLParser.IterationStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#whileIterationStatement.
    def enterWhileIterationStatement(self, ctx:CustomHLSLParser.WhileIterationStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#whileIterationStatement.
    def exitWhileIterationStatement(self, ctx:CustomHLSLParser.WhileIterationStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forIterationStatement.
    def enterForIterationStatement(self, ctx:CustomHLSLParser.ForIterationStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forIterationStatement.
    def exitForIterationStatement(self, ctx:CustomHLSLParser.ForIterationStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forStatement.
    def enterForStatement(self, ctx:CustomHLSLParser.ForStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forStatement.
    def exitForStatement(self, ctx:CustomHLSLParser.ForStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forCondition.
    def enterForCondition(self, ctx:CustomHLSLParser.ForConditionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forCondition.
    def exitForCondition(self, ctx:CustomHLSLParser.ForConditionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forInitExpression.
    def enterForInitExpression(self, ctx:CustomHLSLParser.ForInitExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forInitExpression.
    def exitForInitExpression(self, ctx:CustomHLSLParser.ForInitExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forConditionExpression.
    def enterForConditionExpression(self, ctx:CustomHLSLParser.ForConditionExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forConditionExpression.
    def exitForConditionExpression(self, ctx:CustomHLSLParser.ForConditionExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forIterationExpression.
    def enterForIterationExpression(self, ctx:CustomHLSLParser.ForIterationExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forIterationExpression.
    def exitForIterationExpression(self, ctx:CustomHLSLParser.ForIterationExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forDeclaration.
    def enterForDeclaration(self, ctx:CustomHLSLParser.ForDeclarationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forDeclaration.
    def exitForDeclaration(self, ctx:CustomHLSLParser.ForDeclarationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#forExpression.
    def enterForExpression(self, ctx:CustomHLSLParser.ForExpressionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#forExpression.
    def exitForExpression(self, ctx:CustomHLSLParser.ForExpressionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#jumpStatement.
    def enterJumpStatement(self, ctx:CustomHLSLParser.JumpStatementContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#jumpStatement.
    def exitJumpStatement(self, ctx:CustomHLSLParser.JumpStatementContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#compilationUnit.
    def enterCompilationUnit(self, ctx:CustomHLSLParser.CompilationUnitContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#compilationUnit.
    def exitCompilationUnit(self, ctx:CustomHLSLParser.CompilationUnitContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#translationUnit.
    def enterTranslationUnit(self, ctx:CustomHLSLParser.TranslationUnitContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#translationUnit.
    def exitTranslationUnit(self, ctx:CustomHLSLParser.TranslationUnitContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDefinition.
    def enterStructDefinition(self, ctx:CustomHLSLParser.StructDefinitionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDefinition.
    def exitStructDefinition(self, ctx:CustomHLSLParser.StructDefinitionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDefinationList.
    def enterStructDefinationList(self, ctx:CustomHLSLParser.StructDefinationListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDefinationList.
    def exitStructDefinationList(self, ctx:CustomHLSLParser.StructDefinationListContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#structDefination.
    def enterStructDefination(self, ctx:CustomHLSLParser.StructDefinationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#structDefination.
    def exitStructDefination(self, ctx:CustomHLSLParser.StructDefinationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#externalDeclaration.
    def enterExternalDeclaration(self, ctx:CustomHLSLParser.ExternalDeclarationContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#externalDeclaration.
    def exitExternalDeclaration(self, ctx:CustomHLSLParser.ExternalDeclarationContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#functionDefinition.
    def enterFunctionDefinition(self, ctx:CustomHLSLParser.FunctionDefinitionContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#functionDefinition.
    def exitFunctionDefinition(self, ctx:CustomHLSLParser.FunctionDefinitionContext):
        pass


    # Enter a parse tree produced by CustomHLSLParser#declarationList.
    def enterDeclarationList(self, ctx:CustomHLSLParser.DeclarationListContext):
        pass

    # Exit a parse tree produced by CustomHLSLParser#declarationList.
    def exitDeclarationList(self, ctx:CustomHLSLParser.DeclarationListContext):
        pass



del CustomHLSLParser