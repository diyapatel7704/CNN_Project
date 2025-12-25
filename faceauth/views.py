import os
import base64
import json
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import ReferenceUploadForm
from .utils import verify_against_db, send_email


def index(request):
    return render(request, "faceauth/index.html")


def upload_reference(request):
    if request.method == "POST":
        form = ReferenceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["person_name"].strip()
            files = request.FILES.getlist("images")

            person_folder = os.path.join(settings.AUTHORIZED_DB, name)
            os.makedirs(person_folder, exist_ok=True)

            for f in files:
                with open(os.path.join(person_folder, f.name), "wb") as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)

            return render(request, "faceauth/result.html", {
                "message": f"Saved {len(files)} images for {name}"
            })
    else:
        form = ReferenceUploadForm()

    return render(request, "faceauth/upload.html", {"form": form})


@csrf_exempt
def verify_image(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        raw_data = request.POST.get("image")
        if raw_data is None:
            body = json.loads(request.body.decode())
            raw_data = body.get("image")

        header, encoded = raw_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)

        live_path = os.path.join(settings.BASE_DIR, "live.jpg")
        with open(live_path, "wb") as f:
            f.write(img_bytes)

        authorized, person, dist = verify_against_db(live_path)

        send_email(authorized, person, live_path)

        return JsonResponse({
            "authorized": authorized,
            "name": person,
            "distance": dist
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
