import tkinter as tk
import subprocess
import os


class Demo:
    def __init__(self, name: str, command: 'list[str]'):
        self.command = command
        self.process = None
        self.name = name

    def start(self):
        # initialize the process for the first time
        if self.process is None:
            self.process = subprocess.Popen(self.command)
            return True

        poll = self.process.poll()
        if poll is None:
            return False

        self.process = subprocess.Popen(self.command)
        return True

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            print('killed', self.name, 'pid:', self.process.pid)
            return True
        return False


demos = [
    Demo('N-Body Physics',
         ['python',
          os.path.join('particle_gravity', 'graphical.py')]),
    Demo('Markov GUI', ['python', 'markov.py']),
    Demo('Evil Rock-Paper-Scissors', ['python', 'rps.py']),
]

root = tk.Tk()
root.title("N-Queens Launcher")
frame = tk.Frame(root)
frame.pack()

text = tk.Label(frame, text="Select a demo to run")
text.pack(fill=tk.X)
for d in demos:
    button = tk.Button(frame, text=d.name, command=d.start)
    button.pack(fill=tk.X)
    button = tk.Button(frame, text='Kill ' + d.name, command=d.stop)
    button.pack(fill=tk.Y)

root.mainloop()
