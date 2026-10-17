
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import mainthread, Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import threading
import yfinance as yf
import google.generativeai as genai
from plyer import tts
import re

API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

KV = '''
<MessageBubble>:
    orientation: 'vertical'
    size_hint_y: None
    height: msg_label.texture_size[1] + dp(30)
    padding: dp(15)
    canvas.before:
        Color:
            rgba: root.border_color
        Line:
            rectangle: self.x, self.y, self.width, self.height
            width: dp(1.2)
        Color:
            rgba: root.bg_color
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        id: msg_label
        text: root.msg_text
        markup: True
        font_size: '15sp'
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
        halign: 'left'

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0, 0.02, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0, 1, 1, 0.05
        Line:
            points: [self.width/2, 0, self.width/2, self.height]
            width: 1
        Line:
            points: [0, self.height/2, self.width, self.height/2]
            width: 1

    BoxLayout:
        size_hint_y: None
        height: dp(80)
        padding: dp(10)
        canvas.before:
            Color:
                rgba: 0, 0.1, 0.2, 0.8
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0, 1, 1, 0.8
            Line:
                rectangle: self.x, self.y, self.width, self.height
                width: dp(2)
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: "[b][color=#00FFFF]J.A.R.V.I.S. TRADING MAINFRAME[/color][/b]"
                markup: True
                font_size: '20sp'
            Label:
                id: bot_status
                text: "[color=#00FF00]SYSTEM ONLINE - WAITING FOR COMMAND...[/color]"
                markup: True
                font_size: '12sp'

    ScrollView:
        id: scroll
        BoxLayout:
            id: chat_history
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(15)
            spacing: dp(15)

    BoxLayout:
        size_hint_y: None
        height: dp(70)
        padding: dp(5)
        spacing: dp(5)
        canvas.before:
            Color:
                rgba: 0, 0.8, 1, 0.3
            Line:
                rectangle: self.x, self.y, self.width, self.height
                width: dp(1.5)
        TextInput:
            id: user_input
            hint_text: "Target Market likhein ya Keyboard Mic use karein..."
            multiline: False
            font_size: '16sp'
            size_hint_x: 0.8
            background_color: 0, 0.05, 0.1, 1
            foreground_color: 0, 1, 1, 1
            on_text_validate: app.process_input(self.text)
        Button:
            text: "EXEC"
            size_hint_x: 0.2
            font_size: '14sp'
            bold: True
            background_color: 0, 0.5, 0.5, 1
            color: 0, 1, 1, 1
            on_release: app.process_input(app.root.ids.user_input.text)
'''

class MessageBubble(BoxLayout):
    from kivy.properties import StringProperty, ListProperty
    msg_text = StringProperty('')
    bg_color = ListProperty([0, 0, 0, 0])
    border_color = ListProperty([0, 0, 0, 0])

class MKAgentApp(App):
    def build(self):
        self.title = "J.A.R.V.I.S Trading"
        return Builder.load_string(KV)
        
    def on_start(self):
        Clock.schedule_once(lambda dt: self.add_bubble("[color=#00FFFF]> Establishing connection to Global Markets...[/color]", is_user=False), 0.5)
        Clock.schedule_once(lambda dt: self.add_bubble("[color=#00FFFF]> Verifying Creator Identity: Mudasir Khan (Rawalpindi)... Verified.[/color]", is_user=False), 1.2)
        Clock.schedule_once(self.final_boot, 2.5)

    def final_boot(self, dt):
        intro_voice = "Mainframe initialized. Welcome back, Boss. J.A.R.V.I.S is ready to dominate the markets."
        self.add_bubble(f"[b][color=#00FFFF]J.A.R.V.I.S:[/color][/b]\n{intro_voice}", is_user=False)
        self.speak_text(intro_voice)

    def speak_text(self, text):
        clean_text = re.sub(r'\[.*?\]', '', text).replace('*', '')
        def run_tts():
            try: tts.speak(clean_text)
            except: pass
        threading.Thread(target=run_tts).start()

    def format_symbol(self, raw_symbol):
        rs = raw_symbol.upper().replace(" ", "")
        if "BTC" in rs or "BITCOIN" in rs: return "BTC-USD"
        if "ETH" in rs or "ETHEREUM" in rs: return "ETH-USD"
        if "EUR" in rs and "USD" in rs: return "EURUSD=X" 
        if "GOLD" in rs or "XAU" in rs: return "GC=F"
        return rs

    def process_input(self, text):
        if not text: return
        self.add_bubble(f"[b][color=#FFFFFF]COMMAND:[/color][/b] {text}", is_user=True)
        self.root.ids.user_input.text = ""
        self.root.ids.bot_status.text = "[color=#FFFF00]PROCESSING ALGORITHMS...[/color]"
        threading.Thread(target=self.fetch_and_analyze, args=(text,)).start()

    def fetch_and_analyze(self, raw_text):
        raw_upper = raw_text.upper()
        if any(word in raw_upper for word in ["BANAYA", "MAKER", "CREATOR", "DEVELOPER"]):
            reply = "Mere ko MK, matlab Mudasir Khan ne banaya hai, jo Rawalpindi se hain."
            display_reply = f"[color=#00FFFF]>[/color] [b]SYSTEM IDENTITY SCAN[/b]\n\n{reply}"
            self.show_reply(display_reply, reply)
            return

        symbol = self.format_symbol(raw_text)
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="1d", interval="15m")
            if hist_data.empty:
                prompt = f"Boss Mudasir Khan (Rawalpindi) ne pucha hai: '{raw_text}'. Tum J.A.R.V.I.S Trading AI ho. Exness, Binance, ya Quotex ke hawale se market news ya general tip do Roman urdu mein."
            else:
                recent_data = hist_data[['Open', 'High', 'Low', 'Close']].tail(4)
                prompt = f"""
                Tumhara naam J.A.R.V.I.S hai. Tumhe Mudasir Khan (Rawalpindi) ne banaya hai.
                Target Asset: {symbol}. Data: \n{recent_data.to_string()}
                Is data ko analyze karo aur J.A.R.V.I.S ki robotic tone (Roman Urdu) mein batao: 1. Trend 2. Advice (Buy/Sell/Hold).
                """
            response = model.generate_content(prompt)
            reply = response.text
            display_reply = f"[color=#00FFFF]>[/color] [b]SCAN COMPLETE ({symbol})[/b]\n\n{reply}"
        except:
            reply = "Sir, global servers se connect hone mein error aa raha hai."
            display_reply = f"[color=#FF0000]ERROR:[/color] {reply}"
            
        self.show_reply(display_reply, reply)

    @mainthread
    def show_reply(self, display_text, spoken_text):
        self.root.ids.bot_status.text = "[color=#00FF00]SYSTEM ONLINE - WAITING FOR COMMAND...[/color]"
        self.add_bubble(display_text, is_user=False)
        self.speak_text(spoken_text)

    @mainthread
    def add_bubble(self, text, is_user=False):
        bg = [0.02, 0.05, 0.1, 1] if is_user else [0, 0.05, 0.05, 0.8]
        border = [0, 0.5, 1, 0.5] if is_user else [0, 1, 1, 0.5]
        self.root.ids.chat_history.add_widget(MessageBubble(msg_text=text, bg_color=bg, border_color=border))
        Clock.schedule_once(lambda dt: setattr(self.root.ids.scroll, 'scroll_y', 0), 0.1)

if __name__ == '__main__':
    MKAgentApp().run()
