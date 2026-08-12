#pragma once
#include "FunctionalTest.h"
#include "LuaFunctionalTest.generated.h"
#define LUA_TEST_ACTOR_NAME TEXT("LUA_TEST_ACTOR_NAME")

struct FLuaFunctionalTestCallInfo
{
	FString LuaRequirePath;
	FString FunctionName;
	FLuaFunctionalTestCallInfo(): LuaRequirePath(TEXT("")), FunctionName(TEXT("")) {}

	// FLuaFunctionalTestCallInfo(const FLuaFunctionalTestCallInfo& OtherCallInfo): LuaRequirePath(OtherCallInfo.LuaRequirePath),
	// 	FunctionName(OtherCallInfo.FunctionName) {}

	FLuaFunctionalTestCallInfo(const FString& InLuaRequirePath, const FString& InFunctionName): LuaRequirePath(InLuaRequirePath), FunctionName(InFunctionName) {}
};

UCLASS(hidecategories=( Actor, Input, Rendering ), Blueprintable, BlueprintType)
class ALuaFunctionalTest : public AFunctionalTest
{
	GENERATED_BODY()

public:
	ALuaFunctionalTest(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());

	void SetLuaFunctionalTestCallInfo(const FLuaFunctionalTestCallInfo& InCallInfo);

	UFUNCTION(BlueprintCallable)
	FString GetCallClassPath();

	UFUNCTION(BlueprintCallable)
	FString GetCallFunctionName();

protected:
	FLuaFunctionalTestCallInfo CallInfo;
};
