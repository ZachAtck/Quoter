import tkinter as tk
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import numpy as np
from tkinter import filedialog, messagebox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class VoiceRecorder:
    def __init__(self):
        self.frames = []
        self.recording = False
        self.stream = None

        self.root = tk.Tk()
        self.root.title("Quoter")

        self.start_button = tk.Button(
            self.root, text="Start", command=self.start_recording
        )
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(
            self.root, text="Stop", command=self.stop_recording, state=tk.DISABLED
        )
        self.stop_button.pack(pady=10)

        self.text_label = tk.Label(self.root, text="Recording: False")
        self.text_label.pack(pady=10)

    def start_recording(self):
        self.recording = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.text_label.configure(text="Recording: True")

        self.frames = []
        sd.default.samplerate = 44100
        sd.default.channels = 2

        def callback(indata, frames, time, status):
            self.frames.append(indata.copy())

        self.stream = sd.InputStream(callback=callback)
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.text_label.configure(text="Recording: False")

        self.stream.stop()
        self.stream.close()

        file_name = "recorded_audio.wav"
        sf.write(file_name, np.concatenate(self.frames), samplerate=44100)

        recognizer = sr.Recognizer()

        with sr.AudioFile(file_name) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            result = messagebox.askyesno("Confirmation", "You said: " + text)
            if result:
                name = tk.simpledialog.askstring("Name", "Please enter your name:")
                email = tk.simpledialog.askstring("Email", "Please enter your email:")
                smtp_host = ''
                smtp_port = 587
                smtp_username = ''
                smtp_password = ''

                sender_email = 'zachwillfixit@gmail.com'
                html_content = f'''
                    <html>
                    <head>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                                background-color: #f2f2f2;
                            }}
                            .container {{
                                max-width: 600px;
                                margin: 0 auto;
                                padding: 20px;
                                background-color: #fff;
                                border-radius: 5px;
                                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            }}
                            h2 {{
                                color: #333;
                                text-align: center;
                                margin-bottom: 20px;
                            }}
                            p {{
                                color: #666;
                                line-height: 1.5;
                                margin-bottom: 10px;
                            }}
                            .footer {{
                                color: #999;
                                text-align: center;
                                margin-top: 20px;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h2>Offical Quote Certificate</h2>
                            <p>Congratulations, {name}!</p>
                            <p>{text}</p>
                            <p class="footer">Best regards,<br/>Zachary Weber - Founder & CEO of Quoter</p>
                        </div>
                    </body>
                    </html>
                '''

                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = email
                message['Subject'] = "Official Quote Certificate"

                message.attach(MIMEText(html_content, 'html'))

                try:
                    smtp_server = smtplib.SMTP(smtp_host, smtp_port)
                    smtp_server.ehlo()
                    smtp_server.starttls()
                    smtp_server.login(smtp_username, smtp_password)

                    smtp_server.sendmail(sender_email, email, message.as_string())
                    smtp_server.quit()

                    print(f"Certificate email sent successfully to {email}")
                except smtplib.SMTPException as e:
                    print(f"Error sending certificate: {e}")


        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print("Error; {0}".format(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.run()
