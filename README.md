# paper-figure-reconstruction

将论文 PNG、截图或 PDF 中的科研示意图重建为**可编辑 SVG、真实 Blender 三维模型，以及可选的 Adobe Illustrator AI 文件**的 Codex Skill。

**从一张参考图，建立一个能检查、能修改、能继续维护的科研绘图工程。** 项目围绕参考图的布局、形状、文字和科学关系组织工作，将二维标注与三维建模分别交给合适的工具，并通过可追溯的源文件修改逐步提高相似度。

这是一个 **Codex Skill + 本地辅助脚本**项目：Codex 负责观察参考、分解结构和编写复杂建模代码，脚本负责重复执行生成、渲染、比较与导出。

## 项目有什么特点？

| 特点 | 具体做法 | 对使用者的价值 |
|---|---|---|
| **忠于参考的逆向重建** | 先拆分 panel、文字、箭头、物体及遮挡关系，再拟合布局和几何 | 可以沿用论文的表达结构，而不是重新设计一张无关的图 |
| **三维部分真实建模** | 使用 Blender mesh、curve、材质、相机和灯光；保留 `.blend` 与建模代码 | 后续可以改变结构、角度或视点；不会把截图平面冒充三维模型 |
| **二维与三维协同** | SVG 保留原生文字和路径；Blender 输出透明渲染；Illustrator 可选地分层排版 | 兼顾三维质感和标注编辑，纯二维任务也能独立完成 |
| **修改源文件后迭代** | 用组件 ID、`figure-spec.json` 和项目脚本定位修改对象，再重新渲染 | 能定向调整某个箭头、晶片或 panel，并检查需要保留的部分 |
| **视觉与语义分别验收** | 同尺寸叠图、差异图、SSIM、轮廓距离，加上箭头方向、旋向和结构核对 | 能定位偏差，也能发现“分数很高但关键元素错误”的情况 |
| **面向长期维护** | 保存源码和来源信息，提供问题模板、回归测试及更新备份 | 遇到问题可以给出最小复现，再修复、验证和更新安装副本 |

这些特点包含工作流约定和已实现的工具能力。尤其是科学语义判断、复杂几何建模和最终视觉验收，仍需要 Codex 分析及使用者审阅，并非全部由脚本自动完成。

## 适合什么任务？

- **论文示意图重建**：从 PNG、截图或指定 PDF 页/区域恢复布局、文字、箭头和对象层级。
- **二维标注与三维物体混合的图**：例如材料堆叠、光路元件或装置示意；复杂形状通过项目专用 Blender Python 实现。
- **已有工程的局部修改**：增加 panel、更改晶片转角、替换标注，同时明确哪些内容必须保持不变。

如果目标是从曲线图提取实验数据、从单张图片恢复不可见的精确三维结构，或生成与参考无关的新视觉设计，需要其他方法。没有晶体学数据时，图中的原子排布只能作为有明确假设的示意模型，不能宣称恢复了真实晶体结构。

## 图 1：从参考图到可验证的重建

```mermaid
flowchart TD
    R["参考 PNG / 截图 / PDF 指定区域"] --> A["Codex 分析结构、文字、层级与科学关系"]
    A --> S["figure-spec.json 与项目源码"]
    S --> V["二维：原生 SVG 文字与路径"]
    S --> B["三维：Blender 几何建模与透明渲染"]
    V --> C["合成预览 PNG"]
    B --> C
    R -. "只用于观察和比较" .-> Q["视觉比较 + 科学语义 + 可编辑性检查"]
    C --> Q
    Q --> D{"满足本次验收目标？"}
    D -- "否：定位具体偏差" --> F["定向修改布局、相机、几何或标注"]
    F --> S
    D -- "是" --> O["交付源文件、预览与质量报告"]
```

这是一轮轮修改源文件的过程。优先处理布局、相机和轮廓，再调整内部结构、文字、材质与灯光。无法从参考确定的信息和仍存在的偏差要进入报告；指标提高并不自动代表科学含义正确。

## 图 2：文件之间的关系与可编辑范围

```mermaid
flowchart LR
    P["figure-spec.json<br/>组件、布局与参数"] --> S["SVG<br/>原生文字、箭头与路径"]
    P --> C["Blender Python<br/>项目建模逻辑"]
    C --> B["BLEND<br/>几何、材质、相机与灯光"]
    B --> R["自行渲染的 PNG<br/>三维部分的二维投影"]
    R --> S
    S --> I["Illustrator JSX<br/>可选：分层、排版与置入渲染"]
    I --> AI["AI<br/>二维对象可编辑；三维渲染为位图"]
    S --> PNG["最终 PNG<br/>查看、比较与使用"]
    AI --> PNG
```

