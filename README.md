# PAINAD Recorder

## Table of Contents

- [Clone the Repository](#clone-the-repository)
- [Installation](#installation)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Linux](#linux)
- [Shortcuts](#shortcuts)

---

A small Tkinter app for recording nurse PAINAD assessments. It uses only the
Python standard library and requires Python 3.10 or newer.

## Clone the Repository

If you have not already downloaded the project, clone it from GitHub first.

1. Copy the repository URL from the GitHub page by clicking **Code → HTTPS** and copying the URL.
2. Open a terminal (Terminal on macOS/Linux, Windows Terminal or PowerShell on Windows).
3. Change to the directory where you want to store the project. For example:

**
    MacOs/Linux:**

    `cd ~/Downloads`

**
    Windows:**

    `cd "$HOME\Downloads"`

4. Clone the repository:

`git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git`

5. Enter the project directory:

`cd YOUR-REPOSITORY`

You are now inside the project folder and can continue with the installation instructions for your operating system.

## Installation

The app requires Python 3.10 or newer and has no third-party dependencies. The
official macOS and Windows Python installers include Tkinter and `pip`; Linux
distributions often provide them as separate packages. The commands below still
create a private Python environment so the app remains isolated from other
software.

Before starting, complete the steps in **Clone the Repository** above. All commands below should be run from the cloned `NurseAssessment` project folder containing `app.py`.

### macOS

1. Install a current Python 3 release from the
   [official Python macOS downloads page](https://www.python.org/downloads/macos/).
   The standard installer includes `pip` and Tkinter.
2. Open **Terminal**: press `Command+Space`, type `Terminal`, and press Enter.
3. In Terminal, type `cd ` with a space after it. Drag the `NurseAssessment`
   folder from Finder into the Terminal window, then press Enter.
4. Check the installation:

   ```shell
   python3 --version
   python3 -m pip --version
   python3 -m tkinter
   ```

   The last command should open a small Tk window. Close that window before
   continuing.
5. Create the private environment and install the requirements:

   ```shell
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

   The requirements step finishes quickly because no extra packages are
   currently needed.
6. Start the app:

   ```shell
   .venv/bin/python app.py
   ```

For later use, open Terminal, return to the `NurseAssessment` folder as in step
3, and repeat only the final command.

### Windows

1. Install a current Python 3 release from the
   [official Python Windows downloads page](https://www.python.org/downloads/windows/).
   During installation, select **Add python.exe to PATH**. Keep the standard
   `pip` and Tcl/Tk options enabled.
2. Open **Windows Terminal** or **PowerShell** from the Start menu.
3. Change to the `NurseAssessment` folder. One way is to right-click the folder
   in File Explorer, select **Copy as path**, type `cd ` in the terminal, paste
   the path, and press Enter. For example:

   ```powershell
   cd "C:\Users\YourName\Downloads\PA_app\NurseAssessment"
   ```
4. Check the installation:

   ```powershell
   py --version
   py -m pip --version
   py -m tkinter
   ```

   Close the small Tk window opened by the last command.
5. Create the private environment and install the requirements:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
6. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

For later use, open Terminal, return to the same folder, and repeat only the
final command.

### Linux

1. Open a terminal. On many systems the shortcut is `Ctrl+Alt+T`.
2. Install Python, `pip`, virtual-environment support, and Tkinter. On Ubuntu or
   Debian:

   ```shell
   sudo apt update
   sudo apt install python3 python3-pip python3-venv python3-tk
   ```

   On Fedora:

   ```shell
   sudo dnf install python3 python3-pip python3-tkinter
   ```
3. Change to the downloaded `NurseAssessment` folder. For example:

   ```shell
   cd ~/Downloads/PA_app/NurseAssessment
   ```
4. Check the installation:

   ```shell
   python3 --version
   python3 -m pip --version
   python3 -m tkinter
   ```

   Close the small Tk window opened by the last command.
5. Create the private environment and install the requirements:

   ```shell
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```
6. Start the app:

   ```shell
   .venv/bin/python app.py
   ```

For later use, open a terminal, return to the same folder, and repeat only the
final command.

## Shortcuts

On macOS:

- `Command+Enter`: record the current assessment
- `Command+Esc`: clear notes (may not work due to shortcut conflicts)

On Windows and Linux:

- `Alt+Enter`: record the current assessment
- `Alt+Esc`: clear notes
