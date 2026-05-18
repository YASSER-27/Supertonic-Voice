// Supertonic Voice - Chrome Extension Service Worker
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "supertonic-play",
    title: "📖 Play with Supertonic Voice",
    contexts: ["selection"]
  });
  chrome.contextMenus.create({
    id: "supertonic-vocal",
    title: "🎙 Send to Supertonic (Voice Message)",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  const selectedText = info.selectionText;
  if (!selectedText) return;

  let action = "";
  if (info.menuItemId === "supertonic-play") {
    action = "read";
  } else if (info.menuItemId === "supertonic-vocal") {
    action = "voice";
  }

  if (action) {
    // Send directly and instantly to the running desktop app via local HTTP port
    fetch("http://127.0.0.1:5003/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ action: action, text: selectedText })
    }).catch(err => {
      console.error("Supertonic Voice App is not running on localhost:5003", err);
    });
  }
});
