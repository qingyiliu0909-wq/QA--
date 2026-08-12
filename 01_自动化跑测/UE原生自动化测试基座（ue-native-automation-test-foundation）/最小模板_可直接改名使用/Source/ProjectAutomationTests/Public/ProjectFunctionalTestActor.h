#pragma once

#include "FunctionalTest.h"
#include "ProjectFunctionalTestActor.generated.h"

UCLASS(Blueprintable)
class PROJECTAUTOMATIONTESTS_API AProjectFunctionalTestActor : public AFunctionalTest
{
    GENERATED_BODY()

public:
    virtual void StartTest() override;
};
