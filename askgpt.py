#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# AskGPT Tool Specification (in English)
# =====================================
#
# This script provides a command-line interface to interact with OpenAI's GPT models.
# It supports session management, workspace configuration, model switching, and various
# modes of interaction.
#
# Features:
# - Session management
#   - `-l`: List all sessions
#   - `-c sessionname`: Create and switch to a new session
#   - `-s sessionname`: Switch to an existing session
#   - `-d sessionname`: Delete the specified session
#   - `-d`: Display the current session's conversation in a custom format ([GPT]/[USER]) without system messages
#   - `-n`: Show the current session name
#   - `-a`: Show all messages of the current session in JSON
#   - `-p`: Show the past history of the current session in JSON
#
# - Workspaces
#   - `-w workspace_path`: Switch to a workspace, sessions are stored in workspace_path/.askgpt/sessions
#   - `-wc`: Clear the workspace setting and revert to default (~/.askgpt/sessions)
#   - `-wl`: List known workspaces, including the current one (if any) and the default.
#
# - Model management
#   - `-m modelname`: Set the current session's model
#   - `-ms modelname`: Set the global default model (stored in ~/.askgpt/model.conf)
#   - `-mc`: Revert the global default model to `gpt-4o` and remove model.conf
#
# - Interactive mode
#   - Run `askgpt` with no options to enter interactive mode.
#   - Type questions and end input with the EOF word (default: "EOF").
#   - If no queries have been asked yet in the current session, pressing enter on an empty line shows the conversation history in the `-d` format.
#   - Once a query has been asked, empty line no longer shows history.
#
# - End-of-file word
#   - `-e eofword`: Change the EOF word
#
# - File input
#   - `-f filename`: Read the content of `filename` and send it as user message
#
# - If no current session exists, a `master_session` is automatically created and used.
#
# - Default model is `gpt-4o`.
#
#
# Quick Installation:
# ------------------
# 1. Ensure you have Python installed and `openai` Python library (`pip install openai`).
# 2. Run this script for the first time. If `~/bin/askgpt` doesn't exist,
#    it will prompt you to install it. If you agree, it will install itself to `~/bin/askgpt`.
# 3. Add `export PATH="$HOME/bin:$PATH"` to your `~/.bashrc` (or `~/.zshrc`, depending on your shell).
#    For example:
#       echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
#    Then run:
#       source ~/.bashrc
#
# After this, you can run `askgpt` from anywhere in your terminal.
#
# Dependencies:
# - `openai` Python library
# - `OPENAI_API_KEY` environment variable set with your API key.
#
"""

import os
import sys
import json
import openai
import shutil
from pathlib import Path

HOME = Path(os.environ.get("HOME", "~"))
ASKGPT_DIR = HOME / ".askgpt"
DEFAULT_MODEL = "gpt-4o"
MODEL_CONF = ASKGPT_DIR / "model.conf"
WORKSPACE_CONF = ASKGPT_DIR / "workspace.conf"
EOF_CONF = ASKGPT_DIR / "eof.conf"
CURRENT_SESSION_FILE = ASKGPT_DIR / "current_session"
INSTALL_PATH = HOME / "bin" / "askgpt"
WORKSPACES_LIST = ASKGPT_DIR / "workspaces.json"

DEFAULT_EOF = "EOF"

def ensure_directories():
    if not ASKGPT_DIR.exists():
        ASKGPT_DIR.mkdir(parents=True, exist_ok=True)
    if not EOF_CONF.exists():
        with EOF_CONF.open("w", encoding="utf-8") as f:
            f.write(DEFAULT_EOF + "\n")

def load_eof_word():
    if EOF_CONF.exists():
        return EOF_CONF.read_text(encoding="utf-8").strip()
    return DEFAULT_EOF

def save_eof_word(eof_word):
    with EOF_CONF.open("w", encoding="utf-8") as f:
        f.write(eof_word + "\n")

def get_current_session():
    if CURRENT_SESSION_FILE.exists():
        sess = CURRENT_SESSION_FILE.read_text(encoding="utf-8").strip()
        if sess:
            return sess
    return None

def ensure_current_session():
    sess = get_current_session()
    if sess is None:
        # create master_session
        master_name = "master_session"
        if not session_exists(master_name):
            create_session_silent(master_name)
        set_current_session(master_name)
        print("No current session found. Created 'master_session' and switched to it.")
        return master_name
    return sess

def set_current_session(sessionname):
    with CURRENT_SESSION_FILE.open("w", encoding="utf-8") as f:
        f.write(sessionname + "\n")

def get_workspace_path():
    if WORKSPACE_CONF.exists():
        ws = WORKSPACE_CONF.read_text(encoding="utf-8").strip()
        if ws:
            return Path(ws)
    return None

def set_workspace_path(ws_path):
    with WORKSPACE_CONF.open("w", encoding="utf-8") as f:
        f.write(str(ws_path) + "\n")
    register_workspace(ws_path)

def clear_workspace():
    if WORKSPACE_CONF.exists():
        WORKSPACE_CONF.unlink()

def get_sessions_dir():
    ws = get_workspace_path()
    if ws:
        sdir = ws / ".askgpt" / "sessions"
        if not sdir.exists():
            sdir.mkdir(parents=True, exist_ok=True)
        return sdir
    else:
        sdir = ASKGPT_DIR / "sessions"
        if not sdir.exists():
            sdir.mkdir(parents=True, exist_ok=True)
        return sdir

def session_file(sessionname):
    return get_sessions_dir() / f"{sessionname}.json"

def session_exists(sessionname):
    return session_file(sessionname).exists()

def load_session(sessionname):
    sf = session_file(sessionname)
    if sf.exists():
        with sf.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                data = {"model": get_default_model(), "messages": data}
            if "model" not in data:
                data["model"] = get_default_model()
            return data
    return {"model": get_default_model(), "messages": []}

def save_session(sessionname, data):
    sf = session_file(sessionname)
    with sf.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def list_sessions():
    for f in get_sessions_dir().glob("*.json"):
        print(f.stem)

def create_session_silent(sessionname):
    data = {
        "model": get_default_model(),
        "messages": []
    }
    save_session(sessionname, data)

def create_session(sessionname):
    if session_exists(sessionname):
        print(f"Session {sessionname} already exists.")
        sys.exit(1)
    create_session_silent(sessionname)
    set_current_session(sessionname)
    print(f"Created and switched to session: {sessionname}")

def print_help():
    help_msg = """
