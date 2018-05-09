
class RectRegion2D:
    """Represent a rectangle."""

    def __init__(self, position, shape):
        self.position = np.array(position[:2])
        self.shape = np.array(shape[:2])

    def contains(self, point):
        """Check whether a point is in the rectangle."""
        for a, b, p in zip(self.position, self.shape, point):
            if p < a:
                break
            if p > a + b:
                break
        else:
            return True
        return False


class ImageButton:
    """A button the can render itself to an image.
    The button takes an image and uses it as the background of the button.
    When the mouse hovers over the button its border will change color."""

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

