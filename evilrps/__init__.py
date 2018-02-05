#!/usr/bin/env python3

# rock paper scissors game which models the player as a markov chain
# and uses it to predict their next move
import pymarkoff
import random
import string
import json
import os
# possible moves

throw_types = [
    "R",
    "S",
    "P",
]
throw_to_name = {"R": "Rock", "P": "Paper", "S": "Scissors"}
# what beats what/does X beat Y?
beats = {
    "R": "S",
    "S": "P",
    "P": "R",
}
beaten_by = {beats[i]: i for i in beats.keys()}

# game loop needs to always ask a player for a throw
# initially, there is no history of throws
# let the player make an arbitrary number of throws at the beginning
# before beginning to model them.


class QuitError(Exception):
    pass


def user_move():
    """Ask a user for their move.
    Sanitizes input."""
    response = ''
    while True:
        try:
            response = input(
                "What's your move? (r)ock, (p)aper, (s)cissors, or q to quit\n>>>"
            ).strip().upper()
        except (KeyboardInterrupt, EOFError):
            raise QuitError("Interrupted")
        if response == 'Q':
            raise QuitError("Quit requested")
        if response not in throw_types:
            print("That's not a valid move...")
        else:
            break
    return response


def pc_choose(samples, brain):
    """Return the ai's next move based on
    markov model of previous moves."""
    try:
        prev = samples[-1]
        # print("Trying to predict based on", prev)
        predicted_player_move = brain.get_next((prev, ))
        # print("Prediction made!")
        return beaten_by[predicted_player_move[0]]
    except pymarkoff.InvalidStateError:
        # this error occurs when the latest moves haven't yet been seen

        # print("Not enough data.")
        # print(e)
        pass
    except IndexError as e:
        # this error occurs on the first move because there aren't enough samples.
        # print("Not enough samples.")
        # print(e)
        pass
    return random.choice(throw_types)


def filter_name(s):
    """Return safe version of user's name."""
    allowed = string.ascii_letters + string.digits + ' '
    return ''.join(i for i in s if i in allowed)


def main():
    brain = pymarkoff.Markov([], orders=(0, 1, 2), discrete=False)

    player_score = 0
    pc_score = 0
    try:
        player_name = filter_name(input("What is your name?\n>>>").strip())
        print("Welcome, {}!".format(player_name))
    except KeyboardInterrupt:
        print()
        print("Have a nice day!")
        quit()
    try:
        target_dir = "rps_markov_samples/"
        if not os.path.isdir("rps_markov_samples/"):
            os.makedirs(target_dir)
        filename = os.path.join(target_dir, player_name, ".txt")
        print(filename)
        with open(filename) as f:
            samples = eval(f.read())
        print("Welcome back, {}".format(player_name))
    except (FileNotFoundError, SyntaxError):
        print("Welcome to Evil Rock Paper Scissor, {}".format(player_name))
        samples = []
    while True:

        pc_choice = pc_choose(samples, brain)
        try:
            player_choice = user_move()
        except (QuitError, KeyboardInterrupt):
            with open("rps_markov_samples/" + player_name + ".txt", 'w') as f:
                f.write(str(samples))
            print()
            print("Have a nice day, {}!".format(player_name))
            # print(dict(brain))
            quit()

        samples.append((player_choice, pc_choice))
        brain.feed([samples[-3:]])
        # print(dict(brain))
        # print(samples)
        print(
            "You threw {}, the computer threw {}.".format(
                *[throw_to_name[i] for i in [player_choice, pc_choice]]),
            end=" ")

        if beats[pc_choice] == player_choice:
            print("The computer wins!")
            pc_score += 1
        elif beats[player_choice] == pc_choice:
            print("You win!")
            player_score += 1
        elif pc_choice == player_choice:
            print("Draw!")
        print("Scores: PC: {}, You: {}".format(pc_score, player_score))


if __name__ == '__main__':
    main()
