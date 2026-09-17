# 从零理解 VLN 与 CityNav：中文可运行教程

这是一套写给 **VLN 初学者** 的中文教程。目标不是让你记住一串模型名，而是让你真正回答下面四个问题：

1. VLN 究竟输入什么、输出什么？
2. 一个 episode 里，无人机如何在多个 step 中反复“看—想—走—停”？
3. CityNav 的语言、轨迹、RGB-D、GNSS/OSM 和 GSM 分别起什么作用？
4. 为什么已经预测出二维目标坐标，仍然需要实时视觉和深度？

仓库包含一套**零第三方依赖的教学环境**、指标实现、数据检查工具，以及迁移到官方 CityNav 代码的复现说明。

> [!IMPORTANT]
> `citynav_tutorial/` 是为了教学而设计的简化实现，不是官方 CityNav simulator 或论文基线。凡是教学近似，文中都会明确标记；正式实验请使用 [CityNav 官方仓库](https://github.com/water-cookie/citynav)。

## 教程框架

```text
阶段 0：先建立全局图景
  └─ VLN = 语言目标 + 连续观测 + 历史状态 → 动作/目标

阶段 1：掌握最小导航闭环
  ├─ episode、step、observation、action、STOP
  └─ 亲手运行一个多步无人机导航 episode

阶段 2：读懂 CityNav 数据集
  ├─ 任务、规模、数据来源、划分、语言与轨迹
  ├─ RGB、Depth、位姿、CityRefer、OSM/GNSS、GSM
  └─ 用检查器查看真实 JSON，而不是只看论文表格

阶段 3：理解 CityNav 如何导航
  ├─ 语言 grounding：文字中的地标 → 地理实体
  ├─ 宏观目标预测：当前状态 → 地图上的子目标/目标点
  ├─ 局部控制：目标点 + RGB-D → 安全动作
  └─ 每一步更新历史，直到 STOP 或超时

阶段 4：学会评价结果
  └─ NE、SR、OSR、SPL，以及“经过目标却不会停”的含义

阶段 5：走向研究复现
  ├─ 官方环境、数据和基线
  └─ GSM/MGP、FlightGPT、SA-GCS、HETT、HTNav 等研究路线
```

## 章节导航

| 顺序 | 章节 | 学完后能回答 |
|---:|---|---|
| 0 | [学习路线](docs/00_学习路线.md) | 今天先学什么、哪些内容可以后学？ |
| 1 | [VLN 基础](docs/01_VLN基础.md) | VLN 与分类、目标检测、普通路径规划有什么区别？ |
| 2 | [CityNav 数据集详解](docs/02_CityNav数据集详解.md) | CityNav 一条数据里有什么，train/test 如何划分？ |
| 3 | [一个 episode 如何运行](docs/03_一个Episode如何运行.md) | 两个连续 step 中，模型分别看到了什么、更新了什么？ |
| 4 | [GSM 与 MGP](docs/04_GSM与MGP.md) | GSM 如何构造、为什么能显著提高 SR？ |
| 5 | [指标与结果解读](docs/05_指标与结果解读.md) | SR、OSR、SPL 和 NE 为什么可能互相矛盾？ |
| 6 | [官方代码复现](docs/06_官方代码复现.md) | 如何从教学代码迁移到正式 CityNav 实验？ |
| 7 | [后续论文与研究路线](docs/07_后续论文与研究路线.md) | 后续方法各自在解决哪类瓶颈？ |

## 5 分钟跑通第一个 episode

要求：Python 3.10 或更高版本。教学示例只使用 Python 标准库。

```bash
git clone <你的仓库地址>
cd citynav-vln-tutorial-zh
python examples/run_toy_episode.py
```

你会看到每一步的位姿、可见地标、动作和目标距离，最后输出：

```text
NE  = ... m     # 最终位置离目标多远
SR  = 1         # 最终是否成功
OSR = 1         # 途中是否曾到达目标附近
SPL = ...       # 成功且路线是否高效
```

这个示例做了四件事：

```mermaid
flowchart LR
    A[中文指令] --> B[在 GSM 中找到图书馆]
    B --> C[解析“南侧 20 米”]
    C --> D[得到地图目标 80,20]
    D --> E[逐步转向/前进]
    E --> F{够近了吗?}
    F -- 否 --> E
    F -- 是 --> G[STOP 并计算指标]
```

真实 CityNav 的区别是：目标 grounding 和动作预测由视觉模型/神经网络完成，观测来自真实城市三维点云渲染的 RGB-D，而不是本教程的字符串提示和二维几何规则。

## 检查真实 CityNav JSON

下载官方数据后，可以先检查字段，避免一开始就陷入训练代码：

```bash
python examples/inspect_citynav.py data/citynav/citynav_train_seen.json
python examples/inspect_citynav.py data/cityrefer/processed_descriptions.json
python examples/inspect_citynav.py data/cityrefer/objects.json
```

检查器会显示顶层类型、记录数量、首条数据字段，并尝试定位 instruction、trajectory、target 和 episode id。它不会修改数据。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

测试覆盖两个最容易混淆的问题：

- 一个策略能否在有限 step 内完成 episode 并正确 STOP；
- “途中到过目标”（OSR=1）但“最终停错位置”（SR=0）是否被正确区分。

## 推荐学习方式

第一次学习时，不要先读所有论文。按下列顺序操作：

1. 阅读第 1、3 章，同时运行 `run_toy_episode.py`。
2. 修改 `examples/toy_citynav.json` 的起点、地标和指令，观察动作序列如何变化。
3. 阅读第 2、4、5 章，把代码变量对应到真实 CityNav 的数据与指标。
4. 拿到真实数据后运行 `inspect_citynav.py`。
5. 最后再进入官方基线和后续论文复现。

## 权威来源与边界

本教程以公开材料为依据，并区分“论文事实”“官方代码事实”和“教学解释”：

- [CityNav 官方代码与 README](https://github.com/water-cookie/citynav)
- [CityNav 项目主页](https://water-cookie.github.io/citynav/)
- [CityNav ICCV 2025 论文 PDF](https://openaccess.thecvf.com/content/ICCV2025/papers/Lee_CityNav_A_Large-Scale_Dataset_for_Real-World_Aerial_Navigation_ICCV_2025_paper.pdf)
- [FlightGPT, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.338/)

数据规模、命名或代码接口可能随官方仓库更新而变化；正式汇报或论文实验请以你使用的 commit、数据版本和论文正文为准，并在实验记录中固定版本。

## License

教程代码采用 [MIT License](LICENSE)。CityNav 数据、官方代码、论文图表和模型权重遵循各自项目的许可协议，本仓库不重新分发它们。
