#!/usr/bin/env python
import Tkinter
import PIL.Image
import PIL.ImageTk
from PIL import ImageChops
import poissonblending
import numpy as np


class PoissonBlendingApp(Tkinter.Tk):
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.entry = None
        self.label_text = None
        self.entry_text = None

        self.image_mask = None
        self.image_src = None
        self.image_dst = None
        self.image_masked_src = None
        self.image_result = None

        self.initialize()

    def create_widgets(self):
        self.grid()

        # Source and Destination images
        self.label_dst = Tkinter.Label(self)
        self.label_dst.grid(row=0, column=0)

        Tkinter \
            .Label(self, text="+") \
            .grid(row=0, column=1)

        self.label_src = Tkinter.Label(self)  # , image=self.image_tk_masked_src)
        self.label_src.grid(row=0, column=2)
        self.label_src.bind('<Button-1>', self.on_mouse_down)
        self.label_src.bind('<B1-Motion>', self.on_mouse_move)

        # Draw/Erase/Move buttons
        self.edit_options_frame = Tkinter.Frame(self)
        self.edit_options_frame.grid(row=1, column=2)
        self.edit_mode = Tkinter.StringVar()
        self.edit_mode.set('draw')
        edit_options = (
            ('Draw', 'draw'),
            ('Erase', 'erase'),
            ('Move', 'move'),
        )
        for text, mode in edit_options:
            b = Tkinter.Radiobutton(self.edit_options_frame, text=text,
                                    variable=self.edit_mode, value=mode,
                                    indicatoron=0)
            b.pack(side=Tkinter.LEFT)

        # Blend button
        Tkinter \
            .Button(self, text=u'Blend', command=self.blend) \
            .grid(row=2, column=0, columnspan=3)

    def initialize(self):

        self.create_widgets()

        self.load_images(src_path='./testimages/test1_src.png', dst_path='./testimages/test1_target.png')

    def load_images(self, src_path, dst_path):
        self.image_src = PIL.Image.open(src_path).convert("RGB")
        self.image_dst = PIL.Image.open(dst_path).convert("RGB")
        self.image_mask = PIL.Image.new('L', self.image_src.size)

        self.image_tk_dst = PIL.ImageTk.PhotoImage(self.image_dst)
        self.label_dst.configure(image=self.image_tk_dst)

        self.update_image_masked_src()

    def blend(self):
        src = np.asarray(self.image_src)
        src.flags.writeable = True
        dst = np.asarray(self.image_dst)
        dst.flags.writeable = True
        mask = np.asarray(self.image_mask)
        mask.flags.writeable = True

        blended_image = poissonblending.blend(dst, src, mask, offset=(40, -30))
        self.image_result = PIL.Image.fromarray(np.uint8(blended_image))
        self.image_tk_result = PIL.ImageTk.PhotoImage(self.image_result)

        result_window = Tkinter.Toplevel()
        label = Tkinter.Label(result_window, image = self.image_tk_result)
        label.pack()
        result_window.title("Blended Result")

    def on_mouse_down(self, event):
        if self.edit_mode.get() == 'move':
            print "Mouse button down:", event.x, event.y
            self.sx, self.sy = event.x, event.y
        elif self.edit_mode.get() == 'draw':
            pass
        elif self.edit_mode.get() == 'erase':
            pass

    def on_mouse_move(self, event):
        if self.edit_mode.get() == 'move':
            print "Mouse move:", event.x, event.y
            dx = event.x - self.sx
            dy = event.y - self.sy
            self.image_mask = ImageChops.offset(self.image_mask, dx, dy)
            self.update_image_masked_src()

            self.sx, self.sy = event.x, event.y
        elif self.edit_mode.get() == 'draw':
            self.modify_mask(event.x, event.y, 255)
        elif self.edit_mode.get() == 'erase':
            self.modify_mask(event.x, event.y, 0)

    def update_image_masked_src(self):
        self.image_masked_src = PIL.Image.blend(self.image_src, self.image_mask.convert("RGB"), 0.3)
        self.image_tk_masked_src = PIL.ImageTk.PhotoImage(self.image_masked_src)
        self.label_src.configure(image=self.image_tk_masked_src)

    def modify_mask(self, x, y, new_value):
        pixel = self.image_mask.load()
        mx, my = self.image_mask.size
        for dx in range(-10, 11):
            for dy in range(-10, 11):
                nx = x + dx
                ny = y + dy
                if 0 <= nx < mx and 0 <= ny < my:
                    pixel[x+dx, y+dy] = new_value
        self.update_image_masked_src()


if __name__ == "__main__":
    app = PoissonBlendingApp(None)
    app.title('Poisson Blending')
    app.mainloop()
