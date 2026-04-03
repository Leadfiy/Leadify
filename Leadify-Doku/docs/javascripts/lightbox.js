document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("img").forEach(img => {
    img.style.cursor = "zoom-in";

    img.addEventListener("click", () => {
      const overlay = document.createElement("div");
      overlay.style.position = "fixed";
      overlay.style.top = 0;
      overlay.style.left = 0;
      overlay.style.width = "100%";
      overlay.style.height = "100%";
      overlay.style.backgroundColor = "rgba(0,0,0,0.8)";
      overlay.style.display = "flex";
      overlay.style.alignItems = "center";
      overlay.style.justifyContent = "center";
      overlay.style.zIndex = 9999;

      const fullImg = document.createElement("img");
      fullImg.src = img.src;
      fullImg.style.maxWidth = "90%";
      fullImg.style.maxHeight = "90%";

      overlay.appendChild(fullImg);

      overlay.addEventListener("click", () => {
        document.body.removeChild(overlay);
      });

      document.body.appendChild(overlay);
    });
  });
});