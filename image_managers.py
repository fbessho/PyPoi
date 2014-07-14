#!/usr/bin/env python
import PIL.Image
import PIL.ImageTk
import ImageChops
import tkFileDialog


class SourceImageManager():
    """Manage source image and mask image"""

    def __init__(self):
        pass

    def open(self):
        self.path = tkFileDialog.askopenfilename()
        self.load()

    def set_path(self, path):
        self.path = path

    def set_tk_label(self, tk_label):
        tk_label.bind('<Button-1>', self.on_mouse_down)
        tk_label.bind('<B1-Motion>', self.on_mouse_move)
        self.tk_label = tk_label

    def set_edit_mode_str(self, edit_mode_str):
        self.edit_mode = edit_mode_str

    def load(self):
        self.image_src = PIL.Image.open(self.path).convert("RGB")
        self.image_mask = PIL.Image.new('L', self.image_src.size)
        self.refresh()

    def refresh(self):
        self.image_masked_src = PIL.Image.blend(self.image_src,
                                                self.image_mask.convert("RGB"),
                                                0.3)
        self.image_tk_masked_src = PIL.ImageTk.PhotoImage(self.image_masked_src)
        self.tk_label.configure(image=self.image_tk_masked_src)

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
            self.image_mask = ImageChops.offset(self.image_mask, dx, dy)
            self.refresh()

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
        self.refresh()