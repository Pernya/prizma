const form = document.querySelector("#job-form");
const fileInput = document.querySelector("#image-input");
const fileName = document.querySelector("#file-name");
const styleSelect = document.querySelector("#style-select");
const submitButton = document.querySelector("#submit-button");
const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const resultImage = document.querySelector("#result-image");
const emptyState = document.querySelector("#empty-state");
const resultActions = document.querySelector("#result-actions");
const downloadLink = document.querySelector("#download-link");
const shareButton = document.querySelector("#share-button");

let currentResultUrl = null;

const setStatus = (message, state = "idle") => {
  statusText.textContent = message;
  statusDot.className = `status-dot ${state}`;
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
const MAX_CLIENT_UPLOAD_BYTES = 2 * 1024 * 1024;
const MAX_CLIENT_IMAGE_SIDE = 1600;
const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

const toLocalApiUrl = (url) => {
  const parsed = new URL(url, window.location.origin);
  return `${parsed.pathname}${parsed.search}`;
};

const readErrorMessage = async (response, fallback) => {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    const payload = await response.json().catch(() => ({}));
    return payload.detail || payload.message || `${fallback} (${response.status})`;
  }

  const text = await response.text().catch(() => "");
  return text.trim() || `${fallback} (${response.status})`;
};

const loadStyles = async () => {
  const response = await fetch("/api/v1/styles");
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "API недоступен"));
  }

  const styles = await response.json();
  if (!styles.length) {
    throw new Error("Backend не вернул список стилей");
  }

  styleSelect.replaceChildren(
    ...styles.map((style) => {
      const option = document.createElement("option");
      option.value = style.name;
      option.textContent = `${style.name} - ${style.description}`;
      return option;
    }),
  );
  setStatus("API готов к обработке", "ready");
};

const waitForJob = async (statusUrl) => {
  const localStatusUrl = toLocalApiUrl(statusUrl);
  for (let attempt = 0; attempt < 45; attempt += 1) {
    const response = await fetch(localStatusUrl);
    if (!response.ok) {
      throw new Error(await readErrorMessage(response, "Не удалось получить статус задачи"));
    }

    const job = await response.json();
    setStatus(`Статус: ${job.status}`, job.status === "failed" ? "error" : "ready");

    if (job.status === "succeeded") {
      return job;
    }

    if (job.status === "failed") {
      throw new Error(job.error || "Обработка завершилась ошибкой");
    }

    await sleep(1200);
  }

  throw new Error("Задача выполняется слишком долго");
};

fileInput.addEventListener("change", () => {
  fileName.textContent = fileInput.files[0]?.name || "PNG, JPEG или WebP до 10 МБ";
});

const canvasToBlob = (canvas, type, quality) =>
  new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
          return;
        }
        reject(new Error("Не удалось подготовить изображение"));
      },
      type,
      quality,
    );
  });

const loadDrawableImage = async (file) => {
  if ("createImageBitmap" in window) {
    const bitmap = await createImageBitmap(file);
    return {
      source: bitmap,
      width: bitmap.width,
      height: bitmap.height,
      cleanup: () => bitmap.close?.(),
    };
  }

  const objectUrl = URL.createObjectURL(file);
  const image = new Image();
  image.decoding = "async";
  await new Promise((resolve, reject) => {
    image.addEventListener("load", resolve, { once: true });
    image.addEventListener("error", () => reject(new Error("Не удалось прочитать изображение")), { once: true });
    image.src = objectUrl;
  });

  return {
    source: image,
    width: image.naturalWidth,
    height: image.naturalHeight,
    cleanup: () => URL.revokeObjectURL(objectUrl),
  };
};

const prepareUploadFile = async (file) => {
  if (file.size <= MAX_CLIENT_UPLOAD_BYTES) {
    return file;
  }

  const image = await loadDrawableImage(file);
  try {
    const scale = Math.min(1, MAX_CLIENT_IMAGE_SIDE / Math.max(image.width, image.height));
    const width = Math.max(1, Math.round(image.width * scale));
    const height = Math.max(1, Math.round(image.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    canvas.getContext("2d").drawImage(image.source, 0, 0, width, height);

    const blob = await canvasToBlob(canvas, "image/jpeg", 0.86);
    const preparedName = `${file.name.replace(/\.[^.]+$/, "") || "image"}-prepared.jpg`;
    return new File([blob], preparedName, {
      type: "image/jpeg",
    });
  } finally {
    image.cleanup();
  }
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  resultImage.hidden = true;
  emptyState.hidden = false;
  resultActions.hidden = true;
  currentResultUrl = null;

  try {
    const selectedFile = fileInput.files[0];
    if (!selectedFile) {
      throw new Error("Выберите изображение");
    }
    if (!ALLOWED_TYPES.has(selectedFile.type)) {
      throw new Error("Поддерживаются только PNG, JPEG и WebP");
    }
    if (selectedFile.size > MAX_UPLOAD_BYTES) {
      throw new Error("Файл больше 10 МБ");
    }

    setStatus("Подготавливаю изображение...", "ready");
    const uploadFile = await prepareUploadFile(selectedFile);
    const formData = new FormData();
    formData.set("style", styleSelect.value);
    formData.set("file", uploadFile, uploadFile.name);

    setStatus("Отправляю изображение...", "ready");
    const response = await fetch("/api/v1/jobs", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(await readErrorMessage(response, "Не удалось создать задачу"));
    }

    const created = await response.json();
    const job = await waitForJob(created.status_url);
    currentResultUrl = `${toLocalApiUrl(job.result_url)}?t=${Date.now()}`;
    resultImage.src = currentResultUrl;
    downloadLink.href = currentResultUrl;
    downloadLink.download = `prizma-${job.job_id}.png`;
    resultImage.hidden = false;
    emptyState.hidden = true;
    resultActions.hidden = false;
    setStatus("Готово", "ready");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

shareButton.addEventListener("click", async () => {
  if (!currentResultUrl) {
    return;
  }

  const absoluteUrl = new URL(currentResultUrl, window.location.origin).href;
  try {
    if (navigator.share) {
      await navigator.share({
        title: "Prizma result",
        text: "Результат обработки в Prizma",
        url: absoluteUrl,
      });
      return;
    }

    await navigator.clipboard.writeText(absoluteUrl);
    setStatus("Ссылка на результат скопирована", "ready");
  } catch (error) {
    const errorName = error instanceof Error ? error.name : "";
    if (errorName !== "AbortError") {
      setStatus("Не удалось поделиться результатом", "error");
    }
  }
});

loadStyles().catch((error) => {
  setStatus(error.message, "error");
});
