#!/usr/bin/env python
import tkMessageBox
import PIL.Image
import PIL.ImageTk
import PIL.ImageChops
import tkFileDialog


class ImageManager():
    def __init__(self):
        pass

    def open_from_dialog(self):
        path = tkFileDialog.askopenfilename()
        if len(path) > 0:
            self.open(path)

    def open(self, path, **kwargs):
        self.path = path
        self.load(**kwargs)
        self.draw()

    def set_path(self, path):
        self.path = path

    def set_tk_label(self, tk_label):
        tk_label.bind('<Button-1>', self.on_mouse_down)
        tk_label.bind('<B1-Motion>', self.on_mouse_move)
        self.tk_label = tk_label


class SourceImageManager(ImageManager):
    """Manage source image and mask image
    self.path       - path to source image file
    self.image_src  - PIL.Image object of source image
    self.image_mask - PIL.Image object of mask image
    """

    def __init__(self):
        ImageManager.__init__(self)
        self.draw_propagate_functions = []
        self.ZOOM_FUNCTIONS = {
            '+': self.zoom_by_ten_percent,
            '-': self.shrink_by_ten_percent,
            'original': self.reset_size
        }

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
            print "Mouse button down:", event.x, event.y
            self.sx, self.sy = event.x, event.y
        elif self.edit_mode.get() == 'draw':
            self.modify_mask(event.x, event.y, 255)
        elif self.edit_mode.get() == 'erase':
            self.modify_mask(event.x, event.y, 0)

    def on_mouse_move(self, event):
        if self.edit_mode.get() == 'move':
            print "Mouse move:", event.x, event.y
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
        yn = tkMessageBox.askokcancel('Clear mask image',
                                      'Mask will be cleared, do you proceed?')
        if yn:
            self.image_mask = PIL.Image.new('L', self.image_src.size)
            self.draw()

    def save_mask_image(self):
        self.image_mask.save('mask.png')


class DestinationImageManager(ImageManager):
    def __init__(self, src_img_manager):
        ImageManager.__init__(self)
        self.src_img_manager = src_img_manager
        self.src_img_manager.add_propagation_func(self.draw)
        self.offset = (0, 0)

    def load(self):
        self.image = PIL.Image.open(self.path).convert("RGB")

    def draw(self):
        image_to_show = self.image.copy()
        img_src = self.src_img_manager.image_src
        mask = self.src_img_manager.image_mask

        image_to_show.paste(img_src, self.offset, mask)

        self.image_tk = PIL.ImageTk.PhotoImage(image_to_show)
        self.tk_label.configure(image=self.image_tk)

    def on_mouse_down(self, event):
        self.sx, self.sy = event.x, event.y

    def on_mouse_move(self, event):
        dx, dy = (event.x - self.sx, event.y - self.sy)
        x, y = self.offset
        self.offset = (x + dx, y + dy)
        self.draw()

        self.sx, self.sy = event.x, event.y
