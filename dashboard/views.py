import json

from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .storage import ScoreDataError, load_score_data, save_record


def home(request: HttpRequest):
    return render(
        request,
        "dashboard/home.html",
        {
            "daily_score_data": load_score_data(),
        },
    )


@require_GET
def daily_scores(request: HttpRequest):
    return JsonResponse(load_score_data(), json_dumps_params={"ensure_ascii": False, "indent": 2})


@csrf_exempt
@require_http_methods(["POST"])
def daily_score_records(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        record = save_record(payload)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON body"}, status=400)
    except ScoreDataError as error:
        return JsonResponse({"error": str(error)}, status=400)

    return JsonResponse(record, json_dumps_params={"ensure_ascii": False, "indent": 2})
