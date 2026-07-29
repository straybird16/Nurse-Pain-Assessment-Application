"""Entry point for the PAINAD Recorder."""

import tkinter as tk

from config import RECORDS_DIRECTORY
from gui import PainadRecorderApp
from recorder import CsvRecorder


def main() -> None:
    root = tk.Tk()
    PainadRecorderApp(root, CsvRecorder(RECORDS_DIRECTORY))
    root.mainloop()


if __name__ == "__main__":
    main()
