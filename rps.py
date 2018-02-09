#!/usr/bin/env python3
import evil_rock_paper_scissors as evilrps
import cv2
import numpy as np
import enum
import random


class RectRegion2D:
    def __init__(self, position, shape):
        self.position = np.array(position[:2])
        self.shape = np.array(shape[:2])

    def contains(self, point):
        for a, b, p in zip(self.position, self.shape, point):
            if p < a:
                break
            if p > a + b:
                break
        else:
            return True
        return False


class ImageButton:
    def __init__(
            self,
            window_name,
            position,
            image,
            callback,
            name='',
    ):
        self.image = image
        self.rect = RectRegion2D(np.int32(position), np.int32(image.shape))
        self.callback = callback
        self.contains = self.rect.contains
        self.window_name = window_name
        self.name = name

    def handle_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and self.rect.contains((x, y)):
            self.callback(self)

    def draw(self, target_image, mouse_coords):
        frame_width, frame_height, _ = target_image.shape

        icon = self.image
        w = icon.shape[0]
        h = icon.shape[1]
        x, y = self.rect.position
        target_image[y:y + w, x:x + h] = icon
        if self.rect.contains(mouse_coords):
            # cv2.circle(target_image, mouse_coords, 10, 255, -1)
            cv2.rectangle(target_image, tuple(self.rect.position),
                          tuple(self.rect.position + self.rect.shape),
                          (0, 255, 0), 3)
        else:
            cv2.rectangle(target_image, tuple(self.rect.position),
                          tuple(self.rect.position + self.rect.shape),
                          (255, 255, 255), 3)

        # raise ValueError('Not implemented')


class GameStates(enum.Enum):
    playing = 'playing'
    player_lose = 'lose'
    player_win = 'win'


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
            evilrps.Throws.rock: cv2.imread('res/rock128.png'),
            evilrps.Throws.paper: cv2.imread('res/paper128.png'),
            evilrps.Throws.scissors: cv2.imread('res/scissors128.png'),
        }

        print(self.images.keys())
        self.buttons = {s: list() for s in GameStates}
        # first dim is noum rows, second dim is col values
        frame_height, frame_width, _ = self.frame.shape
        print(frame_height, frame_width, _)

        def create_callback(throw, rand=False):
            obj = self
            r = rand

            def wrapped(widget):
                if r:
                    obj.player_choice = random.choice(list(evilrps.Throws))
                else:
                    # print(widget, 'throw', throw)
                    obj.player_choice = throw
                obj.advance()

            return wrapped

        for index, label in enumerate(evilrps.Throws):
            image = self.images[label]
            w, h, _ = image.shape
            offset = w // 4
            x = index * (frame_width // (len(self.images))) + offset
            assert frame_height - h == 352
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

        self.buttons[GameStates.playing].append(
            ImageButton(
                window_name=self.window_name,
                position=p,
                image=cv2.imread('res/dice128.png'),
                callback=create_callback(0, rand=True),
                name='Random'))
        for index, btn in enumerate(self.buttons[GameStates.playing]):
            image = btn.image
            w, h, _ = image.shape
            offset = w // 4
            offset = 0
            x = index * (frame_width //
                         (len(self.buttons[GameStates.playing]))) + offset
            assert frame_height - h == 352
            y = frame_height - h

            p = (x, y)
            print(p)
            btn.rect.position = p

        img = cv2.imread('res/restart128.png')
        restart_btn = ImageButton(
            window_name=self.window_name,
            position=(640 - img.shape[0], 0),
            image=img,
            callback=self.reset,
            name=label)
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
        print(self.game.scores)

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
            if self.state == GameStates.playing:
                # normal game play
                if player_score - ai_score >= 10:
                    self.picture = self.frame.copy()
                    self.state = GameStates.player_win
                elif ai_score - player_score >= 10:
                    self.picture = self.frame.copy()
                    self.state = GameStates.player_lose

                font = cv2.FONT_HERSHEY_SIMPLEX
                if self.game.scores[0] > self.game.scores[1]:
                    status_color = [0, 255, 0]
                else:
                    status_color = [0, 0, 255]
                message = ' '.join([
                    f'{p.name}: {s}'
                    for p, s in zip(self.game.players, self.game.scores)
                ]) + f' draw: {self.game.draws}'
                cv2.putText(self.frame, message, (0, 50), font, 1,
                            status_color, 2, cv2.LINE_AA)
                if all(self.game.previous_moves):
                    message = ' vs. '.join(
                        t.name for t in self.game.previous_moves)
                    cv2.putText(self.frame, message, (0, 100), font, 1,
                                (0, 255, 155), 2, cv2.LINE_AA)
                try:
                    self.message = random.choice(messages[self.state])
                except IndexError:
                    pass
            elif self.state == GameStates.player_win or self.state == GameStates.player_lose:
                # player has won or lost
                self.frame = self.picture
                cv2.putText(self.frame, self.message, (0, 100), font, 1,
                            (0, 255, 155), 2, cv2.LINE_AA)
            for b in self.buttons[self.state]:
                b.draw(
                    target_image=self.frame, mouse_coords=self.mouse_position)
            cv2.imshow(self.window_name, self.frame)


def main():
    camindex = -1
    cam = cv2.VideoCapture(0)
    rval, frame = cam.read()
    if not rval:
        raise RuntimeError(f'Bad camera ({camindex})!')
    manager = GameManager(cam)
    manager.main()


if __name__ == '__main__':
    main()
