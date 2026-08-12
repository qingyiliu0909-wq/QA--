# -*- coding: utf-8 -*-
"""功能目录路径约定(改布局只改这一处)。

新结构(按角色分,给人+给脚本共用一棵树):
<功能目录>/                          = Docs/CrossCheck/系统功能/<功能>/
  feature.json
  策划/
    交互文档/    原始交互稿(pdf/feishu_images/manifest)
    系统文档/    原始系统稿(各子目录 system1/system2/.../md)
    蓝图文档/    原始蓝图/资产说明稿
    文档冲突对比/ report.json + 冲突报告.html   (模块A 产出,策划看)
  程序/
    工单/        impl_spec.json + 工单.html + <功能>_开发文档.md (模块B 产出,程序/AI看)
    服务器数据/  服务器侧配置/协议参考(可选,程序自己按迭代维护;开工单/迭代工单如果这个目录存在内容,必须一并读取纳入)
  _内部数据/     机器专用,不供人翻:ir/(ir_*.json)、strips_*/(切条图)、
                 wbp_tree.json、抽取用的文字层 md
"""
import os


def ir(d, name=""):
    p = os.path.join(d, "_内部数据", "ir")
    return os.path.join(p, name) if name else p


def internal(d, name=""):
    p = os.path.join(d, "_内部数据")
    return os.path.join(p, name) if name else p


DOC_DIR_NAME = {"interaction": "交互文档", "system": "系统文档", "blueprint": "蓝图文档"}


def doc_dir(d, kind, name=""):
    """kind: interaction | system | blueprint -> 策划/<对应类型>文档/[name]"""
    p = os.path.join(d, "策划", DOC_DIR_NAME[kind])
    return os.path.join(p, name) if name else p


def report_dir(d, name=""):
    """模块A 产出:冲突报告,策划看。"""
    p = os.path.join(d, "策划", "文档冲突对比")
    return os.path.join(p, name) if name else p


def workorder_dir(d, name=""):
    """模块B 产出:AI 开发工单,程序/AI看。"""
    p = os.path.join(d, "程序", "工单")
    return os.path.join(p, name) if name else p


def server_dir(d, name=""):
    """程序自己维护的服务器侧配置/协议参考(可选,随迭代更新)。
    开工单/迭代工单时,如果这个目录下有内容,必须一并读取纳入,不能只看策划三份文档。"""
    p = os.path.join(d, "程序", "服务器数据")
    return os.path.join(p, name) if name else p


def ensure_all(d):
    for p in (ir(d), internal(d), doc_dir(d, "interaction"), doc_dir(d, "system"),
              doc_dir(d, "blueprint"), report_dir(d), workorder_dir(d)):
        os.makedirs(p, exist_ok=True)
    return d


def find_root(start_path):
    """从任意文件/目录往上找,直到看见 feature.json 所在目录(功能根目录)。"""
    d = os.path.dirname(os.path.abspath(start_path))
    for _ in range(6):
        if os.path.exists(os.path.join(d, "feature.json")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.dirname(os.path.abspath(start_path))


# --- 兼容旧代码里 fpaths.out()/fpaths.inp() 的调用点(逐步淘汰用) ---
def out(d, name=""):
    """旧概念的 outputs 已拆成 report_dir/workorder_dir;按文件名归类。"""
    if name in ("report.json", "冲突报告.html") or name == "":
        return report_dir(d, name)
    return workorder_dir(d, name)


def inp(d, name=""):
    """旧概念的 inputs 已拆成 doc_dir(按类型)/internal;默认给内部数据。"""
    return internal(d, name)
