(() => {
  // ponytail: deters passive scraping; use server-side checks against targeted bots.
  const contacts = {
    email: [124, 115, 122, 120, 97, 121, 45, 111, 118, 104, 112, 92, 124, 100, 126, 82, 64, 73, 76, 82, 86, 77, 78, 81, 7, 73, 68, 65],
    github: [121, 102, 103, 100, 102, 44, 56, 55, 126, 115, 111, 116, 104, 124, 49, 67, 78, 79, 12, 69, 95, 71, 85, 73, 66, 69, 93, 95, 70, 71, 86],
    linkedin: [121, 102, 103, 100, 102, 44, 56, 55, 117, 115, 117, 119, 120, 122, 118, 78, 15, 65, 76, 73, 10, 79, 73, 7, 72, 80, 74, 94, 76, 69, 64, 70, 66, 89, 90, 77],
  };

  function reveal(link) {
    const href = contacts[link.dataset.contact]
      .map((code, index) => String.fromCharCode(code ^ (index + 17)))
      .join("");
    link.href = href;
    if (link.hasAttribute("data-contact-text")) {
      link.textContent = href.replace(/^(mailto:|https:\/\/)/, "");
    }
    link.removeAttribute("data-contact");
  }

  function revealFromInteraction(event) {
    if (!event.isTrusted) return;
    const link = event.target.closest?.("a[data-contact]");
    if (link) reveal(link);
  }

  for (const type of ["pointerover", "pointerdown", "keydown", "click", "contextmenu"]) {
    document.addEventListener(type, revealFromInteraction);
  }

  addEventListener("beforeprint", event => {
    if (!event.isTrusted) return;
    document.querySelectorAll("a[data-contact]").forEach(reveal);
  });
})();
