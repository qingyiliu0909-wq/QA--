#include "Test/LuaTestLatentCommand.h"
#include "Test/LuaFunctionalTest.h"

bool FCreateAndWaitFunctionalActorCommand::Update()
{
	if (!IsValid(TestActor))
	{
		UClass* Class = LoadClass<ALuaFunctionalTest>(TestWorld,
			TEXT("Blueprint'/Game/BluePrints/Common/Test/BP_FunctionalTestActor.BP_FunctionalTestActor_C'"));

		if(!IsValid(Class)){
			UE_LOG(LogTemp, Error, TEXT("Failed to load class"));
			return true;
		}
		
		FActorSpawnParameters SpawnParameters;
		SpawnParameters.Name = LUA_TEST_ACTOR_NAME;
		TestActor = TestWorld->SpawnActor<ALuaFunctionalTest>(Class,SpawnParameters);
		return false;
	}
	if (!TestActor->IsActorInitialized())
	{
		return false;
	}
	TestActor->SetLuaFunctionalTestCallInfo(LuaCallInfo);
	return true;
}
