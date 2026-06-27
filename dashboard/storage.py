import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils import timezone


DEFAULT_DAILY_SCORE_DATA: dict[str, Any] = {
    "version": "1.0",
    "name": "Daily Evolution Score",
    "total_score": 100,
    "dimensions": [
        {
            "id": "long_term_growth",
            "name": "长期成长",
            "max": 30,
            "description": "是否提升未来数年的核心能力，如数学、英语、计算机基础、算法、Project Genesis、科研能力等。",
        },
        {
            "id": "survival_progress",
            "name": "现实推进",
            "max": 20,
            "description": "是否改善现实处境，如找工作、收入、接单、资源配置、人际合作等。",
        },
        {
            "id": "project_progress",
            "name": "项目推进",
            "max": 15,
            "description": "是否推进长期项目，如CPU模拟器、GitHub、开源项目、作品集等。",
        },
        {
            "id": "health",
            "name": "身体健康",
            "max": 10,
            "description": "睡眠、饮食、运动、休息恢复是否合理。",
        },
        {
            "id": "self_management",
            "name": "自我管理",
            "max": 10,
            "description": "是否按计划执行，避免拖延，诚实面对自己。",
        },
        {
            "id": "thinking_upgrade",
            "name": "思维升级",
            "max": 10,
            "description": "是否获得新的理解、建立新的知识框架或世界模型。",
        },
        {
            "id": "emotion",
            "name": "情绪稳定",
            "max": 5,
            "description": "面对压力是否保持稳定，没有被情绪完全影响行动。",
        },
    ],
    "grade": [
        {"min": 95, "level": "S"},
        {"min": 90, "level": "A+"},
        {"min": 80, "level": "A"},
        {"min": 70, "level": "B"},
        {"min": 60, "level": "C"},
        {"min": 0, "level": "D"},
    ],
    "records": [
        {
            "date": "2026-06-22",
            "score": {
                "long_term_growth": 27,
                "survival_progress": 4,
                "project_progress": 13,
                "health": 9,
                "self_management": 9,
                "thinking_upgrade": 9,
                "emotion": 5,
            },
            "total": 76,
            "grade": "B",
            "multiplier": 4,
            "confidence": 0.78,
            "summary": "完成高质量学习和项目推进，主动恢复体力，但现实收入推进较少。",
        },
        {
            "date": "2026-06-23",
            "score": {
                "long_term_growth": 24,
                "survival_progress": 3,
                "project_progress": 5,
                "health": 7,
                "self_management": 8,
                "thinking_upgrade": 10,
                "emotion": 4,
            },
            "total": 61,
            "grade": "C",
            "multiplier": 3,
            "confidence": 0.64,
            "summary": "完成较多战略思考，但缺少具体行动推进。",
        },
        {
            "date": "2026-06-24",
            "score": {
                "long_term_growth": 22,
                "survival_progress": 2,
                "project_progress": 6,
                "health": 7,
                "self_management": 8,
                "thinking_upgrade": 9,
                "emotion": 5,
            },
            "total": 59,
            "grade": "D",
            "multiplier": 3,
            "confidence": 0.68,
            "summary": "探索能力较强，但当天成果更多停留在兴趣探索，对当前目标的直接推进有限。",
        },
        {
            "date": "2026-06-25",
            "score": {
                "long_term_growth": 24,
                "survival_progress": 8,
                "project_progress": 9,
                "health": 8,
                "self_management": 9,
                "thinking_upgrade": 8,
                "emotion": 5,
            },
            "total": 71,
            "grade": "B",
            "multiplier": 4,
            "confidence": 0.76,
            "summary": "持续维护长期习惯，并开始考虑优化资源配置。",
        },
        {
            "date": "2026-06-27",
            "score": {
                "long_term_growth": 20,
                "survival_progress": 18,
                "project_progress": 10,
                "health": 6,
                "self_management": 9,
                "thinking_upgrade": 7,
                "emotion": 5,
            },
            "total": 75,
            "grade": "B",
            "multiplier": 4,
            "confidence": 0.92,
            "summary": "开始主动建立收入渠道，将赚钱从想法转化为行动，同时完成必要的生活事务。",
        },
    ],
}


class ScoreDataError(ValueError):
    """Raised when the JSON text storage has an invalid shape."""


def score_file_path() -> Path:
    return Path(settings.DAILY_SCORE_FILE)


def ensure_score_file() -> Path:
    path = score_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        write_score_data(DEFAULT_DAILY_SCORE_DATA)

    return path


def load_score_data() -> dict[str, Any]:
    path = ensure_score_file()

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    validate_score_data(data)
    return data


def save_record(record: dict[str, Any]) -> dict[str, Any]:
    data = load_score_data()
    dimension_ids = {dimension["id"] for dimension in data["dimensions"]}
    normalized = normalize_record(record, data["dimensions"], data["grade"])
    validate_record(normalized, dimension_ids)

    records = data["records"]
    replaced = False

    for index, current in enumerate(records):
        if current["date"] == normalized["date"]:
            records[index] = normalized
            replaced = True
            break

    if not replaced:
        records.append(normalized)

    records.sort(key=lambda item: item["date"])
    write_score_data(data)
    return normalized


def write_score_data(data: dict[str, Any]) -> None:
    validate_score_data(data)
    path = score_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as temp_file:
        temp_file.write(payload)
        temp_name = temp_file.name

    os.replace(temp_name, path)


