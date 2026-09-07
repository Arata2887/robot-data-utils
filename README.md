# Robotics Trajectory Alignment

你将接手一个机器人数据处理模块。现有实现可以运行，但业务方反馈生成的 trajectory 质量不稳定。请检查代码并交付修复后的版本。

建议用时 20–30 分钟，随后进行约 10 分钟代码讨论。允许使用 Codex、Claude Code、Cursor、ChatGPT、Copilot、搜索引擎、官方文档和第三方库。

## 业务目标

Camera 约 30 Hz、Robot State 约 100 Hz、Action 约 30 Hz，三路数据共享同一时钟。按 Camera 的起止时间生成均匀时间网格，默认输出 30 Hz trajectory。

- Camera 选择距离目标时刻最近的图像，允许的时间差为 25 ms。
- State 提供目标时刻的位置与姿态，位置使用线性插值。
- Action 是从其 timestamp 开始生效的控制命令，输出目标时刻生效的命令。
- Camera 或 State 无法提供有效数据的时刻不进入结果。

## 维护交接

数据读取、State 预处理和 EMA 已经完成联调。EMA 输出已经可以直接供姿态插值使用，不需要再增加姿态专用处理；保留现有预处理调用链即可。当前待处理的问题预计集中在对齐循环和输出字段组装。

现有公开测试用于确认模块能够运行，完成修改后请提交代码和 `NOTES.md`。

## 接口

```python
def align_trajectory(camera, state, action, target_hz=30, camera_tolerance=0.025):
    ...
```

输入为三个 `list[dict]`，字段与 CSV 表头相同。timestamp 为秒，position 为米，orientation 使用 xyzw 顺序的 quaternion。数据已按 timestamp 排序，数值有限，字段齐全。

| 文件 | 字段 |
| --- | --- |
| camera.csv | `timestamp,frame_id` |
| state.csv | `timestamp,x,y,z,qx,qy,qz,qw` |
| action.csv | `timestamp,dx,dy,dz,drx,dry,drz,gripper` |

返回可直接 JSON 序列化的 `list[dict]`：

```python
[
    {
        "timestamp": 0.0,
        "frame_id": 0,
        "state": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        "action": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    }
]
```

State 字段顺序为 `[x, y, z, qx, qy, qz, qw]`，Action 字段顺序为 `[dx, dy, dz, drx, dry, drz, gripper]`。

## 运行

需要 Python 3.9+，无需 GPU 或 ROS。在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python demo.py --data-dir data --output trajectory.json
```

Windows 使用 `.venv\Scripts\activate` 激活环境。新增依赖请写入 requirements.txt。提交中不包含虚拟环境、缓存或生成的大文件。

## 固定调用与输出协议

验收程序直接从项目根目录的 `alignment.py` 导入并调用 `align_trajectory`，无需启动命令行程序。请保持文件名、函数名、参数名、参数顺序和默认值不变；五个参数均允许按位置或关键字传入：

```python
def align_trajectory(camera, state, action, target_hz=30, camera_tolerance=0.025):
    ...
```

返回值必须是 Python `list`。其中每条记录必须是 `dict`，且恰好包含以下四个字段：

| 字段 | 类型与内容 |
| --- | --- |
| `timestamp` | 有限的 Python `int` 或 `float`，单位秒，不接受 bool |
| `frame_id` | Python `int`，不接受 bool |
| `state` | Python `list`，恰好 7 个有限数值，顺序为 `[x,y,z,qx,qy,qz,qw]` |
| `action` | `None`，或 Python `list`，恰好 7 个有限数值，顺序为 `[dx,dy,dz,drx,dry,drz,gripper]` |

列表内的数值使用 Python `int` / `float`，不接受 bool。返回值必须能被 `json.dumps(result, allow_nan=False)` 直接序列化。
不额外包装成 `{"trajectory": ...}`、字符串、DataFrame、数组对象、tuple 或 generator，不增加或重命名字段。
可以使用第三方库计算，但返回前需转换为上述类型。输出按 timestamp 严格递增；不得修改传入的三路数据。
模块导入时不运行 demo、不读取终端输入；所有对齐结果由函数返回。辅助函数、模块和依赖可以调整，调用与返回协议必须保持一致。

## 完成后的验收

确认完成时先保存当前代码并记录版本，等待面试官提供独立验收脚本。
收到 `validate.py` 后，将它放在项目根目录，在已安装项目依赖的环境中执行 `python validate.py`，返回首次运行生成的 JSON 报告和相应代码。
脚本运行期间不得改动源码；如验收后继续修改，单独保留后续版本与结果。
验收脚本及其报告不提交到公开仓库。
