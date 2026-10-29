# Verdant Manor 《未签的判决》— 源工程仓库

维多利亚庄园程序化建模源码 + 人物物证资产。拉取本仓库后**无需任何手工建模**，
一条命令即可在 Blender 中完整重建庄园场景、浏览器游戏资产和搜证版工程。

## 目录结构

```
build_all.py                  一键重建编排（宿主 Python，无需 bpy）
manor/
  scripts/                    程序化建模全流程（14 个 Python 脚本）
  textures/                   全部贴图（Poly Haven CC0 + 本项目原创图案，含 sources.json 溯源）
  validation.json             通路射线校验记录（final_polish.py 读写）
  model_summary.json          场景统计摘要
manor_walkthrough/scripts/
  export_web.py               .blend → 浏览器游戏资产（manor.glb.gz / collision.bin.gz / scene.json）
manor_mystery/
  scripts/
    build_story_blend.py      导入六件 GLB，生成搜证版工程（含原庄园零改动断言）
    prepare.py                校验六件 GLB 哈希 / 从 MagicLomix 源重新复制
  assets/
    anchors.json              人物站位与调查点坐标
    story/*.glb               三名人物 + 三件物证（38MB）
```

## 环境要求

- **Blender 5.2.2 LTS**（开发与验证版本；其他大版本的 bpy API 可能不兼容）
- Python 3（宿主编排用，无需 bpy）
- 仅当删除 `manor/textures/` 后重新生成贴图时，才需要：联网（Poly Haven）+ Pillow
  （Blender 内置 Python 不带 Pillow，请用系统 Python 运行该步）

## 一键重建

```bash
python3 build_all.py
# 或指定 Blender 路径：
python3 build_all.py --blender /Applications/Blender.app/Contents/MacOS/Blender
```

七个步骤：

| 步骤 | 内容 | 产物 |
|---|---|---|
| 1 | 贴图检查（仓库自带即跳过） | — |
| 2 | `build_scene.py` 程序化建场景 | `manor/Verdant_Manor_rebuilt.blend` |
| 3 | `final_polish.py` 家具避让 / 饰面开口 / 通路射线校验 | 更新 `validation.json` |
| 4 | `finish_build.py` 网格合并 + 元数据 + 保存 | `manor/Verdant_Manor.blend` |
| 5 | `export_web.py` 导出浏览器资产 | `manor_walkthrough/assets/manor.glb.gz` 等 |
| 6 | `prepare.py` 校验六件 GLB 哈希 | `assets/source_manifest.json` |
| 7 | `build_story_blend.py` 生成搜证版工程 | `manor_mystery/Verdant_Manor_Mystery.blend` |

可选：`--with-renders` 在步骤 4 换用 `finish_and_render.py`，额外渲染 10 张 Cycles 预览图（很慢，非必需）。

重建结果由 `random.seed(1829)` 确定性保证；`build_story_blend.py` 内含原庄园
变换零改动断言（`signature` 前后比对），搜证版不会碰原庄园任何对象。

### 重建保真度（2026-10-29 实测）

原始 `.blend` 在脚本链之外还有少量增量修改（GUI 内微调与历史补丁），因此重建
产物与原始工程**不是字节级一致**，但游戏要素完全等价：

| 指标 | 重建版 | 原始 .blend 导出 |
|---|---|---|
| 房间数 / 相机 / drawCalls / 出生点 | 27 / 8 / 164 / (0,0.08,18) | 相同 |
| 渲染三角面 | 1,412,471 | 1,475,735（95.7%） |
| 碰撞三角面 | 315,415 | 378,679（83.3%） |
| 通路射线校验 | 90+29 探针全部通过 | — |

差异仅表现为个别装饰细节与冗余碰撞面减少，不影响可玩性；浏览器部署包
（线上在用）仍以原始 .blend 导出的资产为准。

## 单步运行

每个 Blender 步骤也可单独执行：

```bash
BL=/Applications/Blender.app/Contents/MacOS/Blender
$BL --background --factory-startup --python manor/scripts/build_scene.py
$BL --background --factory-startup manor/Verdant_Manor_rebuilt.blend --python manor/scripts/final_polish.py
$BL --background --factory-startup manor/Verdant_Manor.blend --python manor/scripts/finish_build.py
$BL --background --factory-startup manor/Verdant_Manor.blend --python manor_walkthrough/scripts/export_web.py
$BL --background --factory-startup manor/Verdant_Manor.blend --python manor_mystery/scripts/build_story_blend.py
```

## 资产来源与授权

| 资产 | 来源 | 授权 |
|---|---|---|
| 实拍 PBR 材质（5 套） | [Poly Haven](https://polyhaven.com)（`textures/sources.json` 逐条记录） | CC0 |
| 墙纸、地毯、装饰画等图案 | 本项目程序化原创（`prepare_materials.py` 生成） | 自有 |
| 建筑与室内建模 | 本项目脚本原创；视觉参考 Wightwick Manor 照片（未用作贴图） | 自有 |
| 六件人物/物证 GLB | MagicLomix 项目，Tripo 生成（`assets/source_manifest.json` 有哈希） | **商用授权未验证，公开发布前需核实** |

## 与可玩版本的关系

- 本仓库是**源工程**（脚本 + 贴图 + GLB，约 77MB）
- 浏览器**可玩部署包**（121MB，自包含、无需 Blender）单独发布；步骤 5 的导出产物
  与部署包 `assets/` 同源，重新导出后可直接替换部署包的对应文件
- `.blend` 是构建产物，本仓库不含（拉取后重建即可）；如需长期归档二进制，
  建议放对象存储（如腾讯云 COS），仓库只管脚本与源资产
