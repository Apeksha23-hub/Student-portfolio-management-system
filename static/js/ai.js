/*
 * "Improve with AI" / "Generate summary" buttons.
 * The AI reply is only a suggestion: "Use this" copies it into the form,
 * and it is saved to the database only when the student clicks Save.
 */
(function () {
  var csrfInput = document.querySelector('input[name="csrf_token"]');
  var BUSY = "AI is busy, please try again later.";

  document.querySelectorAll("[data-ai-panel]").forEach(function (panel) {
    var runButton = panel.querySelector("[data-ai-run]");
    var box = panel.querySelector("[data-ai-suggestion]");
    var suggestion = panel.querySelector("[data-ai-text]");
    var status = panel.querySelector("[data-ai-status]");
    var target = document.getElementById(panel.dataset.target);

    function showStatus(text, isError) {
      status.textContent = text;
      status.className = "text-xs " + (isError ? "text-rose-700" : "text-slate-600");
    }

    runButton.addEventListener("click", function () {
      // Collect only the fields this action needs from the form.
      var payload = { kind: panel.dataset.kind };
      panel.dataset.fields.split(",").filter(Boolean).forEach(function (id) {
        var input = document.getElementById(id);
        payload[id] = input ? input.value : "";
      });

      var label = runButton.textContent;
      runButton.disabled = true;
      runButton.textContent = "Thinking...";
      showStatus("", false);

      fetch(panel.dataset.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfInput ? csrfInput.value : "" },
        body: JSON.stringify(payload),
      })
        .then(function (response) { return response.json(); })
        .then(function (data) {
          var text = data.message || "";
          if (data.ok) {
            suggestion.value = data.suggestion;
            box.classList.remove("hidden");
            text = "Review the suggestion below.";
          }
          if (typeof data.remaining === "number") {
            text += " " + data.remaining + " AI actions left today.";
          }
          showStatus(text.trim(), !data.ok);
        })
        .catch(function () { showStatus(BUSY, true); })
        .finally(function () {
          runButton.disabled = false;
          runButton.textContent = label;
        });
    });

    panel.querySelector("[data-ai-accept]").addEventListener("click", function () {
      target.value = suggestion.value.trim();
      box.classList.add("hidden");
      showStatus("Copied into the form. Click Save to keep it.", false);
      target.focus();
    });

    panel.querySelector("[data-ai-discard]").addEventListener("click", function () {
      box.classList.add("hidden");
      showStatus("", false);
    });
  });
})();
