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
        ttk.Style().configure("Side.TLabel", font=("Consolas", 30))
        ttk.Style().configure("SideEntry.TEntry", font=("Consolas", 30))

        # guess answer menu
        self.guessAnswerFrame = ttk.Frame(mainframe)




        # write answer menu
        self.writeAnswerFrame = ttk.Frame(mainframe)

        ttk.Label(self.writeAnswerFrame, text="Write Answer", padding=10, style="Main.TLabel").grid(row=0, column=1, sticky="N")

        for i in range(1, 6, 2):
            ttk.Label(self.writeAnswerFrame, text=f"Q{int((i+1)/2)}:", style="Side.TLabel").grid(row=i, column=0, sticky="W")
            ttk.Label(self.writeAnswerFrame, text=f"A{int((i+1)/2)}:", style="Side.TLabel").grid(row=i+1, column=0, sticky="W")
        ttk.Entry(self.writeAnswerFrame, font=("Consolas", 30)).grid(row=6, column=1, sticky="W, E")
        ttk.Button(self.writeAnswerFrame, text="Submit", padding=10, style="Main.TButton").grid(row=7, column=1) #TODO: Add a function to submit answer to backend and draw next frame

        ttk.Label(self.writeAnswerFrame, text="PLACEHOLDER_QUESTION1", style="Side.TLabel").grid(row=1, column=1, sticky="W") #TODO: backend
        ttk.Label(self.writeAnswerFrame, text="PLACEHOLDER_ANSWER1", style="Side.TLabel").grid(row=2, column=1, sticky="W")
        ttk.Label(self.writeAnswerFrame, text="PLACEHOLDER_QUESTION2", style="Side.TLabel").grid(row=3, column=1, sticky="W")
        ttk.Label(self.writeAnswerFrame, text="PLACEHOLDER_ANSWER2", style="Side.TLabel").grid(row=4, column=1, sticky="W")
        ttk.Label(self.writeAnswerFrame, text="PLACEHOLDER_QUESTION3", style="Side.TLabel").grid(row=5, column=1, sticky="W")

        self.writeAnswerFrame.columnconfigure(1, weight=1)
        self.writeAnswerFrame.rowconfigure((1, 2, 3, 4, 5, 6), weight=1)

        # write questions menu
        """
        self.writeQuestionsFrame = ttk.Frame(mainframe)
        ttk.Label(self.writeQuestionsFrame, text="Write Questions", padding=10, style="Main.TLabel").grid(row=0, column=1,sticky="N")
        for i in range(1, 4):
            ttk.Label(self.writeQuestionsFrame, text=f"Q{i}:").grid(row=i, column=0, sticky="W")
            ttk.Entry(self.writeQuestionsFrame).grid(row=i, column=1, sticky="W, E") #TODO this
        """

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
        ttk.Button(self.mainMenu, text="Join Game", padding=10, style="Main.TButton", command=self.raiseFrame(self.writeAnswerFrame)).grid(row=2) # TODO: add a function to validate join code with a generated game code on backend

        self.mainMenu.columnconfigure(0, weight=1)
        self.mainMenu.rowconfigure((0, 1, 2), weight=1)

        for child in mainframe.winfo_children(): 
            child.grid_configure(sticky=(N, W, E, S), row=0, column=0)
        self.raiseFrame(self.mainMenu)

root = Tk()
FrontEnd(root)

root.mainloop()