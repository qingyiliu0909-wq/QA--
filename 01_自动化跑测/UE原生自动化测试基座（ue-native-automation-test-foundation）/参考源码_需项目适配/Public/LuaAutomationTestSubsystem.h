// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "LuaEnvLocator.h"
#include "LuaAutomationTestSubsystem.generated.h"

namespace EAutomationTestType
{
enum Type
{
	UNIT = 0,
	FUNCTIONAL
};
}

/**
 * 
 */
UCLASS()
class EMEDITOR_API UTestLuaEnv : public UObject
{
	GENERATED_BODY()

public:
	UTestLuaEnv();
	
	void SetupEnvFunction_TestClass() const;

	static FString GetTestPath();

	bool RunTestFile(const FString& TestFilePath) const;

	bool RunTestFunc(const FString& TestFilePath, const FString& FuncName) const;

	void ForeachTestFile(const TFunction<void(const FString&, EAutomationTestType::Type)>& Func) const;

	FString GetMapPath();
protected:
	lua_State* GetState() const;
	
	UPROPERTY()
	ULuaEnvLocator* EnvLocator;
};



UCLASS()
class EMEDITOR_API ULuaAutomationTestSubsystem : public UEditorSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	virtual void Deinitialize() override;

	UTestLuaEnv* GetTestLuaEnv();

protected:
	UPROPERTY()
	UTestLuaEnv* TestLuaEnv;
};