| 想修改什么？ | 修改入口 | 需要注意 |
|---|---|---|
| 标注文字、箭头端点、二维布局 | spec / SVG；或 AI 中的原生对象 | AI 中的手工改动不会自动回写 spec 或 SVG |
| 原子位置、物体形状、旋转角度、相机与材质 | Blender 建模脚本 / `.blend` | 改完后重新渲染，再更新合成图中的渲染素材 |
| 最终图片尺寸、画布和图层排版 | spec / 合成逻辑；或 AI | 比较前显式统一画布尺寸，并记录裁剪或缩放 |
| 重建质量和遗漏项 | 对比图、指标 JSON、质量报告 | PNG 便于查看，但不包含原生文字或三维几何 |

内嵌渲染的 SVG/AI 并非全矢量文件；三维几何保存在 BLEND 中。`figure-spec.json` 是布局与参数的约定入口，复杂建模逻辑仍由项目代码表达。这个最小版本不提供应用间的双向自动同步：若直接修改 AI 或 Blender，需要相应维护源参数或脚本，才能在下次重建时保留改动。

---

## 安装到 Codex

先克隆仓库到长期保留的开发目录，再安装 Skill：

```bash
git clone https://github.com/HyNlity/paper-figure-reconstruction.git
cd paper-figure-reconstruction
python3 scripts/install_skill.py
```

默认安装到 `~/.codex/skills/paper-figure-reconstruction/`；若设置了 `CODEX_HOME`，则安装到其 `skills/` 下。也可通过 `--target` 指定路径。安装器只复制 Skill 所需文件，不复制测试、论文素材或 Git 历史。

首次安装拒绝覆盖已有目录。更新时：

```bash
git pull --ff-only
python3 scripts/install_skill.py --update
```

更新前会完整备份现有 Skill 到同级 `skill-backups/`，备份不进入可发现的 `skills/` 目录。先在仓库修改和测试，再更新全局副本；不要长期只修改全局安装目录，否则后续同步容易丢失改动。安装器只管理本 Skill，不修改 Codex 配置或安装软件。

## 日常使用

在 Codex 中附上参考图或 PDF，调用：

> 使用 $paper-figure-reconstruction 重建这张论文图。三维部分必须真实建模，文字保持可编辑。交付 SVG、BLEND、可用时的 AI，以及视觉对比报告。

继续已有工作时，提供原始 `.blend` / SVG / AI 和需要保留的内容：

> 基于已有工程扩展 panel b，保持 panel a 不变。先核对相机、原子布局和旋转方向，再调整材质；验证 panel a 未发生变化。

不要求每张图都经过所有软件。纯二维图只需 SVG；真正的三维物体在 Blender 中建模。SVG/AI 可以包含自行渲染的 PNG，但该部分的几何编辑入口是 `.blend`。

## 工作流与产物

1. 阅读参考，识别 panels、文字、箭头、几何、遮挡和层级，记录不确定信息。
2. 建立 `figure-spec.json`：稳定组件 ID、归一化二维坐标、颜色、字体、三维参数和来源信息。
3. 生成原生 SVG 或 Blender Python 建模脚本，保存可编辑源文件。
4. 同尺寸渲染，生成叠图、差异图、SSIM 和轮廓距离，逐 panel 核对。
5. 定向修改布局、相机、几何、标注及材质，再重新渲染。
6. 可用时通过 Illustrator JSX 导入、分层并保存 AI；实际修改对象、重新打开并渲染，验证可编辑性。

典型交付：`figure.png`、`figure.svg`、三维工作的 `figure.blend`、可用时的 `figure.ai`、`figure-spec.json`、建模源码、环境清单、比较图与质量报告。论文原图不能充当重建纹理或成品素材；保留出处及版权标记，公开复用前核查论文图片许可。

## 环境与命令行工具

基础运行时：Python 3.9+、NumPy、Pillow；SVG 渲染需要 Node.js 和 Sharp。Blender、Illustrator、Poppler 按任务需要使用。MCP **不是必需依赖**，也不默认假设存在“官方 Illustrator MCP”。

先检查已有环境：

```bash
python3 scripts/figure.py doctor --out environment.json
```

