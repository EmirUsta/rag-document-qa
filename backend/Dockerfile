FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 poppler-utils build-essential curl libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# torch + torchvision'un CPU-only wheel'leri acikca ve ayni indeksten birlikte
# kuruluyor (ayri bir katmanda). torchvision'i birlikte kurmazsak,
# unstructured[pdf] -> unstructured_inference -> timm zinciri torchvision'i
# kendi (varsayilan PyPI) indeksinden ceker ve bizim CPU torch'umuzla ABI
# uyumsuzlugu yaratir ("operator torchvision::nms does not exist"). Ayri
# katmanda olmasi, requirements.txt degistiginde torch/torchvision'in
# yeniden indirilmesini onler (build cache).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision

COPY requirements.txt .
# --mount=type=cache: pip'in indirdigi wheel'ler imaj katmanina DAHIL OLMAYAN
# kalici bir BuildKit cache'inde tutulur - Dockerfile degisip katman gecersiz
# olsa bile daha once inen paketler internetten tekrar cekilmez, imaj boyutu
# da sismez (--no-cache-dir'in aksine).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .
RUN python -c "import nltk; nltk.download('punkt_tab')"

# ENV bloğu bilerek EN SONDA: bu satırlar değişince yukarıdaki ağır
# apt/pip katmanları (torch dahil) YENİDEN İNMESİN diye - Docker layer
# cache'i sıralı çalışır, erken bir katman değişirse sonrakiler de
# geçersiz olur, ama tersi (sondaki değişir, öncekiler etkilenmez) sorun
# değil.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=4 \
    TOKENIZERS_PARALLELISM=false \
    HF_HOME=/app/.cache/huggingface

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
