from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import range
from past.utils import old_div
from builtins import object
import logging
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
import PIL.ImageChops
import PIL.ImageDraw
import tkinter.filedialog
import math
from collections import namedtuple


EditMode = namedtuple('EditMode', 'display value')


class ImageManager(object):
    def __init__(self):
        pass

    def open_from_dialog(self):
        path = tkinter.filedialog.askopenfilename()
        if len(path) > 0:
            self.open(path)

    def open(self, path, **kwargs):
        self.path = path
        self.load(**kwargs)
        self.draw()

    def set_path(self, path):
        self.path = path

    def draw(self):
        """Called when GUI needs to be refreshed"""

    def on_mouse_move2(self):
        pass

    def set_tk_label(self, tk_label):
        tk_label.bind('<Button-1>', self.on_mouse_down)
        tk_label.bind('<B1-Motion>', self.on_mouse_move)
        tk_label.bind('<B2-Motion>', self.on_mouse_move2)
        self.tk_label = tk_label


class SourceImageManager(ImageManager):
    """Manage source image and mask image, which is shown on the right hand
    side in the GUI.

    Attributes:
        self.path: path to source image file.
        self.image_src: PIL.Image object of source image.
        self.image_mask: PIL.Image object of mask image.
        self.edit_mode: Tkinter.StringVar(). Stores current mode selected.
    """
    EDIT_MODES = (
        EditMode('Draw', 'draw'),
        EditMode('Erase', 'erase'),
        EditMode('Move', 'move'),
    )

    def __init__(self):
        ImageManager.__init__(self)
        self.draw_propagate_functions = []
        self.ZOOM_FUNCTIONS = {
            '+': self.zoom_by_ten_percent,
            '-': self.shrink_by_ten_percent,
            'original': self.reset_size
        }

        self.path = None
        self.image_src = None
        self.image_mask = None
        self.edit_mode = None

    def set_edit_mode_str(self, edit_mode_str):
        self.edit_mode = edit_mode_str

    def add_propagation_func(self, callback_func):
        self.draw_propagate_functions.append(callback_func)

    def load(self, mask_path=None):
        self.image_src = PIL.Image.open(self.path).convert("RGB")
        if mask_path:
            self.image_mask = PIL.Image.open(mask_path).convert("L")
        else:
            self.image_mask = PIL.Image.new('L', self.image_src.size)

        self.original_size = self.image_src.size
        self.current_scale_percentage = 100

    def draw(self):
        self.image_masked_src = PIL.Image.blend(self.image_src,
                                                self.image_mask.convert("RGB"),
                                                0.3)
        self.image_tk_masked_src = PIL.ImageTk.PhotoImage(self.image_masked_src)
        self.tk_label.configure(image=self.image_tk_masked_src)
        for f in self.draw_propagate_functions:
            f()

    def on_mouse_down(self, event):
        if self.edit_mode.get() == 'move':
            self.sx, self.sy = event.x, event.y
        elif self.edit_mode.get() == 'draw':
            self.modify_mask(event.x, event.y, 255)
        elif self.edit_mode.get() == 'erase':
            self.modify_mask(event.x, event.y, 0)

    def on_mouse_move(self, event):
        if self.edit_mode.get() == 'move':
            dx = event.x - self.sx
            dy = event.y - self.sy
            self.image_mask = PIL.ImageChops.offset(self.image_mask, dx, dy)
            self.draw()

            self.sx, self.sy = event.x, event.y
        elif self.edit_mode.get() == 'draw':
            self.modify_mask(event.x, event.y, 255)
        elif self.edit_mode.get() == 'erase':
            self.modify_mask(event.x, event.y, 0)

    def modify_mask(self, x, y, new_value):
        pixel = self.image_mask.load()
        mx, my = self.image_mask.size
        for dx in range(-10, 11):
            for dy in range(-10, 11):
                nx = x + dx
                ny = y + dy
                if 0 <= nx < mx and 0 <= ny < my:
                    pixel[x + dx, y + dy] = new_value
        self.draw()

    def resize(self, new_scale):
        self.image_src = PIL.Image.open(self.path).convert("RGB")
        new_size = tuple([int(x * new_scale) for x in self.image_src.size])
        self.image_src = self.image_src.resize(new_size)
        self.image_mask = self.image_mask.resize(new_size)
        self.draw()

    def shrink_by_ten_percent(self):
        self.current_scale_percentage -= 10
        self.resize(self.current_scale_percentage / 100.0)

    def zoom_by_ten_percent(self):
        self.current_scale_percentage += 10
        self.resize(self.current_scale_percentage / 100.0)

    def reset_size(self):
        self.current_scale_percentage = 100
        self.resize(1)

    def clear_mask(self):
        yn = tkinter.messagebox.askokcancel(
            'Clear mask image',
            'Mask will be cleared, do you proceed?')
        if yn:
            self.image_mask = PIL.Image.new('L', self.image_src.size)
            self.draw()

    def save_mask_image(self):
        self.image_mask.save('mask.png')


