# -*- coding: utf-8 -*-
"""生成《云迹 yunji 项目归属说明》PDF，需本机安装 fpdf2：pip install fpdf2"""
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    import winreg
else:
    winreg = None  # type: ignore

try:
    from fpdf import FPDF
except ImportError:
    print("请先执行: pip install fpdf2", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Windows 常见中文字体（若不存在可改 simsun.ttc 或 msyhbd.ttc）
FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\msyh.ttf"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
]


def run_git(args: list[str]) -> str:
    r = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return (r.stdout or "").strip()


def pick_font() -> Path:
    for p in FONT_CANDIDATES:
        if p.is_file():
            return p
    raise SystemExit("未找到 Windows 中文字体（msyh/simsun 等），无法生成中文 PDF。")


def resolve_windows_desktop() -> Path:
    """读取注册表「桌面」实际路径（含重定向到 D: 等情况）。"""
    if winreg is None:
        return Path.home() / "Desktop"
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        ) as key:
            raw, _ = winreg.QueryValueEx(key, "Desktop")
            p = Path(str(raw))
            if p.is_dir():
                return p
    except OSError:
        pass
    home = Path.home()
    for sub in ("Desktop", "桌面"):
        cand = home / sub
        if cand.is_dir():
            return cand
    return home


class Doc(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font(self._font_family, size=9)
        self.set_text_color(100, 100, 100)
        w = self.w - self.l_margin - self.r_margin
        self.cell(w, 10, f"第 {self.page_no()} 页", align="C")


def main() -> None:
    font_path = pick_font()
    git_name = run_git(["config", "user.name"]) or "（未配置）"
    git_email = run_git(["config", "user.email"]) or "（未配置）"
    remote = run_git(["remote", "get-url", "origin"]) or "（无 remote）"
    root = run_git(["rev-list", "--max-parents=0", "HEAD"])
    first_date = run_git(["log", "-1", "--format=%ci", root]) if root else ""
    first_msg = run_git(["log", "-1", "--format=%s", root]) if root else ""
    latest_hash = run_git(["rev-parse", "HEAD"])
    latest_date = run_git(["log", "-1", "--format=%ci"])
    latest_msg = run_git(["log", "-1", "--format=%s"])
    n_commits = run_git(["rev-list", "--count", "HEAD"]) or "0"

    today = datetime.now().strftime("%Y年%m月%d日")

    pdf = Doc()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(16, 16, 16)
    family = "YunjiZH"
    pdf.add_font(family, fname=str(font_path))
    pdf._font_family = family

    pdf.add_page()
    text_w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_font(family, size=18)
    pdf.multi_cell(text_w, 11, "《云迹（yunji）》项目归属与原创性说明", align="C")
    pdf.ln(6)

    pdf.set_font(family, size=11)
    lines = [
        "一、声明目的",
        "    本文件用于说明下列软件仓库所对应之「云迹」校园社区 Web 项目由声明人主导开发与维护，"
        "可作为课程作业、实习/求职材料、竞赛申报等场景下的辅助说明材料。本文件内容包含可核验的 "
        "Git 元数据摘要，但不替代具有法律效力的公证或合同。",
        "",
        "二、仓库与身份信息（由本机 Git 配置与仓库 remote 读取，可复现核验）",
        f"    · 声明人（Git user.name）：{git_name}",
        f"    · 联系邮箱（Git user.email）：{git_email}",
        f"    · 远程仓库地址（origin）：{remote}",
        f"    · 仓库本地路径：{REPO_ROOT}",
        "",
        "三、开发过程客观记录（Git）",
        f"    · 当前分支最新提交：{latest_hash[:12]}…（{latest_date}）",
        f"      摘要：{latest_msg}",
        f"    · 仓库根提交：{root[:12] if root else '—'}…（{first_date}）",
        f"      摘要：{first_msg}",
        f"    · 截至生成时提交总数：{n_commits}",
        "",
        "四、项目内容概要（便于第三方对照仓库）",
        "    本项目为前后端分离的校园社区应用：后端为 Django REST 风格接口；前端为 Vue 3 + Vite "
        "PWA；包含广场帖子、话题、积分与等级、活动专栏、导生管理、情感倾诉与私信等模块。具体以 "
        "仓库内源代码与 README 为准。",
        "",
        "五、原创性声明",
        "    本人声明：上述仓库中的程序源代码、在本人提交范围内之文档与配置，为本人（及本人明确说明"
        "的合作者）创作或依法取得使用权；若存在引用开源组件，均遵循相应开源许可证并在仓库内以依赖"
        "声明等形式体现。",
        "",
        "六、文件生成说明",
        f"    本 PDF 由仓库内脚本 scripts/generate_project_attestation_pdf.py 于 {today} 在本机生成；"
        "生成所依据的 Git 信息可通过在仓库根目录执行相同脚本或手动运行 git 命令复现。",
        "",
        "声明人签字：____________________",
        "日期：____________________",
    ]
    for line in lines:
        if not line.strip():
            pdf.ln(3)
            continue
        pdf.multi_cell(text_w, 7, line)

    desktop = resolve_windows_desktop()
    desktop.mkdir(parents=True, exist_ok=True)
    out_primary = desktop / "云迹yunji项目归属证明.pdf"
    out_ascii = desktop / "yunji-project-attestation.pdf"
    pdf.output(str(out_primary))
    shutil.copy2(out_primary, out_ascii)
    print(out_primary)
    print(out_ascii)


if __name__ == "__main__":
    main()
