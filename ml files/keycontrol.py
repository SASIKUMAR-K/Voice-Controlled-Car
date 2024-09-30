import serial
from pynput import keyboard
import time
import sys
from rich import print
from rich.console import Console

console = Console()

SERIAL_PORT = 'COM13'
BAUD_RATE = 9600


def create_serial_connection():
    attempts = 0
    while attempts < 3:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            console.print(
                f'[bold green]Connected to serial port {SERIAL_PORT}[/bold green]')
            return ser
        except serial.SerialException as e:
            attempts += 1
            console.print(
                f'[bold red]Connection attempt {attempts} failed:[/bold red] {e}')
            time.sleep(2)
    console.print(
        '[bold red]Failed to connect to serial port after 3 attempts[/bold red]')
    return None


ser = create_serial_connection()
if ser is None:
    raise SystemExit(
        '[bold red]Unable to establish serial connection[/bold red]')

key_mapping = {
    keyboard.Key.up: '1',
    keyboard.Key.down: '2',
    keyboard.Key.right: '3',
    keyboard.Key.left: '4',
    'w': '1',
    's': '2',
    'd': '3',
    'a': '4',
    ' ': '0',
    'h': '5',
    'k': '6',
    'o': 'STOP'
}


pressed_keys = set()


def on_press(key):
    try:
        if hasattr(key, 'char') and key.char in key_mapping:
            if key.char not in pressed_keys:
                pressed_keys.add(key.char)
                send_key_data(key.char)
                console.print(
                    f'[bold cyan]Key pressed:[/bold cyan] {key_mapping[key.char]}')
                if key.char == 'o':
                    console.print('[bold red]Stopping program...[/bold red]')
                    return False
        elif key in key_mapping:
            if key not in pressed_keys:
                pressed_keys.add(key)
                send_key_data(key)
                console.print(
                    f'[bold cyan]Key pressed:[/bold cyan] {key_mapping[key]}')
                if key == keyboard.Key.esc:
                    console.print('[bold red]Stopping program...[/bold red]')
                    return False
    except AttributeError:
        if key in key_mapping and key not in pressed_keys:
            pressed_keys.add(key)
            send_key_data(key)
            console.print(
                f'[bold cyan]Key pressed:[/bold cyan] {key_mapping[key]}')


def on_release(key):
    try:
        if hasattr(key, 'char') and key.char in key_mapping:
            if key.char in pressed_keys:
                pressed_keys.discard(key.char)
                console.print(
                    f'[bold yellow]Key released:[/bold yellow] {key_mapping[key.char]}')
                ser.write(b'0\n')
        elif key in key_mapping:
            if key in pressed_keys:
                pressed_keys.discard(key)
                console.print(
                    f'[bold yellow]Key released:[/bold yellow] {key_mapping[key]}')
                ser.write(b'0\n')
    except AttributeError:
        if key in key_mapping:
            if key in pressed_keys:
                pressed_keys.discard(key)
                console.print(
                    f'[bold yellow]Key released:[/bold yellow] {key_mapping[key]}')
                ser.write(b'0\n')


def send_key_data(key):
    if key in key_mapping:
        ser.write((key_mapping[key] + '\n').encode())


try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    pass

ser.close()