class DestinationImageManager(ImageManager):
    """Manage destination image, the one on the left hand side in the GUI.

    Attributes:
        rotate: In degrees
        edit_mode: Tkinter.StringVar(). Stores current mode selected.
        image: A destination image as a PIL.Image object.
        src_img_cropped: Source image cropped to mask area.
        src_mask_cropped: Mask image cropped to mask area.
    """
    logger = logging.getLogger('DestinationImageManager')
    EDIT_MODE_MOVE = EditMode('Move', 'move')
    EDIT_MODE_ROTATE = EditMode('Rotate', 'rotate')
    EDIT_MODES = (EDIT_MODE_MOVE, EDIT_MODE_ROTATE)

    def __init__(self, src_img_manager):
        ImageManager.__init__(self)
        self.src_img_manager = src_img_manager
        self.src_img_manager.add_propagation_func(self.draw)

        self.image = None
        self.src_img_cropped = None
        self.src_mask_cropped = None
        self.offset = (0, 0)
        self.rotate = 0
        self.edit_mode = None

    def load(self):
        self.image = PIL.Image.open(self.path).convert("RGB")

    def draw(self):
        image_to_show = self.image.copy()
        self.draw_mask(image_to_show)

        self.image_tk = PIL.ImageTk.PhotoImage(image_to_show)
        self.tk_label.configure(image=self.image_tk)

    def draw_mask(self, image):
        """Add mask to image"""

        img_src = self.src_img_manager.image_src.copy()
        mask = self.src_img_manager.image_mask.copy()

        # Draw box around mask
        mask_bbox = self.src_img_manager.image_mask.getbbox()

        # Mask is empty, no need to draw mask
        if mask_bbox is None:
            return

        l, u, r, b = mask_bbox
        mask_bbox = l+1, u+1, r-1, b-1  # shrink bbox by 1px to avoid run out of edge
        if (mask_bbox is not None and
            self.edit_mode.get() == self.EDIT_MODE_ROTATE.value):
            draw = PIL.ImageDraw.Draw(img_src)
            draw.rectangle(mask_bbox, None, 'red')

            draw = PIL.ImageDraw.Draw(mask)
            draw.rectangle(mask_bbox, None, 'white')

        squared_msk_img = SquareMaskImage(img_src, mask, self.offset, self.rotate)

        image.paste(
            squared_msk_img.squared_src_img,
            squared_msk_img.offset,
            squared_msk_img.squared_msk_img
        )

    def set_edit_mode_str(self, edit_mode):
        self.edit_mode = edit_mode

    def on_mouse_down(self, event):
        self.sx, self.sy = event.x, event.y

    def on_mouse_move(self, event):

        if self.edit_mode.get() == self.EDIT_MODE_MOVE.value:
            dx, dy = (event.x - self.sx, event.y - self.sy)
            x, y = self.offset
            self.offset = (x + dx, y + dy)

        elif self.edit_mode.get() == self.EDIT_MODE_ROTATE.value:
            x0, y0 = self.calc_center_of_mask()
            rotate_old = self.calc_angle(x0, y0, self.sx, self.sy)
            rotate_new = self.calc_angle(x0, y0, event.x, event.y)
            self.rotate += rotate_new - rotate_old

        else:
            self.logger.error('Invalid edit mode: %s' % self.edit_mode.get())

        self.draw()
        self.sx, self.sy = event.x, event.y

    def calc_angle(self, x0, y0, x1, y1):
        """Calc angle from (x0, y0) to (x1, y1).

        x0, y0, x1, y1 is provided as PIL coordinates (top-left is the root),
        however return value is angle in the normal mathematical coordinates
        (bottom-left is the root).

        Returns:
            Angle in degrees
        """
        y0, y1 = -y0, -y1
        angle_in_radian = math.atan2((y1-y0), (x1-x0))
        return angle_in_radian / math.pi * 180.0

    def calc_center_of_mask(self):
        """Returns center of the mask image."""
        left, upper, right, lower = self.src_img_manager.image_mask.getbbox()
        return (left+right)/2.0, (upper+lower)/2.0

    def mode_changed(self, *args, **kwargs):
        """Callback function which is called when mode changes"""
        if self.image:
            self.draw()


class SquareMaskImage(object):
    def __init__(self, src_img, msk_img, offset, rotate):
        self.squared_src_img, self.squared_msk_img = self.create_images(src_img, msk_img)
        self.squared_src_img = self.squared_src_img.rotate(rotate)
        self.squared_msk_img = self.squared_msk_img.rotate(rotate)

        self.offset = self.calc_new_offset(msk_img, offset)

    def create_images(self, src_img, mask_img):
        left, upper, right, lower = mask_img.getbbox()
        square_size = int(math.sqrt((right-left)**2 + (upper-lower)**2))  # create square of this px on a side
        cropped_mask_image = mask_img.crop(mask_img.getbbox())
        cropped_src_image = src_img.crop(mask_img.getbbox())

        square_src_image = PIL.Image.new(src_img.mode, (square_size, square_size))
        square_mask_image = PIL.Image.new(mask_img.mode, (square_size, square_size))

        center_of_square = (old_div(square_size,2), old_div(square_size,2))
        top_left = (center_of_square[0] - old_div((right-left),2)), (center_of_square[1] - old_div((lower-upper),2))
        square_src_image.paste(cropped_src_image, top_left)
        square_mask_image.paste(cropped_mask_image, top_left)

        return square_src_image, square_mask_image

    def calc_new_offset(self, msk_img, original_offset):
        left, upper, right, lower = msk_img.getbbox()
        center_of_bbox = old_div((left+right),2), old_div((upper+lower),2)
        square_size = int(math.sqrt((right-left)**2 + (upper-lower)**2))
        offset_delta = center_of_bbox[0] - old_div(square_size,2), center_of_bbox[1] - old_div(square_size,2)

        return (original_offset[0] + offset_delta[0]), (original_offset[1] + offset_delta[1])
