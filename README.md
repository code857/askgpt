# AskGPT Tool Specification 

 This script provides a command-line interface to interact with OpenAI's GPT models.
 It supports session management, workspace configuration, model switching, file input,
 and various modes of interaction.

## Features:
 - Session management
   - `-l`: List all sessions
   - `-c sessionname`: Create and switch to a new session
   - `-s sessionname`: Switch to an existing session
   - `-d sessionname`: Delete the specified session
   - `-d`: Display the current session's conversation in a custom format ([GPT]/[USER]) without system messages
   - `-n`: Show the current session name
   - `-a`: Show all messages of the current session in JSON
   - `-p`: Show the past history of the current session in JSON

 - Workspaces
   - `-w workspace_path`: Switch to a workspace, sessions are stored in workspace_path/.askgpt/sessions
   - `-wc`: Clear the workspace setting and revert to default (~/.askgpt/sessions)
   - `-wl`: List known workspaces, including the current one (if any) and the default.

 - Model management
   - `-m modelname`: Set the current session's model
   - `-ms modelname`: Set the global default model (stored in ~/.askgpt/model.conf)
   - `-mc`: Revert the global default model to `gpt-4o` and remove model.conf

 - Interactive mode
   - Run `askgpt` with no options to enter interactive mode.
   - Type questions and end input with the EOF word (default: "EOF").
   - If no queries have been asked yet in the current session, pressing enter on an empty line shows the conversation history in the `-d` format.
   - Once a query has been asked, empty line no longer shows history.

 - End-of-file word
   - `-e eofword`: Change the EOF word

 - File input (`-f filename`)
   - If `-f filename` is specified, the content of the file is used as a user message.
   - After processing the file input, the script remains in interactive mode, accepting further standard input.
   - If the first action is the user typing just the EOF word without any typed lines, and `-f` was specified, 
     the file content is immediately sent as the user message and a response is obtained.
   - If the first action is the user typing the EOF word with no `-f` given, the program exits (no input to send).
   - After `-f` input is consumed and a response received, subsequent EOF with no user input means exit.

 - If no current session exists, a `master_session` is automatically created and used.

 - Default model is `gpt-4o`.


## Quick Installation:
 ------------------
 1. Ensure you have Python installed and `openai` Python library (`pip install openai`).
 2. Run this script for the first time. If `~/bin/askgpt` doesn't exist,
    it will prompt you to install it. If you agree, it will install itself to `~/bin/askgpt`.
 3. Add `export PATH="$HOME/bin:$PATH"` to your `~/.bashrc` (or `~/.zshrc`, depending on your shell).
    For example:
       echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    Then run:
       source ~/.bashrc

 After this, you can run `askgpt` from anywhere in your terminal.

## Dependencies:
 - `openai` Python library
 - `OPENAI_API_KEY` environment variable set with your API key.
