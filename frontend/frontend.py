from tkinter import *
from tkinter import ttk
from random import randint

class FrontEnd:

    @staticmethod
    def generateGameCode():
        return str(randint(10000000, 99999999))

    @staticmethod
    def raiseFrame(frame: ttk.Frame):
        return lambda: frame.tkraise()

    def __init__(self, root):
        # establish root
        self.root = root
        root.title("Two AIs and a Human")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # establish mainframe
        mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        ttk.Style().configure("Main.TButton", font=("Consolas", 50))
        ttk.Style().configure("Main.TLabel", font=("Consolas", 50))

        # write answer menu
        self.writeAnswerFrame = ttk.Frame(mainframe)

        # write questions menu
        self.writeQuestionsFrame = ttk.Frame(mainframe)

        # game code menu
        self.waitingFrame = ttk.Frame(mainframe)
        
        ttk.Label(self.waitingFrame, text="Waiting for Second Player...", padding=10, style="Main.TLabel").grid(row=0, sticky="N")
        ttk.Label(self.waitingFrame, text="Code", padding=10, style="Main.TLabel").grid(row=1)

        self.waitingFrame.columnconfigure(0, weight=1)
        self.waitingFrame.rowconfigure(1, weight=1)

        # mainmenu frame ### DO NOT MOVE THIS "DO NOT LEAVE YET"
        self.mainMenu = ttk.Frame(mainframe)

        ttk.Label(self.mainMenu, text="Main Menu", padding=10, style="Main.TLabel").grid(row=0)
        ttk.Button(self.mainMenu, text="Create Game", padding=10, style="Main.TButton", command=self.raiseFrame(self.waitingFrame)).grid(row=1)
        ttk.Button(self.mainMenu, text="Join Game", padding=10, style="Main.TButton").grid(row=2) # TODO: add a function to validate join code with a generated game code on backend

        self.mainMenu.columnconfigure(0, weight=1)
        self.mainMenu.rowconfigure((0, 1, 2), weight=1)

        for child in mainframe.winfo_children(): 
            child.grid_configure(sticky=(N, W, E, S), row=0, column=0)
        self.raiseFrame(self.mainMenu)

root = Tk()
FrontEnd(root)

root.mainloop()