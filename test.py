import tkinter as tk
import yfinance as yf
from datetime import datetime
import pytz
from tkinter import ttk

class MarketTickerWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Market Ticker")
        self.root.bell()
        
        # Make window stay on top and frameless
        self.root.attributes('-topmost', True, '-alpha', 0.9)
        self.root.overrideredirect(True)
        
        # Create main frame with a white background
        lbl = tk.Label(self.root,text="Indian Markets at a glance")
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        lbl.grid(sticky="nsew")
        # Configure the window to expand properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Data for tracking mouse drag
        self._drag_data = {"x": 0, "y": 0, "moved": False}
        
        # Bind mouse events for dragging
        self.main_frame.bind('<Button-1>', self.on_drag_start)
        self.main_frame.bind('<B1-Motion>', self.on_drag_motion)
        
        # Add close button
        close_button = ttk.Button(self.main_frame, text="×", width=2, 
                                command=self.root.quit)
        close_button.grid(row=0, column=4, sticky="ne")
        
        # Initialize symbol data
        self.symbols = {
            "NIFTY50": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "HDFC Bank": "HDFCBANK.NS",
            "IGIL": "IGIL.NS",
        }
        
        # Create labels for each symbol
        self.price_labels = {}
        self.change_labels = {}
        
        # Style configuration
        style = ttk.Style()
        style.configure("Green.TLabel", foreground="green")
        style.configure("Red.TLabel", foreground="red")
        
        # Create and place labels
        for idx, (name, symbol) in enumerate(self.symbols.items(), start=1):
            # Symbol name label
            name_label = ttk.Label(self.main_frame, text=name, width=12)
            name_label.grid(row=idx, column=0, padx=2, pady=1, sticky="w")
            
            # Price label
            price_label = ttk.Label(self.main_frame, text="Loading...", width=10)
            price_label.grid(row=idx, column=1, padx=2, pady=1)
            self.price_labels[symbol] = price_label
            
            # Change label
            change_label = ttk.Label(self.main_frame, text="--", width=15)
            change_label.grid(row=idx, column=2, padx=2, pady=1)
            self.change_labels[symbol] = change_label
        
        # Initial update
        self.update_prices()
    
    def is_market_open(self):
        india_tz = pytz.timezone('Asia/Calcutta')
        current_time = datetime.now(india_tz)
        
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if current_time.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # NSE market hours: 9:15 AM to 3:30 PM
        market_start = datetime.strptime('09:15', '%H:%M').time()
        market_end = datetime.strptime('15:30', '%H:%M').time()
        current_time = current_time.time()
        
        return market_start <= current_time <= market_end
    
    def update_prices(self):
        try:
            for name, symbol in self.symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    # Get 2 days of data regardless of market status
                    data = ticker.history(period="2d")
                    
                    if len(data) >= 2:  # Make sure we have enough data
                        current_price = data['Close'].iloc[-1]
                        prev_close = data['Close'].iloc[-2]
                        
                        # Calculate changes
                        price_change = current_price - prev_close
                        pct_change = (price_change / prev_close) * 100
                        
                        # Format the price with the appropriate number of decimal places
                        if current_price >= 100:
                            price_text = f"₹{current_price:.1f}"
                        else:
                            price_text = f"₹{current_price:.2f}"
                        
                        # Update price label
                        self.price_labels[symbol].config(
                            text=price_text,
                            foreground="green" if price_change > 0 else "red"
                        )
                        
                        # Update change label
                        change_text = f"{price_change:+.2f} ({pct_change:+.2f}%)"
                        self.change_labels[symbol].config(
                            text=change_text,
                            foreground="green" if price_change > 0 else "red"
                        )
                    else:
                        self.price_labels[symbol].config(text="No data")
                        self.change_labels[symbol].config(text="--")
                        
                except Exception as e:
                    print(f"Error updating {name}: {e}")
                    self.price_labels[symbol].config(text="Error")
                    self.change_labels[symbol].config(text="--")
        
        except Exception as e:
            print(f"Major error in update: {e}")
        
        # Update every 1 second during market hours, otherwise every minute
        update_interval = 500 if self.is_market_open() else 60000
        self.root.after(update_interval, self.update_prices)

    def on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["moved"] = False

    def on_drag_motion(self, event):
        moved_x = event.x - self._drag_data["x"]
        moved_y = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + moved_x
        y = self.root.winfo_y() + moved_y
        self.root.geometry(f"+{x}+{y}")
        self._drag_data["moved"] = True

    def run(self):
        # Set initial position (you can modify these values)
        self.root.geometry("+0+0")  # Position the window at x=0, y=0, i.e top left of your screen
        self.root.mainloop()

if __name__ == "__main__":
    app = MarketTickerWidget()
    app.run()