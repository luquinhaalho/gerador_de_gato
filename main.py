# main.py

import tkinter as tk
from ui import CatViewerApp

if __name__ == "__main__":
    # Cria a janela principal
    root = tk.Tk()
    
    # Inicia a nossa aplicação, passando a janela principal para ela
    app = CatViewerApp(root)
    
    # Inicia o loop de eventos do Tkinter, que mantém a janela aberta
    root.mainloop()