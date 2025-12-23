// Load Navbar and Footer (and then configure UI)
function loadComponent(url, placeholderId, callback) {
  fetch(url)
    .then(resp => resp.text())
    .then(html => {
      document.getElementById(placeholderId).innerHTML = html;
      if (typeof callback === "function") callback();
    })
    .catch(err => console.error("Failed loading component:", url, err));
}

// load components
document.addEventListener("DOMContentLoaded", () => {
  loadComponent("components/navbar.html", "navbar-placeholder", setupRoleUI);
  loadComponent("components/footer.html", "footer-placeholder");
  startTypingEffect(); // optional: kick off typing animation if present
  attachStockFormHandler();
});

/* ---------------------------
   Role-based UI (frontend-only)
   ---------------------------
   For development/testing use:
   localStorage.setItem('role','admin')   // show admin UI
   localStorage.setItem('role','user')    // hide admin UI
   localStorage.removeItem('role')        // guest
*/
function setupRoleUI() {
  const role = (localStorage.getItem("role") || "user").toLowerCase();

  // Show/hide admin-only elements
  document.querySelectorAll(".admin-only").forEach(el => {
    el.style.display = (role === "admin") ? "" : "none";
  });

  // Update Auth link text for demo convenience
  const authLink = document.getElementById("auth-link");
  if (authLink) {
    if (role === "admin" || role === "user") {
      authLink.textContent = "Logout";
      authLink.href = "#";
      authLink.addEventListener("click", (e) => {
        e.preventDefault();
        localStorage.removeItem("role");
        // reload to apply UI changes (in a real app you'd call logout endpoint)
        location.reload();
      });
    } else {
      authLink.textContent = "Login";
      authLink.href = "login.html";
    }
  }

  // ensure admin cannot toggle donor on admin pages (visual only)
  document.querySelectorAll(".donor-switch input[disabled]").forEach(inp => {
    // already disabled in markup — nothing to do; kept for clarity
    inp.closest('.donor-switch')?.classList.add('donor-disabled');
  });
}

/* ---------------------------
   Stock form dummy handler (existing)
   --------------------------- */
function attachStockFormHandler() {
  const forms = document.querySelectorAll("#stockForm");
  if (forms.length) {
    forms.forEach(stockForm => {
      stockForm.addEventListener("submit", function (e) {
        e.preventDefault();
        alert("Stock added/updated (frontend only)");
        stockForm.reset();
      });
    });
  }
}

/* ---------------------------
   Typing effect (moved to a function)
   --------------------------- */
const phrases = ["Welcome To RedConnect", "Your blood is precious, share it.", "Real heroes bleed voluntarily."];

function startTypingEffect() {
  const dynamicText = document.querySelector('span.typing-effect');
  if (!dynamicText) return;
  let phraseIndex = 0;
  let letterIndex = 0;

  function printLetters(phrase) {
    if (letterIndex == phrase.length) {
      setTimeout(clearLetters, 1500);
    } else if (letterIndex < phrase.length) {
      dynamicText.textContent += phrase.charAt(letterIndex);
      letterIndex += 1;
      setTimeout(function () { printLetters(phrase) }, 100);
    }
  }

  function clearLetters() {
    if (letterIndex == -1) {
      phraseIndex = (phraseIndex + 1) % phrases.length;
      letterIndex = 0;
      setTimeout(function () { printLetters(phrases[phraseIndex]) }, 500);
    } else if (letterIndex > -1) {
      dynamicText.textContent = phrases[phraseIndex].substring(0, letterIndex);
      letterIndex -= 1;
      setTimeout(clearLetters, 50);
    }
  }

  printLetters(phrases[0]);
}


