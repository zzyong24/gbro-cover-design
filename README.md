# gbro-cover-design · 多平台封面

保留原版有冲击力的10种构图与道具叙事，扩展为可交付真实成图的视频、图文和文章封面技能。无需每次固定三轮问答；不强制统一品牌配色。

## 效果（上游原版示例）


<table>
  <tr>
    <td><img src="assets/examples/01-让AI做我老板.webp" width="180"/></td>
    <td><img src="assets/examples/02-下一代Agent来了.webp" width="180"/></td>
    <td><img src="assets/examples/03-3个Skills一个运营部.webp" width="180"/></td>
    <td><img src="assets/examples/04-别再自己操作电脑了.webp" width="180"/></td>
  </tr>
  <tr>
    <td><img src="assets/examples/05-我真不该做这期视频.webp" width="180"/></td>
    <td><img src="assets/examples/06-一键制作拼贴动画.webp" width="180"/></td>
    <td><img src="assets/examples/07-养Agent晚了还有救吗.webp" width="180"/></td>
    <td><img src="assets/examples/08-AI生视频不是模型.webp" width="180"/></td>
  </tr>
</table>

---


## 本fork新增

- 视频/图文：按入口输出3:4、4:3、16:9或明确需要的9:16，横竖独立重排。
- X Articles：5:2（2000×800）；X图片帖单独选择，避免混用规格。
- 公众号：2.35:1主图（1880×800）＋主图同源1:1预览及裁切坐标；确有独立上传槽位时另做方图。
- 真人/无人像模式；身份、风格、产品证据参考图分别声明，个人素材与配置留在用户目录。
- 默认通过宿主已有授权工具生成真实位图并打开检查；仅要提示词时才只交提示词。无工具时如实说明缺口。
- 封面大字与发布标题互补，分别记录；manifest交接每个槽位、成图、尺寸、来源与验收状态。

## 安装

```sh
git clone https://github.com/zzyong24/gbro-cover-design.git ~/.codex/skills/gbro-cover-design
```

其他宿主换成相应skills目录，完整安装references、assets与scripts。已安装时先保存本地修改，再拉取更新；安装技能不等于授权付费、上传或发布。

自然语言示例：“按这份稿件做抖音、B站和X Articles封面，用我的照片，保留原版风格。”或“给公众号做无人像主封面，方形裁切也要能看懂。”

## 配置与依赖

复制 `assets/config.example.json` 到 `~/.config/gbro-cover-design/config.json`，或用 `GBRO_COVER_CONFIG` 指定其他配置路径；填写已授权本地人像路径、平台人像偏好和署名。可完全不配置，直接使用当次输入。**不要将照片、凭据或个人配置提交进仓库**；旧版config.md可只读迁移到外置配置，不删除原件。

宿主须有可用的授权图像生成工具；本技能不附带API凭据或收费服务，不自行充值或切换付费通道。离线规格脚本需要Python3；图片核对、公众号预览与测试需要Pillow（在自己的隔离工具环境安装，不改系统环境）。

```sh
python3 scripts/cover_contract.py plan --platform douyin --platform x-article --platform wechat-article --out /任务目录/plan.json
python3 scripts/cover_contract.py verify /任务目录/manifest.json
python3 -m unittest discover -s tests
```

plan只列任务，verify只查文件/像素/同源裁切事实，不能证明画面好看、本人身份、用户认可、发布授权或平台验收。真实生成的提示词、输入与成图会发送到宿主选定的生图服务，按当次授权使用；个人输入不进入本仓库。

规格、依据时效、安全区与模型尺寸限制见 [平台规格与交接](references/platform-output.md)。风格模板在 `references/style-XX-*.md`，原版提示词在 `references/examples.md`；模板比例现按当期槽位填写，示例仍保留原来的3:4。

## 来源与许可

Fork自 [pyang5166/gbro-cover-design](https://github.com/pyang5166/gbro-cover-design)，其基于 [feitangyuan/oh-my-cover-design](https://github.com/feitangyuan/oh-my-cover-design)。保留上游示例、署名与MIT许可，详见 [LICENSE](LICENSE)。上游示例是风格展示，不代表新增各平台规格均已经原生页面验收。
