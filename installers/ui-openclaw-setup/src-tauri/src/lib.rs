use anyhow::{anyhow, Context, Result};
use chrono::Local;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn openclaw_config_path() -> Result<PathBuf> {
    let home = std::env::var("HOME").context("HOME not set")?;
    Ok(Path::new(&home).join(".openclaw").join("openclaw.json"))
}

fn run_cmd(program: &str, args: &[&str]) -> Result<String> {
    let out = Command::new(program)
        .args(args)
        .output()
        .with_context(|| format!("failed to run {program}"))?;
    let stdout = String::from_utf8_lossy(&out.stdout).to_string();
    let stderr = String::from_utf8_lossy(&out.stderr).to_string();
    if !out.status.success() {
        return Err(anyhow!(
            "command failed: {} {}\n{}",
            program,
            args.join(" "),
            if stderr.is_empty() { stdout } else { stderr }
        ));
    }
    Ok(stdout.trim().to_string())
}

#[derive(Debug, Serialize)]
struct CheckResult {
    installed: bool,
    version: Option<String>,
    config_path: Option<String>,
}

#[tauri::command]
fn check_openclaw() -> Result<CheckResult, String> {
    (|| {
        let config_path = openclaw_config_path().ok();
        match run_cmd("openclaw", &["--version"]) {
            Ok(version) => Ok(CheckResult {
                installed: true,
                version: Some(version),
                config_path: config_path.map(|p| p.display().to_string()),
            }),
            Err(_) => Ok(CheckResult {
                installed: false,
                version: None,
                config_path: config_path.map(|p| p.display().to_string()),
            }),
        }
    })()
    .map_err(|e: anyhow::Error| e.to_string())
}

#[derive(Debug, Deserialize)]
struct ApplyInput {
    telegram_bot_token: String,
    openai_api_key: String,
}

#[derive(Debug, Serialize)]
struct Preview {
    config_path: String,
    backup_path: String,
    changes: Vec<String>,
}

fn compute_backup_path(config_path: &Path) -> PathBuf {
    let ts = Local::now().format("%Y%m%d-%H%M%S");
    let fname = format!("openclaw.json.bak-{ts}");
    config_path.with_file_name(fname)
}

#[tauri::command]
fn preview_apply(_input: ApplyInput) -> Result<Preview, String> {
    (|| {
        let config_path = openclaw_config_path()?;
        let backup_path = compute_backup_path(&config_path);

        let mut changes = vec![
            "Set channels.telegram.botToken".to_string(),
            "Set openai.apiKey".to_string(),
        ];

        // Optional: mention gateway not started
        changes.push("Will NOT start/restart gateway automatically".to_string());

        Ok(Preview {
            config_path: config_path.display().to_string(),
            backup_path: backup_path.display().to_string(),
            changes,
        })
    })()
    .map_err(|e: anyhow::Error| e.to_string())
}

#[tauri::command]
fn apply_config(input: ApplyInput) -> Result<Preview, String> {
    (|| {
        let config_path = openclaw_config_path()?;
        if !config_path.exists() {
            return Err(anyhow!(
                "Config not found at {}. Run 'openclaw setup' first.",
                config_path.display()
            ));
        }

        // Backup first
        let backup_path = compute_backup_path(&config_path);
        fs::copy(&config_path, &backup_path).with_context(|| {
            format!(
                "failed to backup {} -> {}",
                config_path.display(),
                backup_path.display()
            )
        })?;

        // Load JSON
        let raw = fs::read_to_string(&config_path)
            .with_context(|| format!("failed to read {}", config_path.display()))?;
        let mut obj: Value = serde_json::from_str(&raw).context("config is not valid JSON")?;

        // Ensure structure
        set_dot(&mut obj, "channels.telegram.botToken", Value::String(input.telegram_bot_token));
        set_dot(&mut obj, "openai.apiKey", Value::String(input.openai_api_key));

        // Write back
        let out = serde_json::to_string_pretty(&obj)?;
        fs::write(&config_path, out)
            .with_context(|| format!("failed to write {}", config_path.display()))?;

        Ok(Preview {
            config_path: config_path.display().to_string(),
            backup_path: backup_path.display().to_string(),
            changes: vec![
                "Applied channels.telegram.botToken".to_string(),
                "Applied openai.apiKey".to_string(),
                "Gateway NOT started automatically".to_string(),
            ],
        })
    })()
    .map_err(|e: anyhow::Error| e.to_string())
}

fn set_dot(root: &mut Value, path: &str, value: Value) {
    let parts: Vec<&str> = path.split('.').collect();
    let mut cur = root;
    for (i, key) in parts.iter().enumerate() {
        let is_last = i == parts.len() - 1;
        if is_last {
            if let Value::Object(map) = cur {
                map.insert((*key).to_string(), value);
            }
            return;
        }
        // descend / create
        if let Value::Object(map) = cur {
            cur = map
                .entry((*key).to_string())
                .or_insert_with(|| Value::Object(serde_json::Map::new()));
        } else {
            // overwrite non-object
            *cur = Value::Object(serde_json::Map::new());
            if let Value::Object(map) = cur {
                cur = map
                    .entry((*key).to_string())
                    .or_insert_with(|| Value::Object(serde_json::Map::new()));
            }
        }
    }
}

#[tauri::command]
fn run_status() -> Result<String, String> {
    run_cmd("openclaw", &["status"]).map_err(|e| e.to_string())
}

#[tauri::command]
fn start_gateway_confirmed() -> Result<String, String> {
    run_cmd("openclaw", &["gateway", "start"]).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            check_openclaw,
            preview_apply,
            apply_config,
            run_status,
            start_gateway_confirmed
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

