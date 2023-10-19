import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import webbrowser
import datetime
import speech_recognition as sr
import pyttsx3
import os
import openai
import smtplib
from email.message import EmailMessage
import ssl
import speech_recognition as sr
import pyttsx3
from config import apikey
from calender import create_event

# Initialize Tkinter application
app = tk.Tk()
app.title("Tom A.I.")
app.geometry("800x600")
app.configure(bg="white")

# Create a scrolled text widget to show the conversation
conversation_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=70, height=15, bg="lightgray")
conversation_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Global variables for conversation history
chatStr = ""
prev_response = ""

# Function to speak out the response
def say(text):
    print(text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's voice input
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio)
        print(f"User: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Please try again.")
        return ""
    except sr.RequestError:
        print("Sorry, I'm currently unavailable. Please try again later.")
        return ""

# Function to handle voice input and display options
def process_voice_input():
    query = listen()
    if query:
        response = chat(query)
        say(response)
        update_conversation(query, response)

        # Check if the user's query contains specific commands
        if "send email" in query or "mail" in query:
            hide_all_options()  # Hide all options first
            show_email_options()
        elif "schedule" in query or "create" in query or "make an appointment" in query or "meeting" in query or "remainder" in query:
            hide_all_options()  # Hide all options first
            show_schedule_event_options()
        else:
            hide_email_options()  # Hide email options if the query is not about sending an email

# Function to update the conversation in the text widget
def update_conversation(user_query, response):
    conversation_text.insert(tk.END, "User: " + user_query + "\n")
    conversation_text.insert(tk.END, "Tom: " + response + "\n")
    conversation_text.see(tk.END)  # Auto-scroll to the end

# Function to send an email
def send_email(email_receiver, subject, body):
    email_sender = ''
    email_password = ''

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)

# Function to interact with the chatbot
def chat(query):
    global chatStr
    openai.api_key = apikey

    if "send email" in query or "mail" in query:
        return "Sure, I can help you send an email. Please provide the necessary details such as the recipient's email address, subject, and body."

    if "schedule event" in query or "meeting" in query:
        return "Sure, I can Schedule an event for you. Please provide the necessary details such as event date and time, the event must reflect in your calendar."

    prompt = f"{chatStr}Gautam: {query}\n Tom: "
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    reply = response["choices"][0]["text"]
    chatStr += f"Gautam: {query}\n Tom: {reply}\n"
    return reply

# GUI elements for email functionality
email_receiver_label = tk.Label(app, text="Recipient Email:")
email_receiver_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")

email_receiver_entry = tk.Entry(app)
email_receiver_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

subject_label = tk.Label(app, text="Subject:")
subject_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")

subject_entry = tk.Entry(app)
subject_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")

body_label = tk.Label(app, text="Body:")
body_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")

body_entry = tk.Entry(app)
body_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")

def send_email_gui():
    email_receiver = email_receiver_entry.get()
    subject = subject_entry.get()
    body = body_entry.get()

    if email_receiver and subject and body:
        send_email(email_receiver, subject, body)
        messagebox.showinfo("Success", "Email sent successfully.")
    else:
        messagebox.showwarning("Incomplete Information", "Please fill all email fields.")

send_email_button = tk.Button(app, text="Send Email", command=send_email_gui)

# GUI elements for event scheduling functionality
event_summary_label = tk.Label(app, text="Event Name:")
event_summary_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")

event_summary_entry = tk.Entry(app)
event_summary_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

start_time_label = tk.Label(app, text="Start Time (YYYY-MM-DD HH:MM):")
start_time_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")

start_time_entry = tk.Entry(app)
start_time_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")

end_time_label = tk.Label(app, text="End Time (YYYY-MM-DD HH:MM):")
end_time_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")

end_time_entry = tk.Entry(app)
end_time_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")

def schedule_event_gui():
    event_summary = event_summary_entry.get()
    start_time_input = start_time_entry.get() + ":00"
    end_time_input = end_time_entry.get() + ":00"

    if event_summary and start_time_input and end_time_input:
        # Convert user input to datetime objects
        event_start = datetime.datetime.strptime(start_time_input, '%Y-%m-%d %H:%M:%S')
        event_end = datetime.datetime.strptime(end_time_input, '%Y-%m-%d %H:%M:%S')

        # Call the create_event function from the calendar_logic module
        create_event(event_summary, event_start, event_end)

        messagebox.showinfo("Success", "Event scheduled successfully.")
    else:
        messagebox.showwarning("Incomplete Information", "Please fill all event fields.")

schedule_event_button = tk.Button(app, text="Schedule Event", command=schedule_event_gui)

# Function to display email options
def show_email_options():
    hide_all_options()
    email_receiver_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
    email_receiver_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    subject_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")
    subject_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
    body_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")
    body_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    send_email_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# Function to hide the email options
def hide_email_options():
    email_receiver_label.grid_remove()
    email_receiver_entry.grid_remove()
    subject_label.grid_remove()
    subject_entry.grid_remove()
    body_label.grid_remove()
    body_entry.grid_remove()
    send_email_button.grid_remove()

# Function to display event scheduling options
def show_schedule_event_options():
    hide_all_options()
    event_summary_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
    event_summary_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    start_time_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")
    start_time_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
    end_time_label.grid(row=7, column=0, padx=10, pady=5, sticky="e")
    end_time_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    schedule_event_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# Function to hide all email and event scheduling options
def hide_all_options():
    hide_email_options()
    event_summary_label.grid_remove()
    event_summary_entry.grid_remove()
    start_time_label.grid_remove()
    start_time_entry.grid_remove()
    end_time_label.grid_remove()
    end_time_entry.grid_remove()
    schedule_event_button.grid_remove()

# Call the hide_all_options function to hide all options initially
hide_all_options()

# GUI elements for the "Speak" button
title_label = tk.Label(app, text="Tom AI", font=("Arial", 24, "bold"), bg="white")
title_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")  # Center the title label horizontally

speak_button = tk.Button(app, text="Speak", command=process_voice_input)
speak_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

# Add padding to create a border around the GUI
app.grid_rowconfigure(0, weight=1)  # Allow row 0 to expand vertically
app.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand horizontally
app.grid_rowconfigure(2, weight=1)  # Allow row 2 to expand vertically

# Run the main application loop
app.mainloop()
