import { invoke } from "@tauri-apps/api/core";

type CheckResult = {
  installed: boolean;
  version?: string;
  config_path?: string;
};

type Preview = {
  config_path: string;
  backup_path: string;
  changes: string[];
};

function $(sel: string) {
  const el = document.querySelector(sel);
  if (!el) throw new Error(`Missing element: ${sel}`);
  return el as HTMLElement;
}

function getInputs() {
  const telegramBotToken = (document.querySelector(
    "#telegram-token"
  ) as HTMLInputElement).value.trim();
  const openaiApiKey = (document.querySelector("#openai-key") as HTMLInputElement)
    .value.trim();
  return { telegramBotToken, openaiApiKey };
}

function setPre(id: string, obj: unknown) {
  $(id).textContent =
    typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
}

async function check() {
  setPre("#check-result", "檢查中…");
  const res = (await invoke("check_openclaw")) as CheckResult;
  setPre("#check-result", res);
}

async function testButton() {
  console.log("testButton clicked!");
  alert("✅ 測試成功！\n\nJavaScript 綁定正常，按鈕可以執行。");
  setPre("#check-result", "✅ 測試按鈕執行成功（JS 綁定正常）");
}

async function install() {
  console.log("install button clicked!");
  
  const ok = confirm(
    "將開始安裝 OpenClaw（包含 Homebrew/Node 等依賴）。\n\n過程中 macOS 會跳出管理員密碼授權視窗，請輸入密碼。\n\n安裝可能需要 10–30 分鐘，請勿關閉視窗。"
  );
  
  console.log("confirm result:", ok);
  if (!ok) {
    setPre("#check-result", "安裝已取消");
    return;
  }

  setPre("#check-result", "正在啟動安裝程序…\n\n請留意：macOS 會跳出「密碼授權」視窗。\n若視窗未出現，請檢查 Dock 或點擊本 app 圖示。\n\n⏳ 請稍候，安裝可能需要 10–30 分鐘…");
  
  console.log("calling install_openclaw...");
  try {
    const out = (await invoke("install_openclaw")) as string;
    console.log("install_openclaw result:", out);
    setPre("#check-result", out || "安裝完成！\n\n請按「檢查 OpenClaw」驗證安裝結果。");
  } catch (e) {
    console.error("install_openclaw error:", e);
    setPre("#check-result", `❌ 安裝失敗：\n\n${String(e)}\n\n常見原因：\n• 取消了密碼授權\n• 帳號不是管理員\n• 網路連線問題\n\n請點「複製安裝指令」使用手動安裝。`);
  }
}

function copyInstallCommand() {
  console.log("copyInstallCommand clicked!");
  const cmd = '/bin/bash -c "$(curl -fsSL https://openclaw.ai/install.sh)"';
  
  // Copy to clipboard using Tauri clipboard API or fallback
  navigator.clipboard.writeText(cmd).then(() => {
    alert("✅ 已複製安裝指令到剪貼簿！\n\n下一步：\n1. 打開「終端機」(Terminal)\n2. 按 Command+V 貼上\n3. 按 Enter\n4. 輸入密碼");
    setPre("#check-result", `✅ 已複製安裝指令！\n\n請打開 Terminal 貼上執行：\n${cmd}\n\n完成後回到此畫面按「檢查 OpenClaw」驗證。`);
  }).catch((e) => {
    console.error("clipboard write failed:", e);
    setPre("#check-result", `請手動複製以下指令：\n\n${cmd}\n\n然後在 Terminal 執行。`);
  });
}

async function preview() {
  const { telegramBotToken, openaiApiKey } = getInputs();
  if (!telegramBotToken || !openaiApiKey) {
    setPre("#preview", "請先填 Telegram Bot Token 與 OpenAI API Key");
    return;
  }
  const res = (await invoke("preview_apply", {
    input: {
      telegram_bot_token: telegramBotToken,
      openai_api_key: openaiApiKey,
    },
  })) as Preview;
  setPre("#preview", res);
}

async function apply() {
  const { telegramBotToken, openaiApiKey } = getInputs();
  if (!telegramBotToken || !openaiApiKey) {
    setPre("#preview", "請先填 Telegram Bot Token 與 OpenAI API Key");
    return;
  }
  const res = (await invoke("apply_config", {
    input: {
      telegram_bot_token: telegramBotToken,
      openai_api_key: openaiApiKey,
    },
  })) as Preview;
  setPre("#preview", res);
}

async function status() {
  setPre("#status-out", "執行中…");
  const out = (await invoke("run_status")) as string;
  setPre("#status-out", out);
}

async function startGateway() {
  const ok = confirm(
    "確定要啟動 gateway 嗎？\n\n這會在背景啟動 OpenClaw Gateway 服務。"
  );
  if (!ok) return;
  setPre("#status-out", "啟動 gateway 中…");
  const out = (await invoke("start_gateway_confirmed")) as string;
  setPre("#status-out", out || "gateway start: OK");
}

window.addEventListener("DOMContentLoaded", () => {
  console.log("DOMContentLoaded event fired");
  
  (document.querySelector("#btn-check") as HTMLButtonElement).onclick = () => {
    console.log("#btn-check clicked");
    check().catch((e) => setPre("#check-result", String(e)));
  };

  (document.querySelector("#btn-test") as HTMLButtonElement).onclick = () => {
    console.log("#btn-test clicked");
    testButton();
  };

  (document.querySelector("#btn-install") as HTMLButtonElement).onclick = () => {
    console.log("#btn-install clicked");
    install().catch((e) => setPre("#check-result", String(e)));
  };

  (document.querySelector("#btn-copy-install") as HTMLButtonElement).onclick = () => {
    console.log("#btn-copy-install clicked");
    copyInstallCommand();
  };

  (document.querySelector("#btn-preview") as HTMLButtonElement).onclick = () =>
    preview().catch((e) => setPre("#preview", String(e)));

  (document.querySelector("#btn-apply") as HTMLButtonElement).onclick = () =>
    apply().catch((e) => setPre("#preview", String(e)));

  (document.querySelector("#btn-status") as HTMLButtonElement).onclick = () =>
    status().catch((e) => setPre("#status-out", String(e)));

  (document.querySelector("#btn-start-gateway") as HTMLButtonElement).onclick =
    () => startGateway().catch((e) => setPre("#status-out", String(e)));
  
  console.log("All event listeners attached");
});