如果已有 Codex 运行时包含这些库，直接使用其 Python / Node。只有确认需要新环境时，再自行选择以下安装方式；Skill 不会自动执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm install
```

用原创示例运行二维最小流程：

```bash
python scripts/figure.py svg --spec examples/two-panel/figure-spec.json --out output/figure.svg
node scripts/render_svg.cjs output/figure.svg output/figure.png
python scripts/figure.py audit-svg --svg output/figure.svg
python scripts/figure.py compare --reference examples/two-panel/reference.png --candidate output/figure.png --spec examples/two-panel/figure-spec.json --out output/comparison
```

Sharp 解析顺序：`PFR_NODE_MODULES`、普通 Node 模块查找、已有 Codex bundled runtime。`PFR_NODE_MODULES` 应指向包含 Sharp 的 `node_modules` 目录。

三维与 Illustrator 入口：

```bash
python scripts/figure.py blender --spec figure-spec.json --out output/3d --dry-run
python scripts/figure.py illustrator --spec figure-spec.json --svg output/figure.svg --out output/ai
```

前者输出待审批执行的 Blender 命令，不绕过沙盒；复杂几何用 `--script rebuild.py` 指定自定义建模脚本。后者生成 `import.jsx` 和矢量导入文件，不自动启动 Illustrator。执行方法见 [应用适配说明](references/applications.md)。

## 已知问题与处理方式

| 现象 | 处理 |
|---|---|
| 本机 Blender 4.5.10 在沙盒内 Metal 检测时崩溃 | 按环境要求申请沙盒外执行；CPU 渲染不能避开启动检测；不要反复重试或重置偏好设置 |
| Illustrator 中箭头只剩头部 | 已改为显式原生箭杆和头部路径，避免 SVG marker 导入问题 |
| 含内嵌图像的 SVG 导入 Illustrator 长时间占用 | 适配器先导入矢量占位，再原生置入/嵌入自建 PNG；超时后先检查进程，不立即重复执行 |
| 文字出现方框或字体替代 | 核对字体和具体字形；数学符号必要时单独用可编辑路径，保留其他原生文字 |
| SSIM 很高但缺少关键箭头 | 同时检查 panel、局部结构与科学语义；指标不是完整性证明 |
| 两张预览尺寸不同 | 显式统一画布、裁剪并记录转换；比较器不会偷偷缩放或变形对齐 |
| 密集大图的轮廓比较较慢 | 当前采用精确分块最近距离；先对明确记录尺寸的预览/局部区域诊断，再做最终尺寸比较 |

这些是实际遇到并验证的具体问题，不代表对所有软件版本和平台的保证。当前真实应用测试环境为 macOS、Blender 4.5.10 LTS、Illustrator 30.4.0。

## 遇到问题后，如何让我继续维护

建议在 [Issues](https://github.com/HyNlity/paper-figure-reconstruction/issues) 新建问题，使用“Bug report”模板，记录软件版本、最小复现步骤、期望与实际结果、错误日志和允许分享的参考/输出。没有合适的公开素材时，只描述问题或提供原创最小示例，不上传未授权论文和未公开研究资料。

之后可直接在 Codex 中说：

> 请维护 [paper-figure-reconstruction](https://github.com/HyNlity/paper-figure-reconstruction)，修复 issue #编号。先复现，再修改源代码并加入回归测试；验证通过后提交。若需要更新本机全局 Skill，请先核对并备份现有副本。

没有 issue 时也可以说：

> 使用 paper-figure-reconstruction 时，Illustrator 导出的箭头丢失。参考文件在……，预览在……，版本为……。请在仓库修复，并说明根因、验证结果和仍未解决的问题。

每次维护应明确：复现证据 → 根因/假设 → 最小修改 → 回归测试 → 实际应用验证 → 提交与安装同步。仓库中的 [AGENTS.md](AGENTS.md) 给后续维护者保留了这些约束；需要外部应用的验证不能用纯 Python 测试冒充。

## 测试与证据边界

```bash
python -m unittest discover -s tests -v
```

测试覆盖 SVG 原生文字/箭头、错误输入、比较器对平移和缺失元素的响应，以及安装/更新时的备份行为。不会启动 Blender / Illustrator，也不会安装依赖。

初始人工与应用验证还包括：

- 原创二维图：SSIM 0.910550 → 0.994837，轮廓平均误差 0.418104 → 0.102396 px；8 个原生文字；原生 AI 文字/箭杆编辑后另一 panel 像素不变。
- 既有晶体工程：修改真实几何、保存后重新打开、迁移目录重建通过；原工程保持不变。与论文参考的基线 SSIM 约 0.704800，**未达到 1:1**。
- Illustrator 混合图：成功置入自行渲染的 PNG，0 外链；真实三维结构在 BLEND 中编辑。

仓库仅包含可公开的原创二维示例；论文参考、私人路径和大型本地工程不随仓库发布。两例验证的是工作流与可编辑性，不是任意论文的自动识别能力。

## 项目结构

```text
SKILL.md                  Codex Skill 入口
agents/openai.yaml        Skill 展示信息
scripts/                  环境检查、SVG、比较、Blender、Illustrator、安装工具
references/               spec、应用适配、验收与参考项目审查
examples/two-panel/       原创参考、spec、SVG 与预览
tests/                    无需桌面应用的回归测试
.github/ISSUE_TEMPLATE/   问题反馈模板
AGENTS.md                 后续 Codex 维护约定
```

参考项目的能力、依赖和许可证审查见 [project-review.md](references/project-review.md)。本项目当前没有复制其源码或字体；第三方代码许可不等于论文图像的使用许可。
