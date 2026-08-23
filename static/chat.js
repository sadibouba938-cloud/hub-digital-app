/**
 * Hub Digital — Widget de chat « Hub Digital IA »
 * Gère le widget flottant (#chat-widget) et la boîte intégrée (#chatbox).
 * Appelle l'API /api/chat du backend.
 */
(function () {
  "use strict";

  function container(id) {
    return document.getElementById(id);
  }

  function msgEl(cls, text) {
    var d = document.createElement("div");
    d.className = "message " + cls;
    d.textContent = text;
    return d;
  }

  function append(box, cls, text) {
    box.appendChild(msgEl(cls, text));
    box.scrollTop = box.scrollHeight;
  }

  function welcome() {
    var w = container("chat-window");
    if (w && !w.dataset.welcomed) {
      w.dataset.welcomed = "1";
      append(w, "agent", "Bonjour 👋 Je suis Hub Digital IA. Posez-moi une question sur nos services, notre boutique ou nos contacts !");
    }
  }

  window.sendMessage = function () {
    var input = container("chat-input");
    var inlineInput = container("userInput");
    var message = "";
    var box = null;
    var field = null;

    if (input && input.value.trim()) {
      message = input.value.trim();
      box = container("chat-window");
      field = input;
    } else if (inlineInput && inlineInput.value.trim()) {
      message = inlineInput.value.trim();
      box = container("response");
      field = inlineInput;
    }

    if (!message || !box) return;

    append(box, "user", message);
    field.value = "";

    var typing = msgEl("agent", "…");
    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;

    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (d) {
        typing.textContent = d.reply || "Désolé, je n'ai pas de réponse pour le moment.";
      })
      .catch(function (e) {
        typing.textContent = "⚠️ Impossible de joindre l'assistant (" + e.message + "). Réessayez.";
      })
      .then(function () {
        box.scrollTop = box.scrollHeight;
      });
  };

  /* Envoi avec la touche Entrée */
  ["chat-input", "userInput"].forEach(function (id) {
    var el = container(id);
    if (el) {
      el.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          window.sendMessage();
        }
      });
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", welcome);
  } else {
    welcome();
  }
})();