Usage: askgpt [options]

Options:
  -l                 List all sessions.
  -c sessionname     Create a new session with 'sessionname' and switch to it.
  -s sessionname     Switch to an existing session.
  -d sessionname     Delete the specified session.
  -d                 Display the conversation of the current session in a custom format:
                         [GPT]
                         GPT messages...
                         [USER]
                         USER messages...
  -n                 Show the current session name.
  -a                 Show all messages of the current session in JSON.
  -p                 Show the past history of the current session in JSON.
  -h                 Show this help message.
  -e eofword         Change the EOF word to 'eofword'.
  -f filename        Read the content of 'filename' and send it as user message.

  -w workspace_path  Switch the workspace to 'workspace_path'
                     (sessions stored in workspace_path/.askgpt/sessions)
  -wc                Clear the workspace and revert to default (~/.askgpt/sessions)
  -wl                List known workspaces, including current one.

  -m modelname       Change the model of the current session to 'modelname'.
  -ms modelname      Change the global default model to 'modelname' (saved in ~/.askgpt/model.conf).
  -mc                Revert the global default model to gpt-4o and remove ~/.askgpt/model.conf.

Without options:
  askgpt             Start interactive mode. Input your question. End with the EOF word (default: EOF).
                     If no queries asked yet, pressing enter on empty line shows the history (-d format).
                     Once you have entered queries, empty line no longer shows history.
