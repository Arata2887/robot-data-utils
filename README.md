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