def reset_score_file() -> None:
    write_score_data(deepcopy(DEFAULT_DAILY_SCORE_DATA))


def validate_score_data(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ScoreDataError("score data must be a JSON object")

    required_keys = {"version", "name", "total_score", "dimensions", "grade", "records"}
    missing = required_keys - data.keys()

    if missing:
        raise ScoreDataError(f"missing keys: {', '.join(sorted(missing))}")

    if not isinstance(data["dimensions"], list) or not data["dimensions"]:
        raise ScoreDataError("dimensions must be a non-empty list")

    dimension_ids = set()

    for dimension in data["dimensions"]:
        if not isinstance(dimension, dict):
            raise ScoreDataError("each dimension must be an object")
        if not isinstance(dimension.get("id"), str) or not dimension["id"]:
            raise ScoreDataError("each dimension needs a string id")
        if not isinstance(dimension.get("name"), str) or not dimension["name"]:
            raise ScoreDataError("each dimension needs a string name")
        if not isinstance(dimension.get("max"), int) or dimension["max"] <= 0:
            raise ScoreDataError("each dimension needs a positive integer max")
        dimension_ids.add(dimension["id"])

    if not isinstance(data["records"], list):
        raise ScoreDataError("records must be a list")

    for record in data["records"]:
        validate_record(record, dimension_ids)


def normalize_record(
    record: dict[str, Any],
    dimensions: list[dict[str, Any]],
    grades: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ScoreDataError("record must be an object")

    normalized = deepcopy(record)
    normalized["date"] = str(normalized.get("date") or timezone.localdate().isoformat())
    score = normalized.get("score")

    if not isinstance(score, dict):
        raise ScoreDataError("record needs a score object")

    total = 0

    for dimension in dimensions:
        value = score.get(dimension["id"])

        if isinstance(value, str) and value.strip().isdigit():
            value = int(value)
            score[dimension["id"]] = value

        if not isinstance(value, int):
            raise ScoreDataError(f"{dimension['id']} must be an integer")
        if value < 0 or value > dimension["max"]:
            raise ScoreDataError(f"{dimension['id']} must be between 0 and {dimension['max']}")

        total += value

    summary = str(normalized.get("summary") or "").strip()
    normalized["total"] = total
    normalized["grade"] = grade_for_total(total, grades)
    normalized["multiplier"] = estimate_multiplier(score, dimensions)
    normalized["confidence"] = estimate_confidence(score, dimensions, summary)
    normalized["summary"] = summary or "当天记录已保存，待补充总结。"

    if normalized["multiplier"] < 1 or normalized["multiplier"] > 5:
        raise ScoreDataError("multiplier must be between 1 and 5")

    if normalized["confidence"] < 0 or normalized["confidence"] > 1:
        raise ScoreDataError("confidence must be between 0 and 1")

    return normalized


def estimate_multiplier(score: dict[str, int], dimensions: list[dict[str, Any]]) -> int:
    weighted_ids = {"long_term_growth", "survival_progress", "project_progress", "thinking_upgrade"}
    dimension_map = {dimension["id"]: dimension for dimension in dimensions}
    ratios = [
        score.get(dimension_id, 0) / dimension_map[dimension_id]["max"]
        for dimension_id in weighted_ids
        if dimension_id in dimension_map
    ]
    ratio = sum(ratios) / len(ratios) if ratios else 0

    if ratio >= 0.82:
        return 5
    if ratio >= 0.62:
        return 4
    if ratio >= 0.42:
        return 3
    if ratio >= 0.22:
        return 2
    return 1


def estimate_confidence(score: dict[str, int], dimensions: list[dict[str, Any]], summary: str) -> float:
    filled_scores = sum(1 for dimension in dimensions if score.get(dimension["id"], 0) > 0)
    score_completeness = filled_scores / len(dimensions) if dimensions else 0
    summary_length = len(summary)

    if summary_length >= 80:
        summary_signal = 0.18
    elif summary_length >= 30:
        summary_signal = 0.12
    elif summary_length > 0:
        summary_signal = 0.06
    else:
        summary_signal = 0

    return round(max(0.3, min(0.98, 0.56 + score_completeness * 0.24 + summary_signal)), 2)


def grade_for_total(total: int, grades: list[dict[str, Any]]) -> str:
    sorted_grades = sorted(grades, key=lambda item: item["min"], reverse=True)

    for grade in sorted_grades:
        if total >= grade["min"]:
            return grade["level"]

    return "D"


def validate_record(record: dict[str, Any], dimension_ids: set[str]) -> None:
    if not isinstance(record, dict):
        raise ScoreDataError("each record must be an object")

    if not isinstance(record.get("date"), str) or not record["date"]:
        raise ScoreDataError("each record needs a date")

    score = record.get("score")

    if not isinstance(score, dict):
        raise ScoreDataError("each record needs a score object")

    missing_dimensions = dimension_ids - score.keys()

    if missing_dimensions:
        raise ScoreDataError(
            f"{record['date']} is missing score dimensions: {', '.join(sorted(missing_dimensions))}",
        )

    for key in dimension_ids:
        if not isinstance(score[key], int) or score[key] < 0:
            raise ScoreDataError(f"{record['date']} has invalid score value for {key}")

    if not isinstance(record.get("summary"), str):
        raise ScoreDataError(f"{record['date']} needs a summary")
