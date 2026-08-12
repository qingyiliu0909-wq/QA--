#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FProjectSmokeAutomationTest,
    "Project.Smoke.Basic",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FProjectSmokeAutomationTest::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("The automation module is loaded"), true);
    return true;
}
