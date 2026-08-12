#include "Test/LuaTestBase.h"
#include "FunctionalTestBase.h"
#include "FunctionalTestingHelper.h"
#include "FunctionalTestingModule.h"
#include "Test/LuaTestLatentCommand.h"
#include "Kismet/KismetStringLibrary.h"
#include "Test/LuaAutomationTestSubsystem.h"
#include "Misc/AutomationTest.h"
#include "Tests/AutomationCommon.h"

bool FLuaUnitTester::RunTest(const FLuaTestMetaInfo& MetaInfo, FLuaTestBase* TestBase)
{
	auto TestLuaEnv = GEditor->GetEditorSubsystem<ULuaAutomationTestSubsystem>()->GetTestLuaEnv();
	return TestLuaEnv->RunTestFunc(MetaInfo.TestFilePath, MetaInfo.FuncName);
}

bool FLuaFunctionalTester::RunTest(const FLuaTestMetaInfo& MetaInfo, FLuaTestBase* TestBase)
{
	IFunctionalTestingModule::Get().MarkPendingActivation();
	TestBase->SetLogErrorAndWarningHandlingToDefault();

	if (!TestBase->GetOrCreateTestWorld(MetaInfo.MapPath))
	{
		UE_LOG(LogFunctionalTest, Error, TEXT("Failed to start the %s map (possibly due to BP compilation issues)"), *MetaInfo.MapPath);
		return true;
	}
	const FString& LuaRequirePath = TEXT("Test.")+
			MetaInfo.RelativePath.Replace(
				TEXT("/"), TEXT(".")
			);
	ADD_LATENT_AUTOMATION_COMMAND(
		FCreateAndWaitFunctionalActorCommand(FClientFunctionalTestingMapsBase::GetAnyGameWorld(),nullptr,FLuaFunctionalTestCallInfo(LuaRequirePath, MetaInfo.FuncName)));
	ADD_LATENT_AUTOMATION_COMMAND(FStartFTestOnMap(LUA_TEST_ACTOR_NAME))
	return true;
}


FLuaTestBase::FLuaTestBase(const FString& InName, const bool bInComplexTask): FClientFunctionalTestingMapsBase(InName, bInComplexTask) {}

FString FLuaTestBase::GetTestOpenCommand(const FString& Parameters) const
{
	FLuaTestMetaInfo MetaInfo;
	ParseTestInfo(Parameters, MetaInfo);
	if (MetaInfo.TestType == EAutomationTestType::Type::UNIT) { return FAutomationTestBase::GetTestOpenCommand(Parameters); }
	else { return FString::Printf(TEXT("Automate.OpenMapAndFocusActor %s %s"), *MetaInfo.MapPath, *MetaInfo.FuncName); }
}

FString FLuaTestBase::GetTestAssetPath(const FString& Parameters) const
{
	FLuaTestMetaInfo MetaInfo;
	ParseTestInfo(Parameters, MetaInfo);
	if (MetaInfo.TestType == EAutomationTestType::Type::UNIT) { return FAutomationTestBase::GetTestAssetPath(Parameters); }
	else { return MetaInfo.MapPath; }
}

void FLuaTestBase::CreateBeautifiedNameAndTestCommand(EAutomationTestType::Type TestType, const FString& FuncName, const FString& MapPath,
	UTestLuaEnv* TestLuaEnv, const FString& TestFilePath, FString& OutBeautifiedName, FString& OutTestCommand)
{
	FString RelativePath = TestFilePath.RightChop(TestLuaEnv->GetTestPath().Len() + 1);
	RelativePath.Split(TEXT("."), &RelativePath, nullptr);

	FString CommandPrefix;
	if (TestType == EAutomationTestType::Type::UNIT) { CommandPrefix = TEXT("U"); }
	else { CommandPrefix = TEXT("F"); }

	OutBeautifiedName = FString::Printf(TEXT("%s.%s"), *(RelativePath.Replace(TEXT("/"),TEXT("."))), *FuncName);
	OutTestCommand = FString::Printf(TEXT("%s-%s-%s-%s-%s"), *CommandPrefix, *TestFilePath, *RelativePath, *FuncName,
		*MapPath);
}

