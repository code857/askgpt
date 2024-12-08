# AskGpt
Linux command line based ChatGPT interface. Quick start
`$ export OPENAI_API_KEY="your secret`
`$ python3 askgpt.py`
`$ ~/bin/askgpt`

## AskGPT Tool Specification
=====================================

This script provides a command-line interface to interact with OpenAI's GPT models.
It supports session management, workspace configuration, model switching, and various
modes of interaction.

## Features:
- Session management
  - `-l`: List all sessions
  - `-c sessionname`: Create and switch to a new session
  - `-s sessionname`: Switch to an existing session
  - `-d sessionname`: Delete the specified session
  - `-d` (no argument): Display the current session's conversation in a custom format
    ([GPT]/[USER]) without system messages.
  - `-n`: Show the current session name
  - `-a`: Show all messages of the current session in JSON
  - `-p`: Show the past history of the current session in JSON

- Workspaces
  - `-w workspace_path`: Switch to a workspace, sessions are stored in workspace_path/.askgpt/sessions
  - `-wc`: Clear the workspace setting and revert to default (~/.askgpt/sessions)

- Model management
  - `-m modelname`: Set the current session's model
  - `-ms modelname`: Set the global default model (stored in ~/.askgpt/model.conf)
  - `-mc`: Clear the global default model, revert to "gpt-4o" and remove model.conf

- Interactive mode
  - Run `askgpt` with no options: Enter interactive mode.
  - Type questions and end input with the EOF word (default: "EOF").
  - If no input is given and just pressing enter BEFORE any user query in this session, it shows the conversation history in the same format as `-d`.
  - Once a user query has been entered and answered, pressing enter with no input no longer shows history.

- End-of-file word
  - `-e eofword`: Change the EOF word

- File input
  - `-f filename`: Read the content of `filename` and send it as a user message

- Paths & Initialization
  - The script stores sessions in ~/.askgpt/sessions by default.
  - On first run, if ~/bin/askgpt does not exist, ask user to install it there.
    If user agrees, copy itself to ~/bin/askgpt and suggest to add `export PATH=$HOME/bin:$PATH`
    in their `.bashrc`.

- If no current session exists when needed, automatically create `master_session` and inform the user.

Default model is `gpt-4o`.

## Dependencies:
- Requires `openai` Python library and OPENAI_API_KEY environment variable.

## Usage:
see `askgpt -h`


