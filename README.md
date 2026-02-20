THE JUDGE

    You are The Judge. An ordinary person who stumbled upon something extraordinary... A notebook that kills.

THE JUDGE is a text-based strategy game inspired by Death Note. You play as a mysterious figure who possesses a magic notebook—anyone whose name is written in it dies of a heart attack. Your mission: survive 20 turns by eliminating criminals while evading the police. Manage your popularity, outsmart detectives, and decide who deserves to die.
🎮 Features

    Immersive text‑based gameplay with typewriter effects and dynamic news headlines.

    Unique criminals and detectives – each with a crime, danger level, and assigned investigator.

    Strategic choices – kill only the criminal, or eliminate the detective too? Every decision affects your capture risk and public opinion.

    Risk‑reward system – high‑profile criminals give bigger rewards but also increase the chance of getting caught.

    Popularity mechanic – become a folk hero (or a villain) and gain protection when the public supports you.

    Skip turns – lay low when the heat is too high (up to 5 skips per game).

    Multiple endings based on your final popularity and whether you survive.

📦 Installation

    Clone the repository
    bash

    git clone https://github.com/CesarR70/the-judge.git
    cd the-judge

    Run the game (requires Python 3.6 or higher)
    bash

    python3 the-judge.py

That's it! No external dependencies—just the Python standard library.
🕹️ How to Play

    Each turn, you are presented with a list of criminals (their crime, danger level, and the detective in charge, if any).

    Type the number of the criminal you wish to execute.

    If the criminal has a detective, you may choose to kill them too—but beware: killing detectives can backfire.

    You can also skip a turn (if your capture risk is ≥50%) to reduce heat, but it costs a skip and lowers your popularity slightly.

    Your goal: survive 20 turns without letting your capture risk reach 100%.

⚖️ Game Mechanics
Stat	Effect
Effectiveness	Increases with each kill (higher for dangerous criminals). No direct impact, but adds to your score.
Popularity (0–100)	Affects news headlines and, above 60%, reduces capture risk each turn (police become sympathetic).
Capture Risk (0–100)	Rises when you kill; if it hits 100, you're arrested and the game ends.
Skips	You start with 5. Use them when capture risk is ≥50% to lower it by 10% (but popularity drops by 5%).
Detective kills	The first detective you kill always reduces capture risk (a "freebie"). Later kills are unpredictable—they may help or hurt. After you've killed 4 detectives, their names become hidden from you.
🧠 Tips

    Start with low‑danger criminals to build popularity safely.

    High popularity protects you—try to keep it above 60%.

    Killing detectives is a gamble; use it wisely.

    Don't be afraid to skip a turn if capture risk gets too high—it's better than being caught.

    The game gets harder as you progress; later turns introduce more dangerous criminals.

🖥️ Requirements

    Python 3.6+ (f‑strings and other modern features are used)

    Any terminal / command prompt that supports ANSI output (typewriter effects will work fine on most systems).


Enjoy your reign of justice… or terror.
The world is watching.
