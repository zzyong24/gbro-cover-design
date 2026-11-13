# 平台规格与交接

以下为制作预设，不宣称平台永久官方尺寸；开始制作按本次目标入口核对，记录来源与时间。未知变更回生产补图，不在发布页临时设计。只生成选中平台，按实际槽位可调整。

| 配置键 | 原生形式/槽位 | 交付尺寸 | 比例 |
|---|---|---|---|
| douyin | 视频竖封面、横封面 | 1080×1440、1440×1080 | 3:4、4:3 |
| xiaohongshu | 视频/图文笔记竖封面 | 1080×1440 | 3:4 |
| xiaohongshu-landscape | 明确选横版入口时 | 1440×1080 | 4:3 |
| bilibili | 首页推荐、个人空间 | 1440×1080、1920×1080 | 4:3、16:9 |
| channels | 视频号个人页、分享卡 | 1080×1440、1440×1080 | 3:4、4:3 |
| x-article | X Articles头图 | 2000×800 | 5:2 |
| x-post | 明确指定X图片帖 | 1600×900 | 16:9，制作预设，按当期入口核对 |
| wechat-article | 公众号主封面＋同源方形预览 | 1880×800、800×800 | 2.35:1、1:1 |
| wechat-square | 确认可独立上传的方形槽 | 800×800 | 1:1 |
| full-portrait | 明确要求全屏竖封面 | 1080×1920 | 9:16 |

同规格不同槽位可复用已通过安全区检查的图，但 `placements` 须逐项登记，不能把同规格误写成完成了多个不同画幅。9:16不是所有视频默认必出。“X”须区分 Articles 与图片帖，不能以普通帖子比例替代Articles头图。

## 依据与已知范围

- 视频本地尺寸为团队制作基准，2026-10-12曾核对B站4:3/16:9双槽；其他槽位仍以当期创作者界面为准。完整规格矩阵不表示本次已上传验收。
- X Articles 5:2来自社区与团队时间线卡片实测；2000×800为团队制作值，**不是已证实的官方像素要求**。官方帮助：https://help.x.com/en/using-x/articles 。手机/阅读页是否二次裁切必须在实际页面核验。
- 公众号开发文档描述2.35:1和1:1裁切：https://developers.weixin.qq.com/doc/subscription/api/draftbox/draftmanage/api_draft_update ，编辑器坐标：https://developers.weixin.qq.com/doc/subscription/guide/product/mp_editor_jsapi.html 。1880×800与800×800为制作值；资料核对基线2026-10-21，未因本次改Skill而重新宣称在线核实。

## X Articles

2000×800设计左右至少100px、上下至少64px作为初始安全区；左下x=0–300、y=620–800只留背景（旧实测卡片的标签区）。主视觉改为横向对峙、横排巨字或左右关系，不将竖版人物/道具压扁。无人像时保留一组内容物件与巨字的冲击，不退化为平淡的小框列表。

## 公众号：主图与方图是一组

1. 1880×800主图从出图前就安排方形可用区域；默认方形框x=40–840、y=0–800，可按主题改成居中或右侧，但必须记录实际框。主图保留约60px基础安全边距。
2. 同源裁切内至少完整呈现主题关键词与主锚点；不能因主图可读就忽略方形预览。无法兼容时回到主图设计，不靠提交一张独立漂亮方图冒充原生裁切。
3. 生产阶段从**实际最终主图**按坐标生成800×800预览并检查；manifest记录 `kind: crop-preview`、`derivedFrom`、`cropBox`（像素）与 `cropNormalized`。发布侧按原生界面/API实际支持方式填对应坐标；不猜平台能消费独立方图。
4. `wechat-square`仅在确认有独立上传入口时生成独立方图，记录 `kind: generated`；不能代替单源双裁切入口中的方形预览。

## 模型尺寸与生产处理

先按调用工具实际能力选尺寸。支持精确目标就原生生成；例如gpt-image-2要求边长16的倍数，1880×800不直接支持，可生产阶段生成1888×800、预留左右各4px背景后裁为1880×800，记录生成原图、裁切与最终hash；1080等不支持尺寸也用接近的同构图尺寸及预先规划裁切/等比缩放。这个生产处理不允许删除重要文字、脸或证据，不留黑白补边，不把4:3裁成16:9充数。

## 交接

使用 assets/manifest.example.json。每份文件记录目标尺寸、实际路径、生成/派生关系与SHA256；每个槽位记录 platform、slot、assetId、人物模式、规格来源及 `nativeCheck`。封面大字与发布标题分开记录。`visualCheck`只有打开全尺寸及缩略图后才写结果；尺寸程序只能确认文件事实。

脚本（Python3；verify/公众号预览另需Pillow）：

```sh
python3 scripts/cover_contract.py plan --platform douyin --platform x-article --platform wechat-article --out /任务目录/cover-plan.json
python3 scripts/cover_contract.py wechat-preview --image /任务目录/wechat-main.png --out /任务目录/wechat-square-preview.png --crop 40 0 840 800
python3 scripts/cover_contract.py verify /任务目录/cover-manifest.json
```

脚本离线、不生图、不上传；plan只是规格任务单，输出 `missing` 或 `visualPending` 不能称完整交付。测试：`python3 -m unittest discover -s tests`。
