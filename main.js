// main.js
document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("version");
  // 初回読み込み
  loadAndRender(sel.value);
  // 切り替え時も再読込
  sel.addEventListener("change", () => loadAndRender(sel.value));
});

function loadAndRender(ver) {
  const yamlPath = `data/${ver}.yaml`;
  const audioDir = ver;       // ver1/ または ver2/
  const prefix   = "en_";     // 音声ファイル共通

  fetch(yamlPath)
    .then(res => {
      if (!res.ok) throw new Error(`${yamlPath} が見つかりません`);
      return res.text();
    })
    .then(yamlText => {
      const examples = jsyaml.load(yamlText);
      renderExamples(examples, audioDir, prefix);
    })
    .catch(err => {
      console.error("読み込みエラー:", err);
      document.getElementById("examples").innerHTML =
        `<p class="error">データの読み込みに失敗しました: ${err.message}</p>`;
    });
}

function renderExamples(examples, audioDir, voicePrefix) {
  const container = document.getElementById("examples");
  container.innerHTML = "";  // クリア

  examples.forEach((ex, i) => {
    const idx = String(i + 1).padStart(3, "0");
    const mp3Path = `${audioDir}/${voicePrefix}${idx}.mp3`;

    const pair = document.createElement("div");
    pair.classList.add("example-pair");

    // 英文＋音声
    const eng = document.createElement("div");
    eng.classList.add("english");
    eng.innerHTML = `<span class="number">${i + 1}.</span> ${ex.english}`;
    // 音声ファイルの存在チェックは省略／常に表示する場合はコメントアウト可
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.preload = "none";
    audio.innerHTML = `<source src="${mp3Path}" type="audio/mpeg">`;
    eng.appendChild(audio);
    pair.appendChild(eng);

    // 日本語訳
    const jp = document.createElement("div");
    jp.classList.add("japanese");
    jp.textContent = ex.japanese;
    pair.appendChild(jp);

    container.appendChild(pair);
  });
}
