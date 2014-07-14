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

    def select_entry_text(self):
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def initialize(self):
        self.grid()

        # Load images
        self.image_dst = PIL.Image.open('./testimages/test1_target.png').convert("RGB")
        self.image_mask = PIL.Image.open('./testimages/test1_mask.png')
        self.image_src = PIL.Image.open('./testimages/test1_src.png').convert("RGB")
        self.image_masked_src = PIL.Image.blend(self.image_src, self.image_mask.convert("RGB"), 0.3)
        # print "Blending.."
        # self.blend()

        # Display images
        self.image_tk_masked_src = PIL.ImageTk.PhotoImage(self.image_masked_src)
        self.image_tk_dst = PIL.ImageTk.PhotoImage(self.image_dst)
        # self.image_tk_result = PIL.ImageTk.PhotoImage(self.image_result)

        Tkinter \
            .Label(self, image=self.image_tk_dst) \
            .grid(row=0, column=0)

        Tkinter \
            .Label(self, text="+") \
            .grid(row=0, column=1)

        self.label_src = Tkinter.Label(self, image=self.image_tk_masked_src)
        self.label_src.grid(row=0, column=2)
        self.label_src.bind('<Button-1>', self.on_mouse_down)
        self.label_src.bind('<B1-Motion>', self.on_mouse_move)

        Tkinter \
            .Button(self, text=u'Blend', command=self.blend) \
            .grid(row=1, column=0, columnspan=3)

        self.grid_columnconfigure(0, weight=1)
        # self.resizable(True, False)
        self.update()
        self.geometry(self.geometry())

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
        print "Mouse button down:", event.x, event.y
        self.sx, self.sy = event.x, event.y

    def on_mouse_move(self, event):
        print "Mouse move:", event.x, event.y
        dx = event.x - self.sx
        dy = event.y - self.sy
        self.image_mask = ImageChops.offset(self.image_mask, dx, dy)
        self.image_masked_src = PIL.Image.blend(self.image_src, self.image_mask.convert("RGB"), 0.3)
        self.image_tk_masked_src = PIL.ImageTk.PhotoImage(self.image_masked_src)
        self.label_src.configure(image = self.image_tk_masked_src)

        self.sx, self.sy = event.x, event.y


if __name__ == "__main__":
    app = PoissonBlendingApp(None)
    app.title('Poisson Blending')
    app.mainloop()
