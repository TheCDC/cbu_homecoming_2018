#!/usr/bin/env python3
import evil_rock_paper_scissors as evilrps
import cv2
import numpy as np
import enum
import random
import os
from collections import defaultdict
from opencv_gui_utils import ImageButton, FaceFinder

face_classifier = FaceFinder()


class GameStates(enum.Enum):
    """Enumerate states of the game with respect to the UI."""
    playing = 'playing'
    player_lose = 'lose'
    player_win = 'win'


# these messages appear on the screen
messages = {
    GameStates.playing: [''],
    GameStates.player_lose: [
        '"Is it cheating?" - you',
        'How embarrassing',
        'What would your mother say?',
    ],
    GameStates.player_win:
    ['The face of a champion', 'The face of a winner', 'You did it!'],
}


class GameManager:
    """Manage UI state and rendering based on an rps game."""

    def __init__(self, camera):
        self.state = GameStates.playing
        self.window_name = "Evil Rock Paper Scissors"
        self.camera = camera
        ret, self.frame = self.camera.read()
        self.last_frame = self.frame.copy()
        self.player_choice = evilrps.Throws.rock
        self.human = evilrps.Player('Human', self.get_player_choice)
        self.ai = evilrps.Player('AI', evilrps.create_ai())
        self.game = evilrps.Game(self.human, self.ai)
        self.images = {
            evilrps.Throws.rock:
            cv2.imread(os.path.join('img', 'rock128.png')),
            evilrps.Throws.paper:
            cv2.imread(os.path.join('img', 'paper128.png')),
            evilrps.Throws.scissors:
            cv2.imread(os.path.join('img', 'scissors128.png')),
        }

        self.buttons = defaultdict(list)
        # first dim is num rows, second dim is col values
        frame_height, frame_width, _ = self.frame.shape

        def create_callback(throw, rand=False):
            """Return a callback that sets the player's choice."""
            obj = self
            r = rand

            def wrapped(widget):
                """Set the player's throw."""
                if r:
                    obj.player_choice = random.choice(list(evilrps.Throws))
                else:
                    # print(widget, 'throw', throw)
                    obj.player_choice = throw
                obj.advance()

            return wrapped

        # instantiate the rock, paper, scissors, buttons
        for index, label in enumerate(evilrps.Throws):
            image = self.images[label]
            w, h, _ = image.shape
            offset = w // 4
            x = index * (frame_width // (len(self.images))) + offset
            y = frame_height - h

            p = (x, y)
            p = (0, 0)

            self.buttons[GameStates.playing].append(
                ImageButton(
                    window_name=self.window_name,
                    position=p,
                    image=image,
                    callback=create_callback(label),
                    name=label))
        # instantiate the random move button
        self.buttons[GameStates.playing].append(
            ImageButton(
                window_name=self.window_name,
                position=p,
                image=cv2.imread(os.path.join('img', 'dice128.png')),
                callback=create_callback(0, rand=True),
                name='Random'))
        # re calculate button positions
        for index, btn in enumerate(self.buttons[GameStates.playing]):
            image = btn.image
            w, h, _ = image.shape
            offset = w // 4
            offset = 0
            x = index * (frame_width //
                         (len(self.buttons[GameStates.playing]))) + offset
            y = frame_height - h

            p = (x, y)
            print(p)
            btn.rect.position = p

        img = cv2.imread(os.path.join('img', 'restart128.png'))
        restart_btn = ImageButton(
            window_name=self.window_name,
            position=(640 - img.shape[0], 0),
            image=img,
            callback=self.reset,
            name='Reset')
        self.buttons[GameStates.player_lose].append(restart_btn)
        self.buttons[GameStates.player_win].append(restart_btn)

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.handle_event)
        self.mouse_position = (0, 0)

    def get_player_choice(self, opponent_previous_move):
        """Used for callbacks."""
        return self.player_choice

    def handle_event(self, *args):
        """Callback for opencv."""
        x, y = args[1:3]
        # print(event)
        self.mouse_position = (x, y)
        for b in self.buttons[self.state]:
            b.handle_event(*args)

    def advance(self):
        """Advance the rps game state."""
        self.game.advance()
        print(self.game.scores, 'predicted:', self.ai.move(None))

    def reset(self, *args):
        """Completely reset the game."""
        self.state = GameStates.playing
        self.human = evilrps.Player('Human', self.get_player_choice)
        self.ai = evilrps.Player('AI', evilrps.create_ai())
        self.game = evilrps.Game(self.human, self.ai)

    def main(self):
        """Main loop."""
        while True:
            key = cv2.waitKey(1)

            if key == 27:  # exit on ESC

                break

            rval, self.frame = self.camera.read()
            player_score, ai_score = self.game.scores
            # detect faces in the image and draw squares over them
            face_rects = face_classifier.find_face_locations(self.frame)
            for (x, y, w, h) in face_rects:
                cv2.rectangle(self.frame, (x, y), (x + w, y + h),
                              (255, 128, 0), 3)
            # normal game play
            if self.state == GameStates.playing:
                # check for a winner
                if player_score - ai_score >= 10:
                    self.picture = self.frame.copy()
                    self.state = GameStates.player_win
                elif ai_score - player_score >= 10:
                    self.picture = self.frame.copy()
                    self.state = GameStates.player_lose

                # decide font color based on who is winning
                if self.game.scores[0] > self.game.scores[1]:
                    status_color = [0, 255, 0]
                else:
                    status_color = [0, 0, 255]
                # generate scoreboard string
                message = ' '.join([
                    f'{p.name}: {s}'
                    for p, s in zip(self.game.players, self.game.scores)
                ]) + f' draw: {self.game.draws}'
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(self.frame, message, (0, 50), font, 1,
                            status_color, 2, cv2.LINE_AA)
                # don't draw the current move if there isn't one
                if all(self.game.previous_moves):
                    message = ' vs. '.join(
                        t.name for t in self.game.previous_moves)
                    cv2.putText(self.frame, message, (0, 100), font, 1,
                                (0, 255, 155), 2, cv2.LINE_AA)
                # choose a message based on the game state
                try:
                    self.message = random.choice(messages[self.state])
                except IndexError:
                    pass
            # player has won or lost
            elif self.state in [GameStates.player_win, GameStates.player_lose]:
                self.frame = self.picture
                cv2.putText(self.frame, self.message, (0, 100), font, 1,
                            (0, 255, 155), 2, cv2.LINE_AA)
            for b in self.buttons[self.state]:
                b.draw(
                    target_image=self.frame, mouse_coords=self.mouse_position)
            cv2.imshow(self.window_name, self.frame)


def main():
    camindex = -1
    cam = cv2.VideoCapture(camindex)
    rval, frame = cam.read()
    if not rval:
        raise RuntimeError(f'Bad camera ({camindex})!')
    manager = GameManager(cam)
    manager.main()


if __name__ == '__main__':
    main()
