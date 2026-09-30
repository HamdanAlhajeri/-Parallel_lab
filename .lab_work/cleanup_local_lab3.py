import argparse
import ctypes
from ctypes import wintypes
import datetime
import json
import os
import pathlib
import re
import sys
import time


sys.dont_write_bytecode = True
WORK = pathlib.Path("C:/Users/Xxthe/OneDrive/Desktop/Cloud_Lab/Lab3/work")
STATE_PATH = WORK / "state.json"
LOG_PATH = WORK / "local_cleanup.json"
KEY_NAME = "Hamdan-Lab3-20260925"
SECRET_NAMES = (
    "Hamdan-Lab3-20260925.pem",
    "Lab3_password.dpapi",
    "Hamdan-Lab3-A.rdp",
    "Hamdan-Lab3-B.rdp",
    "Hamdan-Lab3-C.rdp",
)
WINDOW_TITLE = re.compile(r"(?<![A-Za-z0-9_-])Hamdan-Lab3(?:-[ABC])?(?:\.rdp)?(?=$|[\s.])", re.I)


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_secret_paths():
    temporary = pathlib.Path(os.environ["TEMP"]).resolve()
    directory = (temporary / "Codex_CloudLab_AWS_Secrets").resolve()
    if directory.parent != temporary:
        raise ValueError("The secrets directory does not resolve directly inside TEMP.")
    paths = []
    for name in SECRET_NAMES:
        original = directory / name
        resolved = original.resolve()
        if original.is_symlink() or resolved.parent != directory or resolved.name != name:
            raise ValueError("A secret target resolves outside its exact expected path: " + name)
        if original.exists() and not original.is_file():
            raise ValueError("The expected secret file is not a regular file: " + name)
        paths.append(original)
    return paths


def process_filename(pid):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(buffer))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return None
        return pathlib.Path(buffer.value).name.lower()
    finally:
        kernel32.CloseHandle(handle)


def lab_windows():
    import win32gui
    import win32process

    found = []

    def collect(handle, unused):
        title = win32gui.GetWindowText(handle)
        if not WINDOW_TITLE.search(title):
            return
        if win32gui.GetClassName(handle) != "TscShellContainerClass":
            return
        pid = win32process.GetWindowThreadProcessId(handle)[1]
        if process_filename(pid) == "mstsc.exe":
            found.append({"handle": handle, "title": title, "pid": pid})

    win32gui.EnumWindows(collect, None)
    return found


def clear_clipboard():
    import win32clipboard

    for attempt in range(10):
        try:
            win32clipboard.OpenClipboard()
            break
        except Exception:
            if attempt == 9:
                raise
            time.sleep(0.1)
    try:
        win32clipboard.EmptyClipboard()
    finally:
        win32clipboard.CloseClipboard()


def main():
    parser = argparse.ArgumentParser(description="Remove only the tracked temporary local credentials and files for Lab 3 after verified AWS cleanup.")
    parser.add_argument("--execute", action="store_true", help="Perform cleanup; also requires state.cleanup.aws_verified=true.")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("This helper is for Windows only.")

    state = json.loads(STATE_PATH.read_text(encoding="utf-8-sig"))
    if state.get("key_pair") != KEY_NAME:
        raise ValueError("State does not identify the expected Lab 3 key pair.")
    credentials = state.get("rdp_credentials", [])
    if not isinstance(credentials, list) or not all(isinstance(target, str) and re.fullmatch(r"TERMSRV/[A-Za-z0-9.-]+", target) for target in credentials):
        raise ValueError("Unexpected tracked RDP credential format.")
    credentials = list(dict.fromkeys(credentials))
    files = safe_secret_paths()
    verified = state.get("cleanup", {}).get("aws_verified") is True
    if args.execute and not verified:
        raise ValueError("Refusing cleanup: state.cleanup.aws_verified must be true after AWS cleanup is verified.")
    windows = lab_windows()
    if not args.execute:
        print(json.dumps({
            "mode": "preview only",
            "aws_verified_guard": verified,
            "tracked_generic_credential_targets": credentials,
            "exact_secret_files": [{"name": path.name, "exists": path.is_file()} for path in files],
            "matching_mstsc_windows": windows,
            "clipboard_action": "clear on execution without reading contents",
            "execute_requires": "--execute and state.cleanup.aws_verified=true",
        }, indent=2))
        return 0

    import pywintypes
    import win32con
    import win32cred
    import win32gui

    log = {"started_utc": utc_now(), "aws_verified_guard": True, "credential_results": [], "file_results": [], "window_results": [], "clipboard_cleared": False, "errors": []}
    for window in windows:
        item = {"title": window["title"], "pid": window["pid"], "status": "close_requested"}
        try:
            current = next((item for item in lab_windows() if item["handle"] == window["handle"] and item["pid"] == window["pid"]), None)
            if current:
                win32gui.PostMessage(window["handle"], win32con.WM_CLOSE, 0, 0)
            else:
                item["status"] = "already_absent"
        except Exception as error:
            item["status"] = "error"
            log["errors"].append("Closing " + window["title"] + ": " + type(error).__name__)
        log["window_results"].append(item)
    for attempt in range(15):
        remaining = lab_windows()
        if not remaining:
            break
        time.sleep(0.2)
    remaining_pids = {window["pid"] for window in remaining}
    for item in log["window_results"]:
        if item["status"] == "close_requested":
            item["status"] = "still_open" if item["pid"] in remaining_pids else "closed"
    if remaining:
        log["errors"].append("A matching Lab 3 Remote Desktop window remains open; no unrelated window or process was closed.")

    for target in credentials:
        item = {"target": target, "type": "generic"}
        try:
            win32cred.CredDelete(target, win32cred.CRED_TYPE_GENERIC, 0)
            item["status"] = "removed"
        except pywintypes.error as error:
            code = getattr(error, "winerror", error.args[0] if error.args else None)
            if code == 1168:
                item["status"] = "already_absent"
            else:
                item["status"] = "error"
                item["error_code"] = code
                log["errors"].append("Credential removal failed for " + target + " (code " + str(code) + ").")
        log["credential_results"].append(item)

    for path in safe_secret_paths():
        item = {"name": path.name}
        try:
            if path.exists():
                path.unlink()
                item["status"] = "removed"
            else:
                item["status"] = "already_absent"
        except OSError as error:
            item["status"] = "error"
            item["error_code"] = error.winerror
            log["errors"].append("File removal failed for " + path.name + " (code " + str(error.winerror) + ").")
        log["file_results"].append(item)

    try:
        clear_clipboard()
        log["clipboard_cleared"] = True
    except Exception as error:
        log["errors"].append("Clipboard clear failed: " + type(error).__name__)
    log["completed_utc"] = utc_now()
    log["local_verified"] = not log["errors"]
    LOG_PATH.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps(log, indent=2))
    print("Cleanup log: " + str(LOG_PATH))
    return 0 if log["local_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
