document.addEventListener("DOMContentLoaded", () => {
  // Simple UX sugar: highlight file name on upload
  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        const hint = document.createElement("div");
        hint.className = "hint";
        hint.textContent = "Selected: " + fileInput.files[0].name;
        fileInput.parentElement.appendChild(hint);
      }
    });
  }
});
