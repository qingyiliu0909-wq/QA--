local Test = TestClass("/Game/Maps/TestMap")

function Test:UTest_Example()
    -- 不需要加载地图的脚本单元测试。
    assert(1 + 1 == 2)
end

function Test:FTest_Example()
    -- 需要加载地图的功能测试。
    -- 由项目自己的 Functional Test Actor 读取此函数并驱动执行。
end

return Test
