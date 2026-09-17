from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LIKELY_FIELDS = {
    "instruction": ("instruction", "description", "text", "route_description"),
    "trajectory": ("trajectory", "path", "positions", "waypoints"),
    "target": ("target", "goal", "target_position", "destination"),
    "episode_id": ("episode_id", "trajectory_id", "id"),
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def first_record(data: Any) -> Any:
    if isinstance(data, list):
        return data[0] if data else None
    if isinstance(data, dict):
        for key in ("episodes", "data", "trajectories", "descriptions"):
            value = data.get(key)
            if isinstance(value, list) and value:
                return value[0]
        return data
    return data


def inspect(path: Path) -> str:
    data = load_json(path)
    record = first_record(data)
    lines = [f"文件: {path}", f"顶层类型: {type(data).__name__}"]
    if isinstance(data, list):
        lines.append(f"顶层记录数: {len(data)}")
    elif isinstance(data, dict):
        lines.append("顶层键: " + ", ".join(map(str, data.keys())))
    if isinstance(record, dict):
        lines.append("首条记录字段: " + ", ".join(map(str, record.keys())))
        for semantic_name, candidates in LIKELY_FIELDS.items():
            found = next((name for name in candidates if name in record), None)
            lines.append(f"  {semantic_name:12s} -> {found or '未自动识别'}")
    preview = json.dumps(record, ensure_ascii=False, indent=2)
    lines.extend(["", "首条记录预览（最多 2000 字符）:", preview[:2000]])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="检查 CityNav JSON 的顶层结构和常见字段")
    parser.add_argument("json_path", type=Path)
    args = parser.parse_args()
    print(inspect(args.json_path))


if __name__ == "__main__":
    main()
