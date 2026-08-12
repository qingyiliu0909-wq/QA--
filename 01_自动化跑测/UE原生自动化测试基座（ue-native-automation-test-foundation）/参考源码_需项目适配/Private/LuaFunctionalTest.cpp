#include "Test/LuaFunctionalTest.h"

ALuaFunctionalTest::ALuaFunctionalTest(const FObjectInitializer& ObjectInitializer): AFunctionalTest(ObjectInitializer) {}

void ALuaFunctionalTest::SetLuaFunctionalTestCallInfo(const FLuaFunctionalTestCallInfo& InCallInfo)
{
	CallInfo.LuaRequirePath = InCallInfo.LuaRequirePath;
	CallInfo.FunctionName = InCallInfo.FunctionName;
}

FString ALuaFunctionalTest::GetCallClassPath() { return CallInfo.LuaRequirePath; }

FString ALuaFunctionalTest::GetCallFunctionName() { return CallInfo.FunctionName; }
