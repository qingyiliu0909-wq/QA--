#pragma once
#include "Test/LuaAutomationTestSubsystem.h"
#include "Test/ClientFuncTestPerforming.h"

class FLuaTestBase;

struct FLuaTestMetaInfo
{
	FString TestFilePath, RelativePath, FuncName, MapPath;
	EAutomationTestType::Type TestType;
};

class FLuaTesterInterface
{
public:
	virtual ~FLuaTesterInterface() = default;

	virtual FString GetCommandPrefix() const = 0;

	virtual bool RunTest(const FLuaTestMetaInfo& MetaInfo, FLuaTestBase* TestBase) = 0;
};

class FLuaUnitTester : public FLuaTesterInterface
{
public:
	virtual FString GetCommandPrefix() const override { return TEXT("U"); }

	virtual bool RunTest(const FLuaTestMetaInfo& MetaInfo, FLuaTestBase* TestBase) override;
};

class FLuaFunctionalTester : public FLuaTesterInterface
{
public:
	virtual FString GetCommandPrefix() const override { return TEXT("F"); }

	virtual bool RunTest(const FLuaTestMetaInfo& MetaInfo, FLuaTestBase* TestBase) override;
};

class FLuaTesterFactory
{
public:
	static TSharedPtr<FLuaTesterInterface> Create(const EAutomationTestType::Type Type)
	{
		switch (Type)
		{
			case EAutomationTestType::Type::UNIT: return MakeShared<FLuaUnitTester>();
			case EAutomationTestType::Type::FUNCTIONAL: return MakeShared<FLuaFunctionalTester>();
			default:
				UE_LOG(LogFunctionalTest, Error, TEXT("Undefined Test type!"));
				break;
		}
		return {};
	}
};

class FLuaTestBase : public FClientFunctionalTestingMapsBase
{
public:
	FLuaTestBase(const FString& InName, const bool bInComplexTask);

	virtual FString GetTestOpenCommand(const FString& Parameters) const override;

	virtual FString GetTestAssetPath(const FString& Parameters) const override;

protected:
	virtual bool RunTest(const FString& Parameters) override;

	virtual void GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const override;

	static void CreateBeautifiedNameAndTestCommand(EAutomationTestType::Type TestType, const FString& FuncName, const FString& MapPath,
		UTestLuaEnv* TestLuaEnv, const FString& TestFilePath, FString& OutBeautifiedName, FString& OutTestCommand);

	void GetTestsInFile(TArray<FString>& BeautifiedNames, TArray<FString>& TestCommands, UTestLuaEnv* TestLuaEnv, const FString&
		TestFilePath) const;

	bool GetOrCreateTestWorld(const FString& MapPackageName) const;

	static void ParseTestInfo(const FString& CommandStr, FLuaTestMetaInfo& MetaInfo);

	friend FLuaFunctionalTester;
};
