# AGENT.md

## Project

- Name: `なんでもショートカット`
- Type: Python desktop app for Windows
- Entry point: `main.py`
- Build target: `dist/NandemoShortcut.exe`
- GitHub: `https://github.com/YujiFukami/NandemoShortCut.git`
- Default branch: `main`

## Current Status

- Global hotkey launcher works with combo hotkeys via `keyboard.add_hotkey()`
- Overlay can open settings by `S` key and by `設定` button
- Settings screen supports:
  - action add/edit/delete
  - category add
  - hotkey capture dialog by actual keyboard input
  - startup enable/disable
- Added action type: `open_path`
- Added single-instance guard to prevent double launch of the EXE
- README added with logo and usage guide
- Initial public `config.json` restored
- Hotkey diagnostics were added for troubleshooting combo/special keys
- Startup registration now uses Windows Task Scheduler with highest privileges
- Startup registration falls back to UAC elevation when normal registration is denied

## Important Files

- `main.py`: app bootstrap and single-instance guard
- `config_manager.py`: config loading/saving and action tree
- `action_executor.py`: action implementations
- `hotkey_listener.py`: global hotkey registration
- `overlay_window.py`: overlay UI
- `settings_window.py`: settings UI
- `startup_manager.py`: Windows startup registration
- `README.md`: public documentation
- `debug_hotkey_listener.py`: manual hotkey event probe
- `debug_hotkey_probe.py`: hotkey parse/scan-code probe
- `.gitignore`: excludes local/private/generated files

## Public vs Private Data

- Public `config.json` is committed with safe initial defaults
- Private local settings must not be committed
- Excluded from Git:
  - `開発者用/`
  - `dist/`
  - `build/`
  - `__pycache__/`
  - `オリジナル/`

## Build

```bash
python -m PyInstaller NandemoShortcut.spec --noconfirm
```

## Run in Dev

```bash
python main.py
```

## Recent Work Completed

- Fixed category-add validation path
- Added file open action with file picker
- Added combo hotkey support
- Added startup registration controls
- Added settings access from overlay
- Prevented duplicate app launch
- Built latest EXE and pushed code to GitHub
- Investigated reports that `Pause` / `Ctrl+F1` sometimes fail as activation hotkeys
- Confirmed by runtime logs that `pause` and `ctrl+f1` both register and trigger correctly in the tested environment
- Added `NANDEMO_SHORTCUT_DEBUG_HOTKEY=1` support in `hotkey_listener.py` to print registration details and raw key events
- Added `debug_hotkey_listener.py` and `debug_hotkey_probe.py` for standalone hotkey diagnosis
- Reworked startup registration from Startup folder `.bat` to Task Scheduler `ONLOGON` task with `/RL HIGHEST`
- Added UAC elevation retry for startup registration using `ShellExecuteExW(..., "runas", ...)`
- Built updated EXE successfully: `dist/NandemoShortcut.exe`

## Notes for Next Session

- If rebuilding EXE fails with access denied, close running `NandemoShortcut.exe` first
- EXE runtime config is stored next to the EXE as `config.json`
- If pushing with Git fails due to ownership, ensure repo is marked as `safe.directory`
- Current repo already has `origin` set to GitHub and `main` tracks `origin/main`
- User reported `Pause` / `Ctrl+F1` startup concerns; current diagnostics show no bug in `keyboard` registration itself
- Most likely remaining failure mode is privilege mismatch versus target apps or other software swallowing keys
- To re-run hotkey diagnostics:
  - `set NANDEMO_SHORTCUT_DEBUG_HOTKEY=1`
  - `python main.py`
- To probe outside the app:
  - `python debug_hotkey_listener.py pause`
  - `python debug_hotkey_listener.py ctrl+f1`
- The settings screen startup button should now trigger UAC when needed and register a scheduled task named `NandemoShortcut`
- The latest user-facing verification still needed is testing startup registration behavior from the built EXE after logon

## Likely Next Tasks

- Re-test EXE behavior after recent UX changes
- Verify scheduled-task based startup from the built EXE across reboot/logon
- Decide whether to keep or remove debug helper scripts before release
- Improve README screenshots or add release notes
- Consider adding config reload/import-export features
- Consider moving user config to AppData if EXE-folder write access becomes a problem
