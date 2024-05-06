from dashboard import *
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    root = ctk.CTk()
    root.title = "Live Hazardous Object Detection"
    dashboard(root)
    root.mainloop()
