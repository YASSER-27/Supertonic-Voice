// Supertonic Voice - Content Script
let currentUtterance = null;

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "speak") {
    speakText(msg.text);
  } else if (msg.action === "sendToApp") {
    sendToDesktopApp(msg.text);
  } else if (msg.action === "stopSpeaking") {
    window.speechSynthesis.cancel();
    hideNotification();
  }
});

function speakText(text) {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;

  // Try to find a good voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => v.name.includes("Microsoft") && v.lang.startsWith("en")) || voices[0];
  if (preferred) utterance.voice = preferred;

  utterance.onstart = () => showNotification("🔊 Playing...", true);
  utterance.onend = () => hideNotification();
  utterance.onerror = () => hideNotification();

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

function sendToDesktopApp(text) {
  // Copy with prefix so the desktop app can detect it
  const prefixed = "SUPERTONIC_TTS:" + text;
  navigator.clipboard.writeText(prefixed).then(() => {
    showNotification("✅ Sent to Supertonic Voice!", false);
    setTimeout(hideNotification, 2500);
  }).catch(() => {
    // Fallback
    const ta = document.createElement("textarea");
    ta.value = prefixed;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    showNotification("✅ Sent to Supertonic Voice!", false);
    setTimeout(hideNotification, 2500);
  });
}

function showNotification(message, showStop) {
  hideNotification();
  const el = document.createElement("div");
  el.id = "supertonic-notification";
  el.innerHTML = `
    <span>${message}</span>
    ${showStop ? '<button id="supertonic-stop-btn">⏹ Stop</button>' : ''}
  `;
  document.body.appendChild(el);

  if (showStop) {
    const btn = document.getElementById("supertonic-stop-btn");
    if (btn) {
      btn.addEventListener("click", () => {
        window.speechSynthesis.cancel();
        hideNotification();
      });
    }
  }
}

function hideNotification() {
  const el = document.getElementById("supertonic-notification");
  if (el) el.remove();
}
