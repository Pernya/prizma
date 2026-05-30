const form = document.querySelector("#job-form");
const fileInput = document.querySelector("#image-input");
const fileName = document.querySelector("#file-name");
const styleSelect = document.querySelector("#style-select");
const submitButton = document.querySelector("#submit-button");
const statusDot = document.querySelector("#status-dot");
const statusText = document.querySelector("#status-text");
const resultImage = document.querySelector("#result-image");
const emptyState = document.querySelector("#empty-state");

const setStatus = (message, state = "idle") => {
  statusText.textContent = message;
  statusDot.className = `status-dot ${state}`;
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const loadStyles = async () => {
  const response = await fetch("/api/v1/styles");
  if (!response.ok) {
    throw new Error("API недоступен");
  }

  const styles = await response.json();
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
  for (let attempt = 0; attempt < 45; attempt += 1) {
    const response = await fetch(statusUrl);
    if (!response.ok) {
      throw new Error("Не удалось получить статус задачи");
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

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  resultImage.hidden = true;
  emptyState.hidden = false;

  try {
    setStatus("Отправляю изображение...", "ready");
    const formData = new FormData(form);
    const response = await fetch("/api/v1/jobs", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Не удалось создать задачу");
    }

    const created = await response.json();
    const job = await waitForJob(created.status_url);
    resultImage.src = `${job.result_url}?t=${Date.now()}`;
    resultImage.hidden = false;
    emptyState.hidden = true;
    setStatus("Готово", "ready");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

loadStyles().catch((error) => {
  setStatus(error.message, "error");
});