"""
    print(help_msg.strip())

def switch_session(sessionname):
    if not session_exists(sessionname):
        print(f"Session {sessionname} does not exist.")
        sys.exit(1)
    set_current_session(sessionname)
    print(f"Switched to session: {sessionname}")

def delete_session(sessionname):
    sf = session_file(sessionname)
    if not sf.exists():
        print(f"Session {sessionname} does not exist.")
        sys.exit(1)
    sf.unlink()
    cur = get_current_session()
    if cur == sessionname:
        CURRENT_SESSION_FILE.unlink(missing_ok=True)
    print(f"Session {sessionname} deleted.")

def display_current_session_custom_format(messages):
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "assistant":
            print("[GPT]")
            print(content.strip())
        elif role == "user":
            print("[USER]")
            print(content.strip())
        # system is skipped

def display_all_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

def get_default_model():
    if MODEL_CONF.exists():
        return MODEL_CONF.read_text(encoding="utf-8").strip()
    return DEFAULT_MODEL

def query_gpt(data):
    model = data.get("model", get_default_model())
    openai.api_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai.api_key:
        print("Error: OPENAI_API_KEY not set.")
        sys.exit(1)

    response = openai.ChatCompletion.create(
        model=model,
        messages=data["messages"]
    )
    return response["choices"][0]["message"]["content"]

def interactive_mode(eof_word):
    sessionname = ensure_current_session()
    data = load_session(sessionname)

    no_question_asked_yet = True

    print(f"Current session: {sessionname}")
    print(f"Type your question and end input with '{eof_word}' on a single line.")
    print("If no query asked yet, empty line shows history (-d format). After queries, empty line does nothing.\n")

    while True:
        user_lines = []
        while True:
            try:
                line = input()
            except EOFError:
                return
            if line.strip() == "":
                if no_question_asked_yet:
                    # show history in -d format
                    display_current_session_custom_format(data["messages"])
                    return
                else:
                    # After queries, empty line does nothing
                    continue
            if line.strip() == eof_word:
                break
            user_lines.append(line)

        if len(user_lines) == 0:
            continue

        # Send to GPT
        user_message = "\n".join(user_lines)
        data["messages"].append({"role":"user", "content": user_message})
        assistant_reply = query_gpt(data)
        data["messages"].append({"role":"assistant", "content": assistant_reply})
        save_session(sessionname, data)
        print(assistant_reply)
        no_question_asked_yet = False

def file_input_mode(filename):
    sessionname = ensure_current_session()
    if not Path(filename).exists():
        print(f"File not found: {filename}")
        sys.exit(1)
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    data = load_session(sessionname)
    data["messages"].append({"role": "user", "content": content})
    assistant_reply = query_gpt(data)
    data["messages"].append({"role": "assistant", "content": assistant_reply})
    save_session(sessionname, data)
    print(assistant_reply)

def set_model_for_current_session(modelname):
    sessionname = ensure_current_session()
    data = load_session(sessionname)
    data["model"] = modelname
    save_session(sessionname, data)
    print(f"Model for session {sessionname} changed to {modelname}.")

def set_global_default_model(modelname):
    with MODEL_CONF.open("w", encoding="utf-8") as f:
        f.write(modelname + "\n")
    print(f"Global default model changed to {modelname}.")

def clear_global_default_model():
    if MODEL_CONF.exists():
        MODEL_CONF.unlink()
    print("Global default model reverted to gpt-4o.")

def set_workspace(workspace_path):
    set_workspace_path(workspace_path)
    print(f"Workspace set to {workspace_path}")

def register_workspace(ws_path):
    # Keep track of known workspaces in workspaces.json
    known = load_workspaces()
    ws_str = str(ws_path)
    if ws_str not in known:
        known.append(ws_str)
        save_workspaces(known)

def load_workspaces():
    if WORKSPACES_LIST.exists():
        with WORKSPACES_LIST.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_workspaces(lst):
    with WORKSPACES_LIST.open("w", encoding="utf-8") as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

def list_workspaces():
    # show current, default, and known
    current_ws = get_workspace_path()
    known = load_workspaces()
    print("Workspaces:")
    if current_ws:
        print(f"* Current workspace: {current_ws}")
    else:
        print("* Current workspace: (default)")

    default_ws = ASKGPT_DIR / "sessions"
    print(f"* Default workspace: {default_ws}")

    if known:
        print("Known workspaces:")
        for ws in known:
            mark = "(current)" if current_ws and str(current_ws) == ws else ""
            print(f" - {ws} {mark}")
    else:
        print("No other known workspaces.")

def first_run_install_check():
    # Check if ~/bin/askgpt exists
    if not INSTALL_PATH.exists():
        print("It seems this is the first time you are running askgpt.")
        ans = input(f"Would you like to install this script to {INSTALL_PATH}? (y/n): ")
        if ans.lower().startswith('y'):
            # Ensure ~/bin exists
            if not INSTALL_PATH.parent.exists():
                INSTALL_PATH.parent.mkdir(parents=True, exist_ok=True)
            # Copy this script to ~/bin/askgpt
            script_path = Path(sys.argv[0]).resolve()
            shutil.copy(script_path, INSTALL_PATH)
            INSTALL_PATH.chmod(0o755)
            print(f"Installed askgpt to {INSTALL_PATH}.")
            print("Please add the following line to your ~/.bashrc (if not already present):")
            print('    export PATH="$HOME/bin:$PATH"')
            print("Then run 'source ~/.bashrc' to update your PATH.")
        else:
            print("Skipping installation. You can manually install the script later if you want.")

def main():
    ensure_directories()
    first_run_install_check()  # Check installation on first run
    eof_word = load_eof_word()

    args = sys.argv[1:]

    if len(args) == 0:
        # interactive mode
        interactive_mode(eof_word)
        return

    if len(args) == 1:
        if args[0] == "-l":
            list_sessions()
            return
        elif args[0] == "-n":
            sess = get_current_session()
            if sess is None:
                sess = ensure_current_session()
            print(sess)
            return
        elif args[0] == "-a":
            sess = ensure_current_session()
            data = load_session(sess)
            display_all_json(data)
            return
        elif args[0] == "-p":
            sess = ensure_current_session()
            data = load_session(sess)
            display_all_json(data)
            return
        elif args[0] == "-h":
            print_help()
            return
        elif args[0] == "-d":
            sess = ensure_current_session()
            data = load_session(sess)
            display_current_session_custom_format(data["messages"])
            return
        elif args[0] == "-wc":
            clear_workspace()
            print("Workspace reverted to default.")
            return
        elif args[0] == "-mc":
            clear_global_default_model()
            return
        elif args[0] == "-wl":
            list_workspaces()
            return
        else:
            print("Invalid option. See -h for help.")
            sys.exit(1)

    if len(args) == 2:
        if args[0] == "-c":
            create_session(args[1])
            return
        elif args[0] == "-s":
            switch_session(args[1])
            return
        elif args[0] == "-d":
            delete_session(args[1])
            return
        elif args[0] == "-e":
            save_eof_word(args[1])
            print(f"EOF word changed to: {args[1]}")
            return
        elif args[0] == "-f":
            file_input_mode(args[1])
            return
        elif args[0] == "-w":
            set_workspace(args[1])
            return
        elif args[0] == "-m":
            set_model_for_current_session(args[1])
            return
        elif args[0] == "-ms":
            set_global_default_model(args[1])
            return
        else:
            print("Invalid option. See -h for help.")
            sys.exit(1)

    # If reached here, invalid usage
    print("Invalid usage. See -h for help.")
    sys.exit(1)

if __name__ == "__main__":
    main()
