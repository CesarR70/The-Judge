#!/usr/bin/env python3
"""
THE JUDGE - A Death Note inspired text-based game
You are "The Judge" - a mysterious figure with a magic notebook that kills anyone via heart attack.
Your goal: Survive 20 turns without being arrested by the police.
"""

import random
import time
import sys

# Game configuration
MAX_TURNS = 20
MAX_SKIPS = 5  # Maximum number of times player can skip a turn
DETECTIVE_HUNT_PENALTY = 25
BASE_CAPTURE_CHANCE = 5
POPULARITY_PROTECTION_THRESHOLD = 60  # Above this, police are secretly sympathetic
POPULARITY_PROTECTION_BONUS = 15  # Capture risk reduction per turn with high popularity
CAPTURE_RISK_SKIP_THRESHOLD = 50  # Above this, can skip turn
CAPTURE_RISK_SKIP_REDUCTION = 10  # How much skip reduces capture risk
POPULARITY_SKIP_PENALTY = 5  # How much skip reduces popularity
DETECTIVE_NAMES_HIDDEN_THRESHOLD = 4  # Hide detective names after this many kills

class Criminal:
    def __init__(self, name, crime, danger_level, detective_in_charge=None):
        self.name = name
        self.crime = crime
        self.danger_level = danger_level  # 1-10 scale
        self.detective_in_charge = detective_in_charge

