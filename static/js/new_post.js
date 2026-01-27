// Preview selected media for new post
"use strict";

function previewMedia(event) {
  const file = event.target.files[0];
  if (!file) return;

  const img = document.getElementById("imagePreview");
  const video = document.getElementById("videoPreview");

  img.classList.add("d-none");
  video.classList.add("d-none");

  const url = URL.createObjectURL(file);

  if (file.type.startsWith("image")) {
    img.src = url;
    img.classList.remove("d-none");
  } else if (file.type.startsWith("video")) {
    video.src = url;
    video.classList.remove("d-none");
  }
}