void FLuaTestBase::GetTestsInFile(TArray<FString>& BeautifiedNames, TArray<FString>& TestCommands, UTestLuaEnv* TestLuaEnv,
	const FString& TestFilePath) const
{
	if (TestLuaEnv->RunTestFile(TestFilePath))
	{
		FString MapPath = TestLuaEnv->GetMapPath();
		TestLuaEnv->ForeachTestFile([this,&BeautifiedNames, &TestCommands, &TestFilePath, &TestLuaEnv, &MapPath](const FString& FuncName,
			EAutomationTestType::Type TestType)
			{
				FString BeautifiedName, TestCommand;
				CreateBeautifiedNameAndTestCommand(TestType, FuncName, MapPath, TestLuaEnv, TestFilePath, BeautifiedName, TestCommand);
				BeautifiedNames.Add(BeautifiedName);
				TestCommands.Add(TestCommand);
			});
	}
}

void FLuaTestBase::GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const
{
	const auto TestLuaEnv = GEditor->GetEditorSubsystem<ULuaAutomationTestSubsystem>()->GetTestLuaEnv();

	TArray<FString> AllTestFilePaths;
	IFileManager::Get().FindFilesRecursive(AllTestFilePaths, *(TestLuaEnv->GetTestPath()),
		TEXT("*.lua"), true, false);

	for (const FString& TestFilePath : AllTestFilePaths) { GetTestsInFile(OutBeautifiedNames, OutTestCommands, TestLuaEnv, TestFilePath); }
}

bool FLuaTestBase::RunTest(const FString& Parameters)
{
	FLuaTestMetaInfo MetaInfo;
	ParseTestInfo(Parameters, MetaInfo);
	return FLuaTesterFactory::Create(MetaInfo.TestType)->RunTest(MetaInfo, this);
}

bool FLuaTestBase::GetOrCreateTestWorld(const FString& MapPackageName) const
{
	UWorld* TestWorld = GetAnyGameWorld();

	if (TestWorld && TestWorld->GetMapName() == MapPackageName && !bForceOpenNewMap) { return true; }
	else if (MapPackageName == TEXT("")) { return false; }
	else { return AutomationOpenMap(MapPackageName, bForceOpenNewMap); }
}

void FLuaTestBase::ParseTestInfo(const FString& CommandStr, FLuaTestMetaInfo& MetaInfo)
{
	TArray<FString> StrArr = UKismetStringLibrary::ParseIntoArray(CommandStr,TEXT("-"));
	checkf(StrArr.Num() >= 4, TEXT("Invalid command str format: %s"), *CommandStr);
	if (StrArr[0] == TEXT("F")) { MetaInfo.TestType = EAutomationTestType::Type::FUNCTIONAL; }
	else
		if (StrArr[0] == TEXT("U")) { MetaInfo.TestType = EAutomationTestType::Type::UNIT; }
	MetaInfo.TestFilePath = StrArr[1];
	MetaInfo.RelativePath = StrArr[2];
	MetaInfo.FuncName = StrArr[3];
	MetaInfo.MapPath = StrArr.Num() == 5
	                   ? StrArr[4]
	                   : TEXT("");
}

IMPLEMENT_CUSTOM_COMPLEX_AUTOMATION_TEST(FLuaFunctionalTest, FLuaTestBase, "EMTest",
	(EAutomationTestFlags::ClientContext | EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter))

void FLuaFunctionalTest::GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const
{
	FLuaTestBase::GetTests(OutBeautifiedNames, OutTestCommands);
}

bool FLuaFunctionalTest::RunTest(const FString& Parameters) { return FLuaTestBase::RunTest(Parameters); }
