using UnrealBuildTool;

public class ProjectAutomationTests : ModuleRules
{
    public ProjectAutomationTests(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PrivateDependencyModuleNames.AddRange(new[]
        {
            "Core", "CoreUObject", "Engine", "UnrealEd", "FunctionalTesting"
        });
    }
}
