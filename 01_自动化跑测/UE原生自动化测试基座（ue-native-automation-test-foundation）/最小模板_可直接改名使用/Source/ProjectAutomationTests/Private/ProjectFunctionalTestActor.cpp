#include "ProjectFunctionalTestActor.h"

void AProjectFunctionalTestActor::StartTest()
{
    Super::StartTest();
    FinishTest(EFunctionalTestResult::Succeeded, TEXT("Replace this smoke assertion with project checks."));
}
