import os
import time
import re
import keyboard
import joblib
import serial
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from vosk import Model, KaldiRecognizer
import pyaudio

model = joblib.load('voice_command_model.pkl')

script_dir = os.path.dirname(os.path.abspath(__file__))
vosk_model_path = os.path.join(script_dir, 'vosk-model-en-in-0.5')

if not os.path.exists(vosk_model_path):
    print("Vosk model directory not found.")
    exit(1)

vosk_model = Model(vosk_model_path)

forward_backward_delay_factor = 22 / 1000
left_right_delay_factor = 9 / 1000

number_words = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
}

command_mapping = {
    "forward": "1",
    "backward": "2",
    "right": "3",
    "left": "4",
    "headlight on": "5",
    "headlight off": "6"
}

console = Console()

port = 'COM13'
baud_rate = 9600
ser = None


def display_welcome_message():
    pattern = '''
***********************
*  Welcome to Robot   *
***********************
    '''
    console.print(Panel.fit(
        pattern, title="[bold cyan]Welcome[/bold cyan]", border_style="green", width=40))


def initialize_bluetooth():
    global ser
    for attempt in range(1, 6):
        try:
            console.print(Text(
                f"Attempt {attempt}: Trying to connect to Bluetooth device...", style="bold yellow"))
            ser = serial.Serial(port, baud_rate, timeout=1)
            console.print(
                Text(f"Connected to Bluetooth on port {port}.", style="bold green"))
            return True
        except serial.SerialException as e:
            console.print(Text(f"Serial port error: {e}", style="bold red"))
            time.sleep(2)
    console.print(
        Text(f"Failed to connect to Bluetooth after 5 attempts.", style="bold red"))
    return False


def classify_command_sklearn(text):
    try:
        prediction = model.predict([text])
        command = prediction[0]
        console.print(
            Text(f"Predicted command: {command}", style="bold green"))
        return command
    except Exception as e:
        console.print(Text(f"Error in classification: {e}", style="bold red"))
        return None


def extract_distance(text):
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))

    words = text.lower().split()
    distance = 0
    for word in words:
        if word in number_words:
            distance += number_words[word]
    return distance if distance else 50


def extract_degrees(text):
    match = re.search(r'(\d+)', text)
    if match:
        return int(match.group(1))

    return 90


def process_command(text):
    commands = []
    console.print(Text(f"Processing command: {text}", style="bold yellow"))
    for cmd in text.split(' and '):
        action = classify_command_sklearn(cmd)
        if action is None:
            console.print(
                Text(f"Command '{cmd}' not recognized.", style="bold red"))
            continue

        if action in ["forward", "backward"]:
            distance = extract_distance(cmd)
            commands.append((command_mapping[action], distance))
        elif action in ["left", "right"]:
            degrees = extract_degrees(cmd)
            commands.append((command_mapping[action], degrees))
        else:
            commands.append((command_mapping[action], 0))
    return commands


def recognize_speech():
    recognizer = KaldiRecognizer(vosk_model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1,
                      rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()
    console.print(
        Text("Listening for a command...", style="bold blue"))

    while True:
        data = stream.read(4096)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = result[14:-3]
            if text == "":
                console.print(
                    Text("Sorry, I did not understand the audio.", style="bold red"))
                return None

            console.print(
                Text(f"Recognized command: {text}", style="bold green"))
            return text


def send_command(action, distance):
    if ser and ser.is_open:
        try:
            command_str = f"{action}\n"
            ser.write((command_str + '\n').encode())
            command_word = [
                k for k, v in command_mapping.items() if v == action][0]

            if command_word in ["left", "right"]:
                delay = distance * left_right_delay_factor
                console.print(Text(
                    f"Successfully sent: {command_word} with degree {distance} deg", style="bold green"))
            elif command_word in ["headlight on", "headlight off"]:
                console.print(Text(
                    f"Successfully sent: {command_word}", style="bold green"))
                delay = 0
            else:
                delay = distance * forward_backward_delay_factor
                console.print(Text(
                    f"Successfully sent: {command_word} with distance {distance} cm", style="bold green"))

            time.sleep(delay)
            send_stop_command()

        except Exception as e:
            console.print(
                Text(f"Failed to send command: {e}", style="bold red"))
    else:
        console.print(
            Text("Bluetooth connection is not established.", style="bold red"))


def send_stop_command():
    try:
        ser.write("0\n".encode())
        console.print(
            Text("Stop command sent successfully.", style="bold green"))
    except Exception as e:
        console.print(
            Text(f"Failed to send stop command: {e}", style="bold red"))


def main():
    display_welcome_message()

    if not initialize_bluetooth():
        return

    while True:
        if keyboard.is_pressed('o'):
            console.print(
                Text("Program terminated by user.", style="bold red"))
            break

        text = recognize_speech()
        if text is not None:
            commands = process_command(text)
            for command, value in commands:
                send_command(command, value)


if __name__ == "__main__":
    main()
