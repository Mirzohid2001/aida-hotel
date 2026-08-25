/**
 * Compress image file inputs in Django admin before upload.
 * Speeds up slow/failed uploads of multi‑MB phone photos.
 */
(function () {
  const MAX_SIDE = 1920;
  const JPEG_QUALITY = 0.82;
  const MIN_BYTES_TO_COMPRESS = 450 * 1024;

  function loadImage(file) {
    return new Promise(function (resolve, reject) {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("image load failed"));
      };
      img.src = url;
    });
  }

  async function compressFile(file) {
    if (!file || !file.type || !file.type.startsWith("image/")) return file;
    if (file.type === "image/svg+xml") return file;
    if (file.size < MIN_BYTES_TO_COMPRESS) return file;

    const img = await loadImage(file);
    let w = img.naturalWidth || img.width;
    let h = img.naturalHeight || img.height;
    const longest = Math.max(w, h);
    if (longest > MAX_SIDE) {
      const ratio = MAX_SIDE / longest;
      w = Math.max(1, Math.round(w * ratio));
      h = Math.max(1, Math.round(h * ratio));
    }

    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, w, h);

    const blob = await new Promise(function (resolve) {
      canvas.toBlob(resolve, "image/jpeg", JPEG_QUALITY);
    });
    if (!blob || blob.size >= file.size) return file;

    const base = (file.name || "image").replace(/\.[^.]+$/, "");
    return new File([blob], base + ".jpg", {
      type: "image/jpeg",
      lastModified: Date.now(),
    });
  }

  async function onFileChange(event) {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || input.type !== "file") return;
    if (!input.files || !input.files.length) return;
    if (input.dataset.aidaCompressing === "1") return;

    const files = Array.from(input.files);
    const needsWork = files.some(function (f) {
      return f.type.startsWith("image/") && f.size >= MIN_BYTES_TO_COMPRESS;
    });
    if (!needsWork) return;

    input.dataset.aidaCompressing = "1";
    input.disabled = true;
    try {
      const compressed = [];
      for (const file of files) {
        compressed.push(await compressFile(file));
      }
      const dt = new DataTransfer();
      compressed.forEach(function (f) {
        dt.items.add(f);
      });
      input.files = dt.files;
    } catch (err) {
      console.warn("Aida image compress skipped:", err);
    } finally {
      input.disabled = false;
      delete input.dataset.aidaCompressing;
    }
  }

  document.addEventListener("change", onFileChange, true);
})();
