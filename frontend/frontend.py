from random import randint
from tkinter import *
from tkinter import ttk
import time
import threading
from httpRequest import *

GAME_CODE: str = ""
PLAYER: str = ""


class FrontEnd:


    @staticmethod
    def raiseFrame(frame: ttk.Frame):
        return lambda: frame.tkraise()

    @staticmethod
    def wrapUpdate(event):
        ttk.Style().configure(event.widget.winfo_class(), wraplength=(event.widget.winfo_width() - 25))

    def __init__(self, root):

        def wait_for_player():
            while True:
                x=checkGame(GAME_CODE, PLAYER)
                print(x)
                if x:
                    drawWriteAnswerFrame()
                    self.raiseFrame(self.writeAnswerFrame)()
                    return
                time.sleep(3)

        def wait_for_player_results():
            while True:
                x=getFinal(GAME_CODE, PLAYER)
                print(x.status_code)
                print(x)
                if x.status_code==200:
                    drawGuessAnswerFrame()
                    self.raiseFrame(self.guessAnswerFrame)()
                    return
                time.sleep(3)

        def giveAnswer():
            self.raiseFrame(self.submitFrame)()
            if data[1] == "":
                giveEntry = ent1.get()
            elif data[3] == "":
                giveEntry = ent2.get()
            else:
                giveEntry = ent3.get()
            submitAnswer(GAME_CODE, PLAYER, giveEntry)
            t=threading.Thread(target=wait_for_player_results)
            t.start()
            

        

        def generateGameCode():
            global PLAYER, GAME_CODE
            PLAYER = '1'
            GAME_CODE = str(randint(10000000, 99999999))
            createRoom(GAME_CODE)
            drawWaitingFrame()
            self.raiseFrame(self.waitingFrame)()
            thread = threading.Thread(target=wait_for_player)
            thread.start()
            
        
        def joinGame():
            global PLAYER, GAME_CODE
            GAME_CODE = entry12.get()
            join(GAME_CODE)
            PLAYER = '2'
            thread = threading.Thread(target=wait_for_player)
            thread.start()

        


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
        ttk.Style().configure("Side.TLabel", font=("Consolas", 24))
        ttk.Style().configure("SideEntry.TEntry", font=("Consolas", 24))
        ttk.Style().configure("sideButton.TRadiobutton", font=("Consolas", 24))




        # waiting screen after submitting answer
        self.submitFrame = ttk.Frame(mainframe)

        ttk.Label(
            self.submitFrame, text="Waiting for other Player", style="Main.TLabel"
        ).grid(row=0, column=0, sticky="N")

        self.submitFrame.columnconfigure(0, weight=1)
        # guess answer menu
        def drawGuessAnswerFrame():
            self.guessAnswerFrame = ttk.Frame(mainframe)
            self.guessAnswerFrame.grid_configure(sticky=(N, S, E, W), row=0, column=0)

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


            dataFinal = getFinal(GAME_CODE, PLAYER).json() #dictionary!
            print(dataFinal)
            print(type(dataFinal))

            ttk.Label(self.guessAnswerFrame,text=dataFinal["q1"],style="Side.TLabel",).grid(row=1, column=2, sticky=(E, W))  # TODO: backend
            ttk.Label(
                self.guessAnswerFrame,
                text=dataFinal["a1"],
                style="Side.TLabel",
            ).grid(row=2, column=2, sticky=(E, W))
            ttk.Label(
                self.guessAnswerFrame,
                text=dataFinal["q2"],
                style="Side.TLabel",
            ).grid(row=3, column=2, sticky="W, E")
            ttk.Label(
                self.guessAnswerFrame,
                text=dataFinal["a2"],
                style="Side.TLabel",
            ).grid(row=4, column=2, sticky="W, E")
            ttk.Label(
                self.guessAnswerFrame,
                text=dataFinal["q3"],
                style="Side.TLabel",
            ).grid(row=5, column=2, sticky="W, E")
            ttk.Label(
                self.guessAnswerFrame,
                text=dataFinal["a3"],
                style="Side.TLabel",
            ).grid(row=6, column=2, sticky="W, E")
            for widget in self.guessAnswerFrame.winfo_children():
                if widget.grid_info()["row"] >= 1 and widget.grid_info()["column"] == 2:
                    widget.bind("<Configure>", self.wrapUpdate)

            answer = IntVar()
            ttk.Radiobutton(
                self.guessAnswerFrame,
                variable=answer,
                value=1,
                style="sideButton.TRadiobutton",
            ).grid(row=2, column=0, sticky="WE")
            ttk.Radiobutton(
                self.guessAnswerFrame,
                variable=answer,
                value=2,
                style="sideButton.TRadiobutton",
            ).grid(row=4, column=0, sticky="WE")
            ttk.Radiobutton(
                self.guessAnswerFrame,
                variable=answer,
                value=3,
                style="sideButton.TRadiobutton",
            ).grid(row=6, column=0, sticky="WE")
            if int(answer.get()) == dataFinal["real"]:
                print("WINNNNNNN")
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
        def drawWriteAnswerFrame():
            self.writeAnswerFrame = ttk.Frame(mainframe)
            self.writeAnswerFrame.grid_configure(sticky=(N, S, E, W), row=0, column=0)

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

            ttk.Button(
                self.writeAnswerFrame,text="Submit",padding=10,style="Main.TButton",command=giveAnswer,).grid(row=7, column=1)  # TODO: Add a function to submit answer to backend and draw next frame

            global data
            data = list(getGame(GAME_CODE, PLAYER))
            entryValue = StringVar()
            

            ttk.Label(self.writeAnswerFrame, text=data[0], style="Side.TLabel").grid(row=1, column=1, sticky="W, E")  # TODO: backend
            ttk.Label(self.writeAnswerFrame, text=data[2], style="Side.TLabel").grid(row=3, column=1, sticky="W, E")
            ttk.Label(self.writeAnswerFrame, text=data[4], style="Side.TLabel").grid(row=5, column=1, sticky="W, E")
            if data[1] == "":
                global ent1
                ent1 = ttk.Entry(self.writeAnswerFrame, font=("Consolas", 24), textvariable=entryValue)
                ent1.grid(row=2, column=1, sticky="W, E")
                ttk.Label(self.writeAnswerFrame, text=data[3], style="Side.TLabel").grid(row=4, column=1, sticky="W, E")
                ttk.Label(self.writeAnswerFrame, text=data[5], style="Side.TLabel").grid(row=6, column=1, sticky="W, E")
            elif data[3] == "":
                global ent2
                ent2 = ttk.Entry(self.writeAnswerFrame, font=("Consolas", 24), textvariable=entryValue)
                ent2.grid(row=4, column=1, sticky="W, E")
                ttk.Label(self.writeAnswerFrame, text=data[1], style="Side.TLabel").grid(row=2, column=1, sticky="W, E")
                ttk.Label(self.writeAnswerFrame, text=data[5], style="Side.TLabel").grid(row=6, column=1, sticky="W, E")
            else:
                global ent3
                ent3 = ttk.Entry(self.writeAnswerFrame, font=("Consolas", 24), textvariable=entryValue)
                ent3.grid(row=6, column=1, sticky="W, E")
                ttk.Label(self.writeAnswerFrame, text=data[1], style="Side.TLabel").grid(row=2, column=1, sticky="W, E")
                ttk.Label(self.writeAnswerFrame, text=data[3], style="Side.TLabel").grid(row=4, column=1, sticky="W, E")





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
        def drawWaitingFrame():

            self.waitingFrame = ttk.Frame(mainframe)
            self.waitingFrame.grid_configure(sticky=(N, W, E, S), row=0, column=0)
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
        global GAME_CODE_not
        GAME_CODE_not = StringVar()
        entry12 = ttk.Entry(self.mainMenu, font=("Consolas", 30), textvariable=GAME_CODE_not)
        entry12.grid(row=2, column=1, sticky="W, E")

        print(GAME_CODE_not)

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
