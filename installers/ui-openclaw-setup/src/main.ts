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

async function install() {
  const ok = confirm(
    "將開始安裝 OpenClaw（包含 Homebrew/Node 等依賴）。\n\n過程中 macOS 會跳出管理員密碼授權視窗，請輸入密碼。\n\n安裝可能需要 10–30 分鐘，請勿關閉視窗。"
  );
  if (!ok) return;

  setPre("#check-result", "安裝中…（請留意是否跳出密碼授權視窗）");
  const out = (await invoke("install_openclaw")) as string;
  setPre("#check-result", out || "安裝完成（請再按一次『檢查 OpenClaw』驗證）");
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
  (document.querySelector("#btn-check") as HTMLButtonElement).onclick = () =>
    check().catch((e) => setPre("#check-result", String(e)));

  (document.querySelector("#btn-install") as HTMLButtonElement).onclick = () =>
    install().catch((e) => setPre("#check-result", String(e)));

  (document.querySelector("#btn-preview") as HTMLButtonElement).onclick = () =>
    preview().catch((e) => setPre("#preview", String(e)));

  (document.querySelector("#btn-apply") as HTMLButtonElement).onclick = () =>
    apply().catch((e) => setPre("#preview", String(e)));

  (document.querySelector("#btn-status") as HTMLButtonElement).onclick = () =>
    status().catch((e) => setPre("#status-out", String(e)));

  (document.querySelector("#btn-start-gateway") as HTMLButtonElement).onclick =
    () => startGateway().catch((e) => setPre("#status-out", String(e)));
});
