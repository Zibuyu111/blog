# Daily Evolution Dashboard

一个小型 Django 页面，用 Poetry 管理依赖，用 JSON 文本文件保存每日评分数据。

## 运行

```bash
poetry install --no-root
poetry run python manage.py runserver 127.0.0.1:8000
```

打开：

```text
http://127.0.0.1:8000/
```

## 数据文件

评分数据存放在：

```text
data/daily_scores.txt
```

文件扩展名是 `.txt`，内容格式是 JSON。Django 会直接读取和写入这个文件，不使用数据库。

## API

读取全部评分数据：

```bash
curl http://127.0.0.1:8000/api/daily-scores/
```

新增或覆盖某一天记录：

```bash
curl -X POST http://127.0.0.1:8000/api/daily-scores/records/ \
  -H 'Content-Type: application/json' \
  -d '{
    "date": "2026-06-28",
    "score": {
      "long_term_growth": 21,
      "survival_progress": 10,
      "project_progress": 11,
      "health": 7,
      "self_management": 8,
      "thinking_upgrade": 8,
      "emotion": 5
    },
    "multiplier": 4,
    "confidence": 0.81,
    "summary": "当天总结。"
  }'
```

后端会自动计算 `total` 和 `grade`，同日期记录会被覆盖。

## 表单规则

页面里的 `New Entry` 表单只需要手动填写真正需要判断的内容：

- 手动填写：7 个 `score` 分项、`summary`
- 自动填充：`date`
- 自动计算：`total`、`grade`、`multiplier`、`confidence`

后端会重新计算自动字段，即使 API 请求传入了这些字段，也不会直接信任客户端值。