class Game:
    def __init__(self):
        self.turn = 1
        self.effectiveness = 0  # How successful your kills are
        self.popularity = 0    # Online popularity (0-100)
        self.capture_risk = 0  # Police likelihood to catch you (0-100)
        self.killed_detectives = 0
        self.current_criminals = []
        self.game_over = False
        self.won = False
        self.executed_names = set()  # Track all executed names (criminals + detectives) to avoid repeats
        self.turns_with_high_popularity = 0  # Track how long player has had high popularity
        self.skips_remaining = MAX_SKIPS  # Number of skips left
        
    def type_text(self, text, delay=0.02):
        """Typewriter effect for dramatic text"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
        
    def slow_print(self, text, delay=0.03):
        """Slower typewriter for important messages"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
        
    def generate_criminals(self):
        """Generate criminals for the current turn"""
        self.current_criminals = []
        
        # Criminal database - higher danger = more risk but more reward
        criminal_database = [
            # Low danger (1-3) - Tutorial and early turns
            ("Marcus Webb", "Petty theft and fraud", 1),
            ("Danny 'Snake' Morrison", "Drug dealing", 2),
            ("Victor Crane", "Assault and robbery", 2),
            ("Jimmy 'The Rat' Franklin", "Informant for gang", 2),
            ("Tina Brooks", "Embezzlement", 1),
            ("Billy Bob Henderson", "DUI and hit-and-run", 1),
            ("Chuck 'The Sneak' Miller", "Burglary ring operator", 2),
            ("Petey 'Two-Times' O'Neil", "Identity theft", 1),
            ("Gambling Jim Malone", "Illegal gambling operation", 2),
            ("Ruth 'The Mom' Henderson", "Child neglect and abuse", 3),
            
            # Medium danger (4-6) - Mid game
            ("Rico 'The Hammer' Santana", "Organized crime - several murders", 4),
            ("Dr. Harold Blackwood", "Illegal human experimentation", 5),
            ("Commander Zara Khan", "Military coup attempt, treason", 6),
            ("Silas 'Deadshot' Nash", "Serial killer - 12 victims", 5),
            ("The Crimson Queen", "International drug cartel leader", 6),
            ("Vinnie 'The Beast' Caruso", "Loan shark, extortionist", 4),
            ("Dr. Patricia Crane", "Black market organ trafficking", 5),
            ("Frankie 'Fingers' Delano", "Master pickpocket, crime boss", 4),
            ("Mayor 'Greedy' John Sullivan", "Corruption, bribery, kickbacks", 5),
            ("Dr. Irving Moss", "Deadly vaccine trials on homeless", 6),
            
            # High danger (7-8) - Late game
            ("General Marcus 'Iron' Sterling", "Military dictator, mass atrocities", 8),
            ("Viktor Volkov", "Terrorist mastermind, nuclear threats", 8),
            ("Elena 'The Spider' Vasquez", "Global human trafficking network", 7),
            ("Dr. Noah Crain", "Bio-weapon developer, mass murder", 7),
            ("Admiral Hector Stone", "Navy officer selling state secrets", 7),
            ("The Syndicate Leader 'Mr. White'", "Global crime syndicate", 8),
            ("Professor Death", "Creating deadly plagues for ransom", 8),
            
            # Extreme danger (9-10) - Final turns
            ("President Richard 'The Puppet' Masters", "Global oligarch controlling governments", 10),
            ("The Architect", "AI terrorist threatening world security", 9),
            ("Kingpin Zero", "Shadow ruler of global crime, unreachable", 10),
        ]
        
        # Detective database - to ensure no repeats
        detective_database = [
            "Detective Sarah Chen", "Detective James Rodriguez", "Detective Michael Torres",
            "Captain Lisa Nakamura", "Detective David Kim", "Inspector General Maria Santos",
            "Chief Superintendent Arthur Black", "Detective Emma Watson",
            "Agent Frank Morrison", "Commander Helen Price", "Detective Robert 'Bob' Williams",
            "Special Agent Catherine 'Cat' Grant", "Detective Luis Fernandez",
            "Chief Inspector Yuki Tanaka", "Detective Anna Kowalski"
        ]
        
        # Determine number and difficulty of criminals based on turn
        if self.turn == 1:
            # Tutorial - just one easy target (don't add detective to executed yet)
            self.current_criminals.append(Criminal("Marcus Webb", "Petty theft and fraud", 1, "Detective Sarah Chen"))
            return
            
        num_criminals = min(3, 2 + (self.turn // 5))  # 2-3 criminals per turn
        
        # Select criminals appropriate for turn difficulty, excluding already executed ones
        if self.turn <= 5:
            pool = [c for c in criminal_database if c[2] <= 5]
        elif self.turn <= 12:
            pool = [c for c in criminal_database if c[2] >= 2 and c[2] <= 8]
        else:
            pool = [c for c in criminal_database if c[2] >= 3]
        
        # Filter out already executed names (criminals only, not detectives)
        available_criminals = [c for c in pool if c[0] not in self.executed_names]
        
        if len(available_criminals) < num_criminals:
            # Add more criminals if we don't have enough
            all_remaining = [c for c in criminal_database if c[0] not in self.executed_names]
            available_criminals = all_remaining
        
        if not available_criminals:
            # Game is out of criminals - generate random ones
            available_criminals = criminal_database[:3]
        
        selected = random.sample(available_criminals, min(num_criminals, len(available_criminals)))
        
        # Get available detectives (not in executed names)
        available_detectives = [d for d in detective_database if d not in self.executed_names]
        
        # If running low on detectives, reset the pool (they can be reassigned)
        if len(available_detectives) < num_criminals:
            available_detectives = detective_database
        
        used_detectives = []
        for name, crime, danger in selected:
            # Sometimes no detective assigned (for higher profile cases)
            if danger >= 7 and random.random() < 0.5:
                detective = None
            else:
                if available_detectives:
                    detective = random.choice(available_detectives[:min(len(available_detectives), 5)])
                    used_detectives.append(detective)
                    # Remove used detective from available
                    if detective in available_detectives:
                        available_detectives.remove(detective)
                else:
                    detective = None
            self.current_criminals.append(Criminal(name, crime, danger, detective))
        
        random.shuffle(self.current_criminals)
    
    def display_intro(self):
        """Display game introduction"""
        print("\n" + "="*60)
        print("                    THE JUDGE")
        print("="*60)
        print()
        self.type_text("You are The Judge.")
        time.sleep(0.5)
        self.type_text("An ordinary person who stumbled upon something extraordinary...")
        time.sleep(0.5)
        self.type_text("A notebook that kills.")
        time.sleep(0.5)
        self.slow_print("\nThe NOTEBOOK OF DEATH.")
        time.sleep(0.5)
        self.type_text("\nAnyone whose name is written in this notebook dies of a heart attack.")
        self.type_text("You are the judge, jury, and executioner.")
        self.type_text("Only YOU can decide who deserves to die.")
        print()
        print("-" * 60)
        self.slow_print("RULES:")
        self.type_text("• Write a criminal's name to execute them")
        self.type_text("• Each turn, choose who to judge (or skip)")
        self.type_text("• Higher profile criminals = more risk, more reward")
        self.type_text("• Killing detectives has varying consequences")
        self.type_text("• If capture risk reaches 100%, you're caught")
        self.type_text("• You can skip up to 5 turns to reduce capture risk")
        self.type_text("• Survive 20 turns to win")
        print("-" * 60)
        print()
        input("Press Enter to begin your reign of justice...")
        print()
    
    def display_turn(self):
        """Display current turn information"""
        print("\n" + "="*60)
        print(f"                    TURN {self.turn} OF {MAX_TURNS}")
        print("="*60)
        
        # Show world status - 4 levels now
        print(f"\n🌐 ONLINE PUBLIC OPINION:")
        if self.popularity < 30:
            print("   [██░░░░░░░░░░░░░░░░░░░░░] People debate your existence")
        elif self.popularity < 50:
            print("   [██████████░░░░░░░░░░░░░░] Some see you as a necessary evil")
        elif self.popularity < 70:
            print("   [██████████████░░░░░░░░░░] People debate if you're hero or villain")
        elif self.popularity < 90:
            print("   [████████████████████░░░░] People describe you as an invisible hero")            
        else:
            print("   [████████████████████] People worship you as a god!")
        
        # Show capture risk and skip info
        if self.capture_risk >= CAPTURE_RISK_SKIP_THRESHOLD and self.skips_remaining > 0:
            print(f"\n⚠️  HIGH CAPTURE RISK: {self.capture_risk}%!")
            print(f"   You can skip this turn ({self.skips_remaining} skips remaining)")
        elif self.skips_remaining == 0:
            print(f"\n⚠️  CAPTURE RISK: {self.capture_risk}%")
            print("   Your ego won't let you skip anymore...")
        
        print(f"\n📺 NEWS HEADLINE:")
        self.generate_news_headline()
        
        print("\n" + "-"*60)
        self.slow_print("TODAY'S TARGETS:")
        print("-"*60)
        
        for i, criminal in enumerate(self.current_criminals, 1):
            print(f"\n  [{i}] {criminal.name}")
            print(f"      Crime: {criminal.crime}")
            print(f"      Danger Level: {'★' * criminal.danger_level}{'☆' * (10 - criminal.danger_level)}")
            if self.killed_detectives >= DETECTIVE_NAMES_HIDDEN_THRESHOLD:
                print(f"      Detective: [REDACTED - Investigation sealed]")
            elif criminal.detective_in_charge and criminal.detective_in_charge not in self.executed_names:
                print(f"      Detective: {criminal.detective_in_charge}")
            elif criminal.detective_in_charge and criminal.detective_in_charge in self.executed_names:
                print(f"      Detective: [ELIMINATED]")
            else:
                print(f"      Detective: No official assignment")
    
    def generate_news_headline(self):
        """Generate a news headline based on current game state and how long player has had high popularity"""
        
        # Track turns with high popularity
        if self.popularity >= 50:
            self.turns_with_high_popularity += 1
        
        # Base headlines for low popularity
        low_pop_headlines = [
            "MYSTERIOUS DEATHS CONTINUE - Police baffled by 'natural causes'",
            "'THE JUDGE' - Internet sleuths debate vigilante identity",
            "Another 'impossible' death rocks the criminal underworld",
            "Conspiracy theories swirl as deaths defy explanation",
            "Police admit they're 'completely stumped' by the deaths",
            "Is this the work of a serial killer? Experts debate",
            "Deaths linked to 'A Silent Judge' in online conspiracy circles",
            "Skeptics claim murders are just coincidental heart attacks",
        ]
        
        # Medium popularity headlines
        medium_pop_headlines = [
            "Online community forms cult around 'The Judge' figure",
            "'THE JUDGE' - Public divided on vigilante justice",
            "More victims fall to 'impossible' deaths",
            "Support groups form both for and against The Judge",
            "Criminal underworld trembles at The Judge's power",
            "Is The Judge a hero? Online poll shows 50/50 split",
            "Police struggle to find leads in 'Judge' case",
            "Former criminals praise The Judge's work",
        ]
        
        # High popularity headlines
        high_pop_headlines = [
            "People worship 'The Judge' as a god!",
            "'THE JUDGE' - Is this the end of crime as we know it?",
            "The Judge is untouchable - internet declares victory",
            "Entire criminal organizations surrender to authorities out of fear",
            "World leaders discuss The Judge's 'clean-up' of society",
            "The Judge has become an international phenomenon",
            "Could The Judge really be unstoppable? World wonders",
            "Police beginning to admit defeat - The Judge is winning",
        ]
        
        # Special headlines for long-term high popularity AND low capture risk
        unstoppable_headlines = [
            "ANALYSIS: Is The Judge UNSTOPPABLE? Experts say yes",
            "The Judge has operated for so long, experts wonder if they'll EVER be caught",
            "Has The Judge transcended mortal law? Philosophers weigh in",
            "Police resources drained - The Judge continues unchecked",
            "The world considers the idea of The Judge as a permanent fixture",
            "Forget Sherlock Holmes - The Judge is the perfect criminal",
            "Is The Judge a ghost? No body, no evidence, no arrests",
            "The Judge's reign appears ETERNAL - officials begin to give up hope",
        ]
        
        # Determine which headline pool to use
        high_pop_and_low_risk = (self.popularity >= 60 and self.capture_risk <= 30)
        has_been_popular = self.turns_with_high_popularity >= 5
        
        if high_pop_and_low_risk and has_been_popular and random.random() < 0.4:
            print(f"   \"{random.choice(unstoppable_headlines)}\"")
        elif self.popularity >= 60:
            print(f"   \"{random.choice(high_pop_headlines)}\"")
        elif self.popularity >= 30:
            print(f"   \"{random.choice(medium_pop_headlines)}\"")
        else:
            print(f"   \"{random.choice(low_pop_headlines)}\"")
    
    def calculate_detective_kill_risk(self):
        """Calculate capture risk change when killing a detective
        - First detective kill (killed_detectives == 0): always decreases capture risk (freebie)
        - Second+ kills: random chance to increase or decrease
        """
        if self.killed_detectives == 0:
            # First detective kill - always decreases capture risk (freebie!)
            return -random.randint(20, 40)
        else:
            # Subsequent kills - random chance
            roll = random.random()
            if roll < 0.5:
                # 50% chance to decrease
                return -random.randint(15, 30)
            else:
                # 50% chance to increase
                return random.randint(10, 30)
    
    def calculate_capture_risk(self, criminal):
        """Calculate capture risk for executing a criminal"""
        base_risk = criminal.danger_level * 2
        detective_bonus = 10 if criminal.detective_in_charge else 0
        random_factor = random.randint(-5, 10)
        return base_risk + detective_bonus + random_factor
    
    def apply_popularity_protection(self):
        """Apply capture risk reduction if popularity is high enough"""
        if self.popularity >= POPULARITY_PROTECTION_THRESHOLD:
            reduction = POPULARITY_PROTECTION_BONUS
            self.capture_risk = max(0, self.capture_risk - reduction)
            print(f"\n🛡️  PUBLIC SUPPORT IS PROTECTING YOU!")
            print(f"   Police sympathy lowers capture risk by {reduction}%")
            return True
        return False
    
    def skip_turn(self):
        """Skip the current turn to reduce capture risk"""
        print()
        self.slow_print("You choose to lay low this turn...")
        time.sleep(0.5)
        self.slow_print("The notebook remains in your pocket.")
        
        # Reduce capture risk
        self.capture_risk = max(0, self.capture_risk - CAPTURE_RISK_SKIP_REDUCTION)
        
        # Slightly reduce popularity
        self.popularity = max(0, self.popularity - POPULARITY_SKIP_PENALTY)
        
        # Use up a skip
        self.skips_remaining -= 1
        
        print(f"\n✓ You laid low - Capture Risk -{CAPTURE_RISK_SKIP_REDUCTION}%")
        print(f"✓ Public interest wanes - Popularity -{POPULARITY_SKIP_PENALTY}%")
        print(f"   ({self.skips_remaining} skips remaining)")
        
        # Random event chance
        if random.random() < 0.15:
            print("\n📺 NEWS:")
            event = random.choice([
                "The Judge seems to have gone quiet...",
                "Is The Judge done? Internet debates intensify.",
                "Police celebrate what they think is a victory."
            ])
            self.type_text(f"  {event}")
        
        self.turn += 1
        
        if self.turn > MAX_TURNS:
            self.won = True
            self.game_over = True
    
    def execute(self, criminal_index):
        """Execute the chosen criminal"""
        criminal = self.current_criminals[criminal_index]
        
        self.executed_names.add(criminal.name)
        
        print()
        self.slow_print(f"You write {criminal.name}'s name in the notebook...")
        time.sleep(1)
        self.slow_print("...")
        time.sleep(1)
        
        # Check if detective will be targeted (only if not already hidden)
        if criminal.detective_in_charge and criminal.detective_in_charge not in self.executed_names:
            if self.killed_detectives >= DETECTIVE_NAMES_HIDDEN_THRESHOLD:
                # Detective names are hidden - don't ask to kill
                pass
            else:
                print()
                self.type_text(f"The detective assigned to {criminal.name}'s case is:")
                print(f"  → {criminal.detective_in_charge}")
                kill_detective = input("\nKill the detective too? (y/n): ").strip().lower()
                
                if kill_detective == 'y':
                    self.executed_names.add(criminal.detective_in_charge)
                    self.killed_detectives += 1
                    print()
                    self.slow_print(f"You write {criminal.detective_in_charge}'s name in the notebook...")
                    time.sleep(1)
                    self.slow_print("...")
                    time.sleep(1)
                    self.slow_print(f"{criminal.detective_in_charge} clutches their chest and collapses!")
                    
                    detective_risk_change = self.calculate_detective_kill_risk()
                    # Calculate criminal's capture risk increase BEFORE applying it
                    criminal_capture_increase = self.calculate_capture_risk(criminal)
                    # Apply both changes to get the net change
                    self.capture_risk += detective_risk_change + criminal_capture_increase
                    
                    # Show the NET capture risk change (detective + criminal combined)
                    net_risk_change = detective_risk_change + criminal_capture_increase
                    if net_risk_change < 0:
                        print(f"\n✅  The police haven't made the connection yet!")
                        print(f"   Net capture risk changed by {net_risk_change}%")
                    else:
                        print(f"\n⚠️  WARNING! The investigation is getting closer!")
                        print(f"   Net capture risk increased by {net_risk_change}%!")
                    
                    # Update stats for criminal execution
                    self.effectiveness += criminal.danger_level * 2
                    self.popularity += criminal.danger_level * 3 + random.randint(5, 15)
                    
                    self.apply_popularity_protection()
                    
                    # Cap stats
                    self.popularity = min(100, self.popularity)
                    self.capture_risk = max(0, min(100, self.capture_risk))
                    
                    print(f"\n✓ Effectiveness +{criminal.danger_level * 2}")
                    print(f"✓ Popularity +{criminal.danger_level * 3 + 10}")
                    
                    if self.capture_risk >= 100:
                        self.game_over = True
                        return
                    
                    self.random_event()
                    
                    self.turn += 1
                    return
        
        # Execute the criminal (no detective killed)
        self.slow_print(f"\n{criminal.name} clutches their chest...")
        self.slow_print(f"Collapses...")
        self.slow_print("Heart attack. Dead.")
        
        # Update stats
        self.effectiveness += criminal.danger_level * 2
        self.popularity += criminal.danger_level * 3 + random.randint(5, 15)
        capture_increase = self.calculate_capture_risk(criminal)
        self.capture_risk += capture_increase
        
        self.apply_popularity_protection()
        
        # Cap stats
        self.popularity = min(100, self.popularity)
        self.capture_risk = max(0, min(100, self.capture_risk))
        
        print(f"\n✓ Effectiveness +{criminal.danger_level * 2}")
        print(f"✓ Popularity +{criminal.danger_level * 3 + 10}")
        print(f"⚠ Capture Risk +{capture_increase}%")
        
        if self.capture_risk >= 100:
            self.game_over = True
            return
        
        self.random_event()
        
        self.turn += 1
        
        if self.turn > MAX_TURNS:
            self.won = True
            self.game_over = True
    
    def random_event(self):
        """Random events that can happen"""
        if random.random() < 0.2:
            print("\n📺 BREAKING NEWS:")
            events = [
                "Your online following has grown significantly! (+20 Popularity)",
                "Police almost caught a lead! (-10 Capture Risk)",
                "A famous celebrity praised your actions! (+20 Popularity)",
                "A rival detective agency takes over the case! (+15 Capture Risk)",
            ]
            event = random.choice(events)
            self.type_text(f"  {event}")
            
            if "Popularity" in event:
                self.popularity += 20
                self.capture_risk -= 13
            if "Capture Risk -" in event:
                self.capture_risk -= 10
            if "Capture Risk +" in event:
                self.capture_risk += 15
                
            self.popularity = min(100, self.popularity)
            self.capture_risk = max(0, min(100, self.capture_risk))
    
    def display_game_over(self):
        """Display game over screen"""
        print("\n" + "="*60)
        if self.won:
            print("                    VICTORY!")
            print("="*60)
            self.slow_print("\nThe world has fallen silent.")
            time.sleep(1)
            self.slow_print("No more mysterious deaths...")
            time.sleep(1)
            self.slow_print("No more criminals dying of 'heart attacks'...")
            time.sleep(1)
            print()
            self.slow_print("The police have given up.")
            self.slow_print("The investigations have been closed.")
            self.slow_print("The world moves on, never knowing the truth...")
            print()
            self.slow_print("But The Judge is still out there.")
            self.slow_print("Watching.")
            self.slow_print("Waiting.")
            print()
            print("="*60)
            self.slow_print("YOU SURVIVED 20 TURNS!")
            print("The police could NOT stop The Judge.")
            print("  [BEST ENDING]")
            print("="*60)
        else:
            print("                    GAME OVER")
            print("="*60)
            self.slow_print("\n🚨 POLICE HAVE ARRESTED YOU! 🚨")
            print()
            self.type_text("They found the notebook.")
            self.type_text("They found your notes.")
            self.type_text("It's over.")
            print()
            print("-"*60)
            self.slow_print("FINAL STATS:")
            print("-"*60)
            print(f"  Turns Survived: {self.turn - 1}")
            print(f"  Effectiveness Score: {self.effectiveness}")
            print(f"  Final Popularity: {self.popularity}%")
            print(f"  Criminals Executed: {len([n for n in self.executed_names if 'Detective' not in n and 'Agent' not in n and 'Captain' not in n and 'Commander' not in n and 'Chief' not in n and 'Inspector' not in n])}")
            print(f"  Detectives Eliminated: {self.killed_detectives}")
            print(f"  Skips Used: {MAX_SKIPS - self.skips_remaining}")
            print("-"*60)
            
            print("\n" + "="*60)
            if self.popularity < 30:
                self.slow_print("\nTHE WORLD'S FINAL VERDICT:")
                print("\" The monster is finally caught!")
                print("  The 'Judge' was just another madman.")
                print("  Justice has been served by the real courts.\"")
                print()
                print("  [WORST ENDING]")
            elif self.popularity < 70:
                self.slow_print("\nTHE WORLD'S FINAL VERDICT:")
                print("\" The Judge is gone, but the debate continues.")
                print("  Was he a hero or a villain?")
                print("  Perhaps we'll never know...\"")
                print()
                print("  [BAD ENDING]")
            else:
                self.slow_print("\nTHE WORLD'S FINAL VERDICT:")
                print("\" The Judge has vanished!")
                print("  Is he dead? In hiding? A god ascended to heaven?")
                print("  The world mourns their guardian angel.\"")
                print("  Flowers and candles appear at monuments worldwide.")
                print()
                print("  [GOOD ENDING]")
            print("="*60)
    
    def play(self):
        """Main game loop"""
        self.display_intro()
        
        while not self.game_over:
            self.generate_criminals()
            self.display_turn()
            
            valid_choice = False
            while not valid_choice:
                try:
                    # Show skip option if capture risk is high and skips remain
                    if self.capture_risk >= CAPTURE_RISK_SKIP_THRESHOLD and self.skips_remaining > 0:
                        choice = input(f"\nWho will you judge? (Enter number, 's' to skip [{self.skips_remaining} left], or 'q' to quit): ").strip().lower()
                    else:
                        choice = input("\nWho will you judge? (Enter number or 'q' to quit): ").strip()
                    
                    if choice.lower() == 'q':
                        print("\nYou put away the notebook... for now.")
                        return
                    
                    # Handle skip turn
                    if choice.lower() == 's' and self.capture_risk >= CAPTURE_RISK_SKIP_THRESHOLD and self.skips_remaining > 0:
                        valid_choice = True
                        self.skip_turn()
                        continue
                    elif choice.lower() == 's' and self.skips_remaining == 0:
                        print("Your ego won't let you skip anymore! You've used all 5 skips.")
                        continue
                    elif choice.lower() == 's' and self.capture_risk < CAPTURE_RISK_SKIP_THRESHOLD:
                        print("You can't skip yet. Capture risk is below 50%.")
                        continue
                    
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < len(self.current_criminals):
                        valid_choice = True
                        self.execute(choice_num)
                    else:
                        print("Invalid choice. Please enter a valid number.")
                except ValueError:
                    print("Please enter a number.")
            
            if self.turn > MAX_TURNS:
                self.won = True
                self.game_over = True
        
        self.display_game_over()

if __name__ == "__main__":
    game = Game()
    game.play()
