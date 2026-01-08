import random

COLORS = [
    "\033[31m",
    "\033[32m",
    "\033[33m",
    "\033[34m",
    "\033[35m",
    "\033[36m",
    "\033[91m",
    "\033[92m",
]
RESET = "\033[0m"

CHEST_COST = 200
MIN_BET_FLOOR = 50
HIGH_BET_BONUS_1 = 300
HIGH_BET_BONUS_2 = 600

CHEST_ITEMS = [
    "nothing",
    "double_dice",
    "double_money",
    "reroll",
    "swap",
    "add_1",
    "add_3",
    "minus_1",
    "minus_3",
    "triple_dice",
    "low_bet",
]
CHEST_WEIGHTS = [40, 14, 12, 14, 5, 5, 3, 4, 2, 1, 4]
USABLE_NOW = {
    "double_dice",
    "triple_dice",
    "double_money",
    "swap",
    "add_1",
    "add_3",
    "minus_1",
    "minus_3",
    "low_bet",
}


def roll_dice(dice_mode):
    if dice_mode == "triple_dice":
        first = random.randint(1, 6)
        second = random.randint(1, 6)
        third = random.randint(1, 6)
        return first + second + third, f"dice: {first} + {second} + {third}"
    if dice_mode == "double_dice":
        first = random.randint(1, 6)
        second = random.randint(1, 6)
        return first + second, f"dice: {first} + {second}"
    value = random.randint(1, 6)
    return value, f"die: {value}"


def format_inventory(inventory):
    if not inventory:
        return "empty"
    counts = {}
    for item in inventory:
        counts[item] = counts.get(item, 0) + 1
    parts = []
    for name in sorted(counts.keys()):
        parts.append(f"{name} x{counts[name]}")
    return ", ".join(parts)


def remove_inventory_item(inventory, item):
    if item in inventory:
        inventory.remove(item)
        return True
    return False


class TerminalUI:
    def print(self, text):
        print(text)

    def prompt_int(self, prompt, min_value=None, max_value=None):
        while True:
            raw = input(prompt).strip()
            if not raw.isdigit():
                print("Enter a whole number.")
                continue
            value = int(raw)
            if min_value is not None and value < min_value:
                print(f"Enter a number >= {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Enter a number <= {max_value}.")
                continue
            return value

    def prompt_yes_no(self, prompt):
        while True:
            ans = input(prompt).strip().lower()
            if ans in {"y", "yes"}:
                return True
            if ans in {"n", "no"}:
                return False
            print("Enter y or n.")

    def prompt_choice(self, title, options):
        if not options:
            return None
        print(title)
        for idx, item in enumerate(options, 1):
            print(f"{idx}) {item}")
        print("0) none")
        choice = self.prompt_int("Choose powerup: ", 0, len(options))
        if choice == 0:
            return None
        return options[choice - 1]

    def prompt_string(self, prompt):
        return input(prompt)

    def supports_color(self):
        return True


class DiceGame:
    def __init__(self, ui):
        self.ui = ui
        self.use_color = ui.supports_color()

    def tag(self, player):
        if not self.use_color:
            return player["name"]
        return f"{player['color']}{player['name']}{RESET}"

    def choose_powerup(self, inventory):
        options = [item for item in inventory if item in USABLE_NOW]
        return self.ui.prompt_choice("Powerups you can use this round:", options)

    def cpu_choose_powerup(self, inventory, money):
        options = [item for item in inventory if item in USABLE_NOW]
        if not options:
            return None
        if money < MIN_BET_FLOOR and "low_bet" in options:
            return "low_bet"
        for item in ["double_money", "triple_dice", "double_dice", "add_3", "add_1"]:
            if item in options:
                return item
        for item in ["swap", "minus_3", "minus_1"]:
            if item in options:
                return item
        return None

    def cpu_should_buy_chest(self, money):
        if money < CHEST_COST:
            return False
        if money >= 800:
            return True
        if money <= 300:
            return False
        return random.random() < 0.5

    def cpu_choose_bet(self, money, min_bet, effects):
        if money <= min_bet:
            return money
        risk = 0.2
        if money >= 800:
            risk = 0.4
        elif money >= 400:
            risk = 0.3
        if effects["double_money"] or effects["dice_mode"] in {"double_dice", "triple_dice"}:
            risk += 0.1
        if effects["score_bonus"] >= 2:
            risk += 0.05
        risk = min(0.7, risk)
        target = int(money * risk)
        jitter = random.randint(-20, 20)
        bet = max(min_bet, min(money, target + jitter))
        return bet

    def cpu_should_reroll(self, score, dice_mode):
        thresholds = {
            "single": 3,
            "double_dice": 6,
            "triple_dice": 9,
        }
        return score <= thresholds.get(dice_mode, 3)

    def collect_players(self):
        player_count = self.ui.prompt_int("How many players (1-8)? ", 1, 8)
        human_count = player_count
        if player_count == 1:
            cpu_count = self.ui.prompt_int("How many CPU players (0-7)? ", 0, 7)
            player_count = 1 + cpu_count
            human_count = 1
        players = []
        for i in range(player_count):
            is_cpu = i >= human_count
            if is_cpu:
                name = f"CPU {i - human_count + 1}"
            else:
                name = self.ui.prompt_string(f"Player {i + 1} name:")
                name = name.strip() if name else f"Player {i + 1}"
            players.append({
                "id": i,
                "name": name,
                "money": 1000,
                "inventory": [],
                "color": COLORS[i % len(COLORS)],
                "is_cpu": is_cpu,
            })
        return players

    def choose_round_powerup(self, player):
        if player["is_cpu"]:
            chosen = self.cpu_choose_powerup(player["inventory"], player["money"])
        else:
            chosen = self.choose_powerup(player["inventory"])

        effects = {
            "dice_mode": "single",
            "score_bonus": 0,
            "minus_amount": 0,
            "use_swap": False,
            "double_money": False,
            "allow_low_bet": False,
        }

        if chosen:
            remove_inventory_item(player["inventory"], chosen)
            if chosen == "double_dice":
                effects["dice_mode"] = "double_dice"
            elif chosen == "triple_dice":
                effects["dice_mode"] = "triple_dice"
            elif chosen == "add_1":
                effects["score_bonus"] = 1
            elif chosen == "add_3":
                effects["score_bonus"] = 3
            elif chosen == "minus_1":
                effects["minus_amount"] = 1
            elif chosen == "minus_3":
                effects["minus_amount"] = 3
            elif chosen == "swap":
                effects["use_swap"] = True
            elif chosen == "double_money":
                effects["double_money"] = True
            elif chosen == "low_bet":
                effects["allow_low_bet"] = True
            self.ui.print(f"{self.tag(player)} will use {chosen} this round.")
        return effects

    def maybe_buy_chest(self, player):
        if player["money"] < CHEST_COST:
            self.ui.print(f"{self.tag(player)} not enough money for chest (cost ${CHEST_COST}).")
            return
        if player["is_cpu"]:
            buy_chest = self.cpu_should_buy_chest(player["money"])
        else:
            buy_chest = self.ui.prompt_yes_no(
                f"{player['name']} buy powerup chest for ${CHEST_COST}? (y/n)"
            )
        if not buy_chest:
            return
        player["money"] -= CHEST_COST
        powerup = random.choices(CHEST_ITEMS, weights=CHEST_WEIGHTS, k=1)[0]
        if powerup == "nothing":
            self.ui.print(f"{self.tag(player)} chest: nothing!")
            return
        player["inventory"].append(powerup)
        self.ui.print(f"{self.tag(player)} chest: {powerup} added to inventory.")

    def place_bet(self, player, effects):
        min_bet = 1 if effects["allow_low_bet"] else MIN_BET_FLOOR
        if player["money"] < min_bet:
            min_bet = player["money"]

        if player["is_cpu"]:
            bet = self.cpu_choose_bet(
                player["money"],
                min_bet,
                {
                    "dice_mode": effects["dice_mode"],
                    "score_bonus": effects["score_bonus"],
                    "double_money": effects["double_money"],
                },
            )
            self.ui.print(f"{self.tag(player)} bets ${bet}.")
        else:
            bet = self.ui.prompt_int(
                f"{player['name']} bet amount (min ${min_bet}): ",
                min_bet,
                player["money"],
            )

        player["money"] -= bet
        if bet >= HIGH_BET_BONUS_2:
            effects["score_bonus"] += 2
            self.ui.print(f"{self.tag(player)} big bet bonus +2!")
        elif bet >= HIGH_BET_BONUS_1:
            effects["score_bonus"] += 1
            self.ui.print(f"{self.tag(player)} big bet bonus +1!")
        return bet

    def maybe_use_reroll(self, player, score, effects):
        if "reroll" not in player["inventory"]:
            return score
        if player["is_cpu"]:
            use_reroll = self.cpu_should_reroll(score, effects["dice_mode"])
        else:
            use_reroll = self.ui.prompt_yes_no(f"{player['name']} use reroll? (y/n)")
        if not use_reroll:
            return score
        remove_inventory_item(player["inventory"], "reroll")
        new_score, detail = roll_dice(effects["dice_mode"])
        self.ui.print(f"{self.tag(player)} rerolled {new_score} ({detail}).")
        return new_score

    def apply_minus(self, active_players, rolls, effects_map):
        for player in active_players:
            effects = effects_map[player["id"]]
            if effects["minus_amount"] <= 0:
                continue
            opponents = [p for p in active_players if p["id"] != player["id"]]
            if not opponents:
                continue
            target = random.choice(opponents)
            rolls[target["id"]] = max(0, rolls[target["id"]] - effects["minus_amount"])
            self.ui.print(
                f"{self.tag(player)} hits {self.tag(target)} for -{effects['minus_amount']} -> "
                f"{rolls[target['id']]}.")

    def apply_swap(self, active_players, rolls, effects_map):
        for player in active_players:
            effects = effects_map[player["id"]]
            if not effects["use_swap"]:
                continue
            opponents = [p for p in active_players if p["id"] != player["id"]]
            if not opponents:
                continue
            target = random.choice(opponents)
            rolls[player["id"]], rolls[target["id"]] = rolls[target["id"]], rolls[player["id"]]
            self.ui.print(f"{self.tag(player)} swaps rolls with {self.tag(target)}.")

    def show_final_rolls(self, active_players, rolls):
        self.ui.print("Final rolls:")
        for player in active_players:
            self.ui.print(f"{self.tag(player)} -> {rolls[player['id']]}")

    def distribute_pot(self, winners, pot, effects_map):
        split = pot // len(winners)
        remainder = pot % len(winners)
        winner_tags = [self.tag(p) for p in winners]
        self.ui.print(f"\nPot: ${pot}. Winner(s): {', '.join(winner_tags)}")

        for player in winners:
            payout = split
            if remainder > 0:
                payout += 1
                remainder -= 1

            if effects_map[player["id"]]["double_money"]:
                bonus = min(payout, pot - (split * len(winners)))
                payout += bonus
                self.ui.print(f"{self.tag(player)} doubles winnings to ${payout}!")
            player["money"] += payout

    def play(self):
        self.ui.print("Dice Gamble")
        self.ui.print("Each player starts with $1000. Highest roll wins the pot.")

        seed = self.ui.prompt_string("Enter random seed (or press Enter): ")
        if seed:
            random.seed(seed)

        players = self.collect_players()
        round_num = 1
        while True:
            active_players = [p for p in players if p["money"] > 0]
            if len(active_players) <= 1:
                break

            self.ui.print(f"\n--- Round {round_num} ---")
            round_num += 1

            pot = 0
            effects_map = {}
            rolls = {}

            for player in active_players:
                self.ui.print(f"\n{self.tag(player)} has ${player['money']}")
                self.ui.print(f"{self.tag(player)} inventory: {format_inventory(player['inventory'])}")

                self.maybe_buy_chest(player)
                effects = self.choose_round_powerup(player)
                bet = self.place_bet(player, effects)

                pot += bet
                effects_map[player["id"]] = effects

            self.ui.print("\nRolling...")
            for player in active_players:
                effects = effects_map[player["id"]]
                score, detail = roll_dice(effects["dice_mode"])
                self.ui.print(f"{self.tag(player)} rolled {score} ({detail}).")

                score = self.maybe_use_reroll(player, score, effects)

                if effects["score_bonus"] > 0:
                    score += effects["score_bonus"]
                    self.ui.print(f"{self.tag(player)} bonus +{effects['score_bonus']} -> {score}.")

                rolls[player["id"]] = score

            self.apply_minus(active_players, rolls, effects_map)
            self.apply_swap(active_players, rolls, effects_map)
            self.show_final_rolls(active_players, rolls)

            highest = max(rolls.values())
            winners = [p for p in active_players if rolls[p["id"]] == highest]
            self.distribute_pot(winners, pot, effects_map)

            for player in players:
                if player["money"] <= 0:
                    self.ui.print(f"{self.tag(player)} is out of money and eliminated.")

        if len(active_players) == 1:
            winner = active_players[0]
            self.ui.print(f"\nGame over! Winner: {self.tag(winner)} with ${winner['money']}")
        else:
            self.ui.print("\nGame over! Everyone is out of money.")


def main():
    ui = TerminalUI()
    game = DiceGame(ui)
    game.play()


if __name__ == "__main__":
    main()
