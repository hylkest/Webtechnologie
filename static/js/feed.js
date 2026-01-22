// Like button toggle in feed
"use strict";

document.addEventListener("DOMContentLoaded", function () {
  var buttons = document.querySelectorAll(".like-button");

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var postId = button.dataset.postId;

      fetch("/posts/" + postId + "/like", { method: "POST" })
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          var parent = button.closest(".blogpost-actions");
          var countEl = parent ? parent.querySelector(".like-count") : null;
          var label = button.querySelector(".like-label");

          if (data.liked) {
            button.classList.add("liked");
            button.setAttribute("aria-pressed", "1");
            if (label) label.textContent = "Je vindt dit leuk";
          } else {
            button.classList.remove("liked");
            button.setAttribute("aria-pressed", "0");
            if (label) label.textContent = "Vind ik leuk";
          }

          if (countEl) {
            countEl.textContent = data.like_count;
          }
        })
        .catch(function (error) {
          console.error("Like request failed", error);
        });
    });
  });
});
