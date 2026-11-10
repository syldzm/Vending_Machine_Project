import tkinter as tk
from gui import VendingMachineGUI

def main():
    # GUI 인스턴스 super vaporization
    root = tk.Tk()
    app = VendingMachineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()