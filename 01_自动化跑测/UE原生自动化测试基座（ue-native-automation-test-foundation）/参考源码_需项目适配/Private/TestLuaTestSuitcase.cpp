#include "Test/LuaAutomationTestSubsystem.h"
#include "Misc/AutomationTest.h"
#include "Misc/ScopeTempFile.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTestLuaUnitTestCollectFunctions, "EMEditor.TestSuitcase.Test Test LuaUnitTest Collect Functions",
	EAutomationTestFlags::EditorContext |
	EAutomationTestFlags::EngineFilter)

bool FTestLuaUnitTestCollectFunctions::RunTest(const FString& Parameters)
{
	FString LuaStr = TEXT("local Class = TestClass() function Class:UTest_Return1() return 1 end return Class");
	FString LuaPath = FPaths::ProjectContentDir() + TEXT("Script/Test/TestTemp.lua");
	{
		FScopeTempFile TempFile(LuaPath, LuaStr);
		auto TestLuaEnv = GEditor->GetEditorSubsystem<ULuaAutomationTestSubsystem>()->GetTestLuaEnv();

		UTEST_EQUAL(TEXT("RunTestFile need to return TestClass"), TestLuaEnv->RunTestFile(LuaPath), true);

		bool bHasTestFunc = false;
		TestLuaEnv->ForeachTestFile([this,&bHasTestFunc](const FString& FuncName, EAutomationTestType::Type)
		{
			bHasTestFunc = true;
			TestEqual(TEXT("Error function name"), FuncName,TEXT("UTest_Return1"));
		});

		UTEST_EQUAL(TEXT("Do not call test function"), bHasTestFunc, true);
		return true;
	}
}
