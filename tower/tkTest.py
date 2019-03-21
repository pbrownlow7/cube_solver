from Tkinter import *
from cube import *
from time import sleep

scramble = None

def GenScramble():
    scramble = CreateScramble()
    s = listToStr(scramble)
    #sleep(0.5)
    for l in labels:
        l.config(text="")
    photoLabel.config(image="")
    scrambleLabel = Label(window, text="Scramble:", bg="black", fg="white", font="none 16 bold")
    scrambleLabel.place(x=600, y=20, anchor="center")
    scrambleTextLabel.config(text="Generating...")
    scrambleTextLabel.place(x=600, y=45, anchor="center")
    window.after(1000, lambda: scrambleTextLabel.config(text=s))

def SolveScramble():
    photoLabel.config(image=cubePhoto)
    scramble = scrambleTextLabel.cget("text")
    solve = SolveCubeWithScramble(scramble)
    tim = "0."
    for i in range(6):
        tim += solve[7][i+2]
        
    t = "SOLVED IN " + tim + " SECONDS:"
    pos = 600
    
    for i in range(len(labels)):
        if i == 0:
            labels[i].config(text=t)
        else:
            labels[i].config(text=solve[i-1])
        labels[i].place(x=600, y=pos+(i*25), anchor="center")

    HighlightSolvePart()
    #labels[0].config(fg="red")
    #for i in range(1, len(labels)):
    #    window.after(1000*i, lambda: labels[i].config(fg="red"))
    #window.after(1000, lambda: labels[0].config(fg="white"))

def HighlightSolvePart():
    labels[1].config(fg="red")
    window.after(1000, lambda: labels[1].config(fg="white"))
    window.after(1000, lambda: labels[2].config(fg="red"))
    window.after(2000, lambda: labels[2].config(fg="white"))
    window.after(2000, lambda: labels[3].config(fg="red"))
    window.after(3000, lambda: labels[3].config(fg="white"))
    window.after(3000, lambda: labels[4].config(fg="red"))
    window.after(4000, lambda: labels[4].config(fg="white"))
    window.after(4000, lambda: labels[5].config(fg="red"))
    window.after(5000, lambda: labels[5].config(fg="white"))
    window.after(5000, lambda: labels[6].config(fg="red"))
    window.after(6000, lambda: labels[6].config(fg="white"))
    window.after(6000, lambda: labels[7].config(fg="red"))
    window.after(7000, lambda: labels[7].config(fg="white"))

window = Tk()
window.title("Cube Solver")
window.configure(background="black")
window.geometry("1200x800")
window.resizable(0, 0)

cubePhoto = PhotoImage(file="cube.png")
photoLabel = Label(window, image="", bg="black")
photoLabel.place(x=600, y=350, anchor="center")

scrambleTextLabel = Label(window, bg="black", fg="white", font="none 12 bold")

genScrambleButton = Button(window, text="Generate Scramble", width=16, height=2, font="none 12 bold", command=GenScramble)
genScrambleButton.place(x=200, y=400, anchor="center")

solveScrambleButton = Button(window, text="Solve Scramble", width=16, height=2, font="none 12 bold", command=SolveScramble)
solveScrambleButton.place(x=200, y=460, anchor="center")

labels = [Label(window, bg="black", fg="white", font="none 16 bold"), Label(window, bg="black", fg="white", font="none 12 bold"), Label(window, bg="black", fg="white", font="none 12 bold"), Label(window, bg="black", fg="white", font="none 12 bold"), Label(window, bg="black", fg="white", font="none 12 bold"), Label(window, bg="black", fg="white", font="none 12 bold"), Label(window, bg="black", fg="white", font="none 12 bold"), Label(window, bg="black", fg="white", font="none 12 bold")]

window.mainloop()
