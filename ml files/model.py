import joblib
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import pandas as pd
import random
commands = {
    "forward": [
        "move forward", "go forward", "forward", "move ahead", "please move forward 10 cm",
        "advance", "step forward", "walk forward", "go straight", "move ahead 10 cm",
        "move forward quickly", "forward march", "proceed forward", "move up",
        "please go forward", "can you move forward", "move 10 cm ahead", "please go ahead 10 cm", "advance 10 cm"
    ],
    "right": [
        "turn right", "rotate right", "move to the right", "right",
        "turn to the right", "rotate to the right", "swing right", "veer right", "turn 90 degrees right",
        "move 90 degrees right", "turn 45 degrees right", "slight right turn", "hard right turn",
        "turn sharply to the right", "rotate clockwise", "right turn", "right rotation"
    ],
    "backward": [
        "move backward", "back", "go back", "please move backward",
        "retreat", "reverse", "step back", "move back", "move back 10 cm",
        "go backwards", "reverse 10 cm", "please reverse", "move backward quickly", "back up",
        "can you move backward", "move 10 cm back", "reverse back", "move back slightly"
    ],
    "left": [
        "turn left", "rotate left", "move to the left", "left",
        "turn to the left", "rotate to the left", "swing left", "veer left", "turn 90 degrees left",
        "move 90 degrees left", "turn 45 degrees left", "slight left turn", "hard left turn",
        "turn sharply to the left", "rotate counterclockwise", "left turn", "left rotation"
    ],
    "headlight on": [
        "turn on the headlight", "headlight on", "activate headlight", "switch on the headlight",
        "enable headlight", "lights on", "headlight activation", "turn headlights on",
        "switch headlights on", "turn the headlight on", "headlights on", "please turn on the headlight",
        "headlight switch on", "headlight power on", "activate headlights"
    ],
    "headlight off": [
        "turn off the headlight", "headlight off", "deactivate headlight", "switch off the headlight",
        "disable headlight", "lights off", "headlight deactivation", "turn headlights off",
        "switch headlights off", "turn the headlight off", "headlights off", "please turn off the headlight",
        "headlight switch off", "headlight power off", "deactivate headlights"
    ]
}


def generate_variations(base_commands, num_variations):
    variations = []
    noise_phrases = ["please", "kindly", "could you",
                     "would you", "can you", "might you"]
    for command in base_commands:
        for _ in range(num_variations):
            noise = random.choice(noise_phrases)
            cmd_variation = f"{noise} {command}"
            variations.append(cmd_variation)
            # Add the base command itself for diversity
            variations.append(command)
    return variations


data = []
for action, cmds in commands.items():
    variations = generate_variations(cmds, 500 // len(cmds))
    data.extend([{"command": cmd, "action": action} for cmd in variations])

for action in commands.keys():
    while len([d for d in data if d["action"] == action]) < 1000:
        cmd = random.choice(commands[action])
        data.append({"command": cmd, "action": action})

df = pd.DataFrame(data)

X_train, X_test, y_train, y_test = train_test_split(
    df['command'], df['action'], test_size=0.2, random_state=42, stratify=df['action'])


model = make_pipeline(TfidfVectorizer(), SVC(
    kernel='linear', probability=True))
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(model, 'voice_command_model.pkl')
