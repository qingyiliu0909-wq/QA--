#pragma once
#include "LuaFunctionalTest.h"
#include "Misc/AutomationTest.h"

DEFINE_EXPORTED_LATENT_AUTOMATION_COMMAND_THREE_PARAMETER(EMEDITOR_API, FCreateAndWaitFunctionalActorCommand, UWorld*, TestWorld, ALuaFunctionalTest*,
	TestActor,FLuaFunctionalTestCallInfo, LuaCallInfo);
