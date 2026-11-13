// Simple lightbox for artwork images.
(function () {
  var box = document.getElementById("lightbox");
  if (!box) return;
  var img = box.querySelector("img");
  var items = [], index = 0, opener = null;

  function show(i) {
    index = (i + items.length) % items.length;
    img.src = items[index].getAttribute("data-full");
    var multi = items.length > 1;
    box.querySelector(".lb-prev").hidden = !multi;
    box.querySelector(".lb-next").hidden = !multi;
  }
  function open(el) {
    items = Array.prototype.slice.call(document.querySelectorAll('[data-group="' + el.getAttribute("data-group") + '"]'));
    opener = el;
    box.hidden = false;
    document.body.style.overflow = "hidden";
    show(items.indexOf(el));
    box.querySelector(".lb-close").focus();
  }
  function close() {
    box.hidden = true;
    img.removeAttribute("src");
    document.body.style.overflow = "";
    if (opener) opener.focus();
  }

  document.addEventListener("click", function (e) {
    var z = e.target.closest("[data-full]");
    if (z) { e.preventDefault(); open(z); }
  });
  box.addEventListener("click", function (e) {
    if (e.target.closest(".lb-prev")) show(index - 1);
    else if (e.target.closest(".lb-next")) show(index + 1);
    else if (e.target !== img) close();
  });
  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(index - 1);
    if (e.key === "ArrowRight") show(index + 1);
  });
})();
