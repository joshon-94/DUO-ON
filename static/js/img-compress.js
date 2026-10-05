// 업로드 전 이미지 자동 압축
// - 서버리스(Vercel) 요청 본문 제한(4.5MB) 대응: 큰 사진을 브라우저에서 줄여서 전송
// - 긴 변 1600px, JPEG 품질 0.82. 압축 실패(HEIC 등 디코딩 불가) 시 원본 유지
(function () {
  var MAX_DIM = 1600;
  var QUALITY = 0.82;
  var SKIP_BELOW = 700 * 1024; // 700KB 이하는 그대로 둠

  function compressFile(file) {
    return new Promise(function (resolve) {
      if (!/^image\//.test(file.type) || file.type === "image/gif" || file.size < SKIP_BELOW) {
        return resolve(file);
      }
      var url = URL.createObjectURL(file);
      var img = new Image();
      img.onload = function () {
        try {
          var w = img.naturalWidth, h = img.naturalHeight;
          var scale = Math.min(1, MAX_DIM / Math.max(w, h));
          var canvas = document.createElement("canvas");
          canvas.width = Math.round(w * scale);
          canvas.height = Math.round(h * scale);
          canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
          canvas.toBlob(function (blob) {
            URL.revokeObjectURL(url);
            if (blob && blob.size < file.size) {
              var name = file.name.replace(/\.[^.]+$/, "") + ".jpg";
              resolve(new File([blob], name, { type: "image/jpeg" }));
            } else {
              resolve(file);
            }
          }, "image/jpeg", QUALITY);
        } catch (e) {
          URL.revokeObjectURL(url);
          resolve(file);
        }
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        resolve(file);
      };
      img.src = url;
    });
  }

  document.addEventListener("change", function (e) {
    var input = e.target;
    if (!input || input.type !== "file" || !/image/.test(input.accept || "")) return;
    if (!input.files || !input.files.length || input.dataset.compressing) return;

    var originals = Array.prototype.slice.call(input.files);
    input.dataset.compressing = "1";
    Promise.all(originals.map(compressFile)).then(function (files) {
      try {
        var dt = new DataTransfer();
        files.forEach(function (f) { dt.items.add(f); });
        input.files = dt.files;
      } catch (err) { /* 미지원 브라우저는 원본 전송 */ }
      delete input.dataset.compressing;
    });
  }, true);
})();
