/*
Paradisio View Modes — Tourist, Business Owner, Premium, God's Eye
Activate: ?mode=tourist|biz|premium|god
Stored in: localStorage
*/
(function () {
    var MODES = {
        tourist: { label: "Tourist", icon: "🌴" },
        biz: { label: "Business Owner", icon: "🏪" },
        premium: { label: "Premium Owner", icon: "⭐" },
        god: { label: "Admin", icon: "👁" },
    };

    var currentMode = localStorage.getItem("paradisio_mode") || "tourist";

    function setMode(mode) {
        if (!MODES[mode]) return;
        currentMode = mode;
        localStorage.setItem("paradisio_mode", mode);
        applyMode(mode);
        document.dispatchEvent(new CustomEvent("modechange", { detail: { mode: mode } }));
    }

    function applyMode(mode) {
        document.documentElement.setAttribute("data-mode", mode);
        document.querySelectorAll("[data-show-mode]").forEach(function (el) {
            var allowed = el.getAttribute("data-show-mode").split(",");
            el.style.display = allowed.includes(mode) ? "" : "none";
        });
        document.querySelectorAll("[data-hide-mode]").forEach(function (el) {
            var hidden = el.getAttribute("data-hide-mode").split(",");
            el.style.display = hidden.includes(mode) ? "none" : "";
        });
    }

    // Build the mode switcher badge
    function buildSwitcher() {
        var div = document.createElement("div");
        div.id = "mode-switcher";
        div.style.cssText =
            "position:fixed;bottom:12px;right:12px;z-index:9999;" +
            "background:var(--surface-raised,#fff);border:1px solid var(--sand-100,#efe4d0);" +
            "border-radius:8px;padding:6px 12px;font-size:0.8em;box-shadow:0 2px 8px rgba(0,0,0,0.1);" +
            "display:flex;align-items:center;gap:8px;cursor:pointer;";

        var label = document.createElement("span");
        label.id = "mode-label";
        label.textContent = MODES[currentMode].label;

        var select = document.createElement("select");
        select.style.cssText = "font-size:0.85em;border:1px solid var(--sand-100);border-radius:4px;padding:2px 4px;";
        for (var key in MODES) {
            var opt = document.createElement("option");
            opt.value = key;
            opt.textContent = MODES[key].label;
            if (key === currentMode) opt.selected = true;
            select.appendChild(opt);
        }
        select.addEventListener("change", function (e) {
            setMode(e.target.value);
            label.textContent = MODES[e.target.value].label;
        });

        div.appendChild(label);
        div.appendChild(select);
        document.body.appendChild(div);
    }

    // Check URL parameter for mode override
    var params = new URLSearchParams(window.location.search);
    var urlMode = params.get("mode");
    if (urlMode && MODES[urlMode]) {
        setMode(urlMode);
    }

    // Apply mode on load
    document.addEventListener("DOMContentLoaded", function () {
        applyMode(currentMode);
        buildSwitcher();
    });

    // Also apply immediately if DOM already loaded
    if (document.readyState === "complete" || document.readyState === "interactive") {
        applyMode(currentMode);
        buildSwitcher();
    }

    window.setParadisioMode = setMode;
    window.getParadisioMode = function () { return currentMode; };
})();
