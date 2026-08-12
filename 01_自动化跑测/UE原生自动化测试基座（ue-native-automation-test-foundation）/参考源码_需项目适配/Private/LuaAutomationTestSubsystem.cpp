// Fill out your copyright notice in the Description page of Project Settings.

#include "Test/LuaAutomationTestSubsystem.h"

#include "LuaEnvLocator.h"

UTestLuaEnv::UTestLuaEnv()
{
	if (IsRunningCommandlet())
	{
		return;
	}
	EnvLocator = NewObject<ULuaEnvLocator>(GetTransientPackage(), ULuaEnvLocator::StaticClass());
}

void UTestLuaEnv::SetupEnvFunction_TestClass() const
{
	luaL_dostring(GetState(), R"(
                    pcall(function() _G.TestClass = 
					function(MapPath) 
						local Class = {} 
						Class.__index = Class 
						Class.__map_path = MapPath or ""
						Class.New = function() 
							local o = {} 
							setmetatable(o,Class) 
							return o 
						end 
						return Class 
					end end)
                )");
}

FString UTestLuaEnv::GetTestPath() { return FPaths::Combine(FPaths::ProjectContentDir(), TEXT("TestScript/Test")); }

bool UTestLuaEnv::RunTestFile(const FString& TestFilePath) const
{
	auto L = GetState();
	luaL_dofile(L, TCHAR_TO_UTF8(*TestFilePath));
	if (LUA_TTABLE != lua_type(L, -1))
	{
		UE_LOG(LogTemp, Warning, TEXT("TestFile need to return TestClass %s"), *TestFilePath);
		lua_settop(L, 0);
		return false;
	}
	return true;
}

bool UTestLuaEnv::RunTestFunc(const FString& TestFilePath, const FString& FuncName) const
{
	auto L = GetState();
	luaL_dofile(L, TCHAR_TO_UTF8(*TestFilePath));
	if (LUA_TTABLE != lua_type(L, -1))
	{
		lua_settop(L, 0);
		return false;
	}
	lua_getfield(L, -1, TCHAR_TO_UTF8(*FuncName));
	if (LUA_TFUNCTION != lua_type(L, -1))
	{
		lua_settop(L, 0);
		return false;
	}
	if (lua_pcall(L, 0, 0, 0))
	{
		UE_LOG(LogTemp, Error, TEXT("RunTestFunc %s.%s failed: %s"), *TestFilePath, *FuncName, UTF8_TO_TCHAR(lua_tostring(L, -1)));
		lua_settop(L, 0);
		return false;
	}
	lua_settop(L, 0);
	return true;
}

void UTestLuaEnv::ForeachTestFile(const TFunction<void(const FString&, EAutomationTestType::Type)>& Func) const
{
	auto L = GetState();
	lua_pushnil(L);
	while (lua_next(L, -2))
	{
		if (LUA_TFUNCTION == lua_type(L, -1))
		{
			FString FuncName = lua_tostring(L, -2);
			if (FuncName.StartsWith(TEXT("UTest_"))) { Func(FuncName, EAutomationTestType::Type::UNIT); }
			else
				if (FuncName.StartsWith(TEXT("FTest_"))) { Func(FuncName, EAutomationTestType::Type::FUNCTIONAL); }
		}
		lua_pop(L, 1);
	}
}

FString UTestLuaEnv::GetMapPath()
{
	auto L = GetState();
	lua_getfield(L, -1, TCHAR_TO_UTF8(TEXT("__map_path")));
	if (LUA_TSTRING != lua_type(L, -1))
	{
		lua_pop(L, 1);
		return "";
	}
	FString MapPath = lua_tostring(L, -1);
	lua_pop(L, 1);
	return MapPath;
}

lua_State* UTestLuaEnv::GetState() const { return EnvLocator->Locate(nullptr)->GetMainState(); }

void ULuaAutomationTestSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	if (IsRunningCommandlet())
	{
		return;
	}
	TestLuaEnv = NewObject<UTestLuaEnv>(GetTransientPackage(), UTestLuaEnv::StaticClass());
	TestLuaEnv->SetupEnvFunction_TestClass();
}

void ULuaAutomationTestSubsystem::Deinitialize() { Super::Deinitialize(); }

UTestLuaEnv* ULuaAutomationTestSubsystem::GetTestLuaEnv() { return TestLuaEnv; }
