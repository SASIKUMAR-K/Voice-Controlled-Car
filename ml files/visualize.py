import joblib
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns
from rich import print
from rich.console import Console
from rich.table import Table
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
import numpy as np

console = Console()

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


def generate_variations(commands, num_variations):
    variations = []
    for cmd in commands:
        for _ in range(num_variations):
            variations.append(cmd)
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

df['command'] = df['command'].astype(str)

label_encoder = LabelEncoder()
df['encoded_action'] = label_encoder.fit_transform(df['action'])

X_train, X_test, y_train, y_test = train_test_split(
    df['command'], df['encoded_action'], test_size=0.2, random_state=42, stratify=df['encoded_action'])

model = make_pipeline(TfidfVectorizer(), SVC(
    kernel='linear', probability=True))
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
report = classification_report(y_test, y_pred, output_dict=True)

table = Table(show_header=True, header_style="bold magenta")
table.add_column("Class")
table.add_column("Precision")
table.add_column("Recall")
table.add_column("F1-Score")
table.add_column("Support")

for label, metrics in report.items():
    if label in ['accuracy', 'macro avg', 'weighted avg']:
        continue
    table.add_row(
        label,
        f"{metrics['precision']:.2f}",
        f"{metrics['recall']:.2f}",
        f"{metrics['f1-score']:.2f}",
        f"{metrics['support']}"
    )

console.print(table)

fig1, ax1 = plt.subplots(figsize=(8, 6))
cm = ConfusionMatrixDisplay.from_estimator(
    model, X_test, y_test, cmap=plt.cm.Blues, normalize='true', ax=ax1
)
ax1.set_title('Confusion Matrix')
plt.show(block=False)

fig2, ax2 = plt.subplots(figsize=(10, 7))
df_report = pd.DataFrame(report).transpose()
sns.heatmap(df_report[['precision', 'recall', 'f1-score']
                      ].astype(float), annot=True, cmap='Blues', fmt='.2f', ax=ax2)
ax2.set_title('Classification Report Heatmap')
plt.show(block=False)


def plot_svm_boundary(X, y, model):
    pca = PCA(n_components=2)
    X_reduced = pca.fit_transform(X)

    model_svm = SVC(kernel='linear')
    model_svm.fit(X_reduced, y)

    unique_labels = np.unique(y)
    colormap = plt.get_cmap('viridis', len(unique_labels))

    h = .02
    x_min, x_max = X_reduced[:, 0].min() - 1, X_reduced[:, 0].max() + 1
    y_min, y_max = X_reduced[:, 1].min() - 1, X_reduced[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    Z = model_svm.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    fig3, ax3 = plt.subplots(figsize=(10, 7))
    ax3.contourf(xx, yy, Z, alpha=0.8, cmap=colormap)

    scatter = ax3.scatter(
        X_reduced[:, 0], X_reduced[:, 1], c=y, cmap=colormap, edgecolor='k', s=50)

    labels = label_encoder.inverse_transform(unique_labels)
    handles, _ = scatter.legend_elements(num=len(unique_labels))
    ax3.legend(handles, labels, title="Commands")

    ax3.set_title('SVM Decision Boundary')
    plt.show()


vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['command'])
plot_svm_boundary(X, df['encoded_action'], model)
