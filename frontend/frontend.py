from random import randint
from tkinter import *
from tkinter import ttk

from httpRequest import *

GAME_CODE: str = ""
PLAYER: str = ""


class FrontEnd:


    @staticmethod
    def raiseFrame(frame: ttk.Frame):
        return lambda: frame.tkraise()

    @staticmethod
    def wrapUpdate(event):
        event.widget.config(wraplength=event.widget.winfo_width())

    def __init__(self, root):

        def generateGameCode():
            self.raiseFrame(self.writeAnswerFrame)
            PLAYER = '1'
            GAME_CODE = str(randint(10000000, 99999999))
            createRoom(GAME_CODE)
            drawGuessAnswerFrame()
        
        def joinGame():
            self.raiseFrame(self.writeAnswerFrame)
            join(GAME_CODE)
            PLAYER = '2'
            drawGuessAnswerFrame()


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
        ttk.Style().configure("sideButton.TRadiobutton", font=("Consolas", 30))

        # waiting screen after submitting answer
        self.submitFrame = ttk.Frame(mainframe)

        ttk.Label(
            self.submitFrame, text="Waiting for other Player", style="Main.TLabel"
        ).grid(row=0, column=0, sticky="N")

        self.submitFrame.columnconfigure(0, weight=1)
        # guess answer menu
        self.guessAnswerFrame = ttk.Frame(mainframe)

        ttk.Label(
            self.guessAnswerFrame,
            text="Guess Human Answer",
            padding=10,
            style="Main.TLabel",
        ).grid(row=0, column=0, sticky="N", columnspan=3)

        for i in range(1, 6, 2):
            ttk.Label(
                self.guessAnswerFrame, text=f"Q{int((i + 1) / 2)}:", style="Side.TLabel"
            ).grid(row=i, column=1, sticky="W, N")
            ttk.Label(
                self.guessAnswerFrame, text=f"A{int((i + 1) / 2)}:", style="Side.TLabel"
            ).grid(row=i + 1, column=1, sticky="W, N")
        def drawGuessAnswerFrame():
            ttk.Label(
                self.guessAnswerFrame,
                text=str(getGame(GAME_CODE, PLAYER)),
                style="Side.TLabel",
            ).grid(row=1, column=2, sticky=(E, W))  # TODO: backend
            ttk.Label(
                self.guessAnswerFrame,
                text=str(getGame(GAME_CODE, PLAYER)),
                style="Side.TLabel",
            ).grid(row=2, column=2, sticky=(E, W))
            ttk.Label(
                self.guessAnswerFrame,
                text=str(getGame(GAME_CODE, PLAYER)),
                style="Side.TLabel",
            ).grid(row=3, column=2, sticky="W, E")
            ttk.Label(
                self.guessAnswerFrame,
                text=str(getGame(GAME_CODE, PLAYER)),
                style="Side.TLabel",
            ).grid(row=4, column=2, sticky="W, E")
            ttk.Label(
                self.guessAnswerFrame,
                text=str(getGame(GAME_CODE, PLAYER)),
                style="Side.TLabel",
            ).grid(row=5, column=2, sticky="W, E")
            ttk.Label(
                self.guessAnswerFrame,
                text=str(getGame(GAME_CODE, PLAYER)),
                style="Side.TLabel",
            ).grid(row=6, column=2, sticky="W, E")
            for widget in self.guessAnswerFrame.winfo_children():
                if widget.grid_info()["row"] >= 1 and widget.grid_info()["column"] == 2:
                    widget.bind("<Configure>", self.wrapUpdate)

        answer = 1
        ttk.Radiobutton(
            self.guessAnswerFrame,
            variable=answer,
            value="answer1",
            style="sideButton.TRadiobutton",
        ).grid(row=2, column=0, sticky="WE")
        ttk.Radiobutton(
            self.guessAnswerFrame,
            variable=answer,
            value="answer2",
            style="sideButton.TRadiobutton",
        ).grid(row=4, column=0, sticky="WE")
        ttk.Radiobutton(
            self.guessAnswerFrame,
            variable=answer,
            value="answer3",
            style="sideButton.TRadiobutton",
        ).grid(row=6, column=0, sticky="WE")

        ttk.Button(
            self.guessAnswerFrame,
            text="Submit",
            padding=10,
            style="Main.TButton",
            command=self.raiseFrame(self.submitFrame),
        ).grid(
            row=7, column=0, columnspan=3
        )  # TODO: Add a function to submit answer to backend and backend responds with whether the user was correct

        self.guessAnswerFrame.columnconfigure(2, weight=1)

        # write answer menu
        self.writeAnswerFrame = ttk.Frame(mainframe)

        ttk.Label(
            self.writeAnswerFrame, text="Write Answer", padding=10, style="Main.TLabel"
        ).grid(row=0, column=1, sticky="N")

        for i in range(1, 6, 2):
            ttk.Label(
                self.writeAnswerFrame, text=f"Q{int((i + 1) / 2)}:", style="Side.TLabel"
            ).grid(row=i, column=0, sticky="W")
            ttk.Label(
                self.writeAnswerFrame, text=f"A{int((i + 1) / 2)}:", style="Side.TLabel"
            ).grid(row=i + 1, column=0, sticky="W")
        ttk.Entry(self.writeAnswerFrame, font=("Consolas", 30)).grid(
            row=6, column=1, sticky="W, E"
        )
        ttk.Button(
            self.writeAnswerFrame,
            text="Submit",
            padding=10,
            style="Main.TButton",
            command=self.raiseFrame(self.submitFrame),
        ).grid(
            row=7, column=1
        )  # TODO: Add a function to submit answer to backend and draw next frame

        ttk.Label(
            self.writeAnswerFrame, text="PLACEHOLDER_QUESTION1", style="Side.TLabel"
        ).grid(row=1, column=1, sticky="W, E")  # TODO: backend
        ttk.Label(
            self.writeAnswerFrame, text="PLACEHOLDER_ANSWER1", style="Side.TLabel"
        ).grid(row=2, column=1, sticky="W, E")
        ttk.Label(
            self.writeAnswerFrame, text="PLACEHOLDER_QUESTION2", style="Side.TLabel"
        ).grid(row=3, column=1, sticky="W, E")
        ttk.Label(
            self.writeAnswerFrame, text="PLACEHOLDER_ANSWER2", style="Side.TLabel"
        ).grid(row=4, column=1, sticky="W, E")
        ttk.Label(
            self.writeAnswerFrame, text="PLACEHOLDER_QUESTION3", style="Side.TLabel"
        ).grid(row=5, column=1, sticky="W, E")

        for widget in self.writeAnswerFrame.winfo_children():
            if widget.grid_info()["row"] >= 1 and widget.grid_info()["column"] == 1:
                widget.bind("<Configure>", self.wrapUpdate)

        self.writeAnswerFrame.columnconfigure(1, weight=1)
        # self.writeAnswerFrame.rowconfigure((1, 2, 3, 4, 5, 6), weight=1)

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

        ttk.Label(
            self.waitingFrame,
            text="Waiting for Second Player...",
            padding=10,
            style="Main.TLabel",
        ).grid(row=0, sticky="N")
        ttk.Label(self.waitingFrame, text=GAME_CODE, padding=10, style="Main.TLabel").grid(
            row=1
        )

        self.waitingFrame.columnconfigure(0, weight=1)
        self.waitingFrame.rowconfigure(1, weight=1)

        # mainmenu frame ### DO NOT MOVE THIS "DO NOT LEAVE YET"
        self.mainMenu = ttk.Frame(mainframe)

        ttk.Entry(self.mainMenu, font=("Consolas", 30)).grid(
            row=2, column=1, sticky="W, E"
        )


        ttk.Label(
            self.mainMenu, text="Main Menu", padding=10, style="Main.TLabel"
        ).grid(row=0)
        ttk.Button(
            self.mainMenu,
            text="Create Game",
            padding=10,
            style="Main.TButton",
            command=generateGameCode,
        ).grid(row=1)
        ttk.Button(
            self.mainMenu,
            text="Join Game",
            padding=10,
            style="Main.TButton",
            command=joinGame,
        ).grid(
            row=3
        )  # TODO: add a function to validate join code with a generated game code on backend

        self.mainMenu.columnconfigure(0, weight=1)
        self.mainMenu.rowconfigure((0, 1, 2), weight=1)

        for child in mainframe.winfo_children():
            child.grid_configure(sticky=(N, W, E, S), row=0, column=0)
        self.raiseFrame(self.mainMenu)

        root.mainloop()


root = Tk()
FrontEnd(root)
