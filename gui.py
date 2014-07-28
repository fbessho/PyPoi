#!/usr/bin/env python
import Tkinter
import tkFileDialog
import tkMessageBox

import PIL.Image
import PIL.ImageTk
import numpy as np

import poissonblending
from image_managers import SourceImageManager, DestinationImageManager


class PoissonBlendingApp(Tkinter.Tk):
    NUM_OF_EXAMPLES = 2  # Examples in the testimages folder.

    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.src_img_manager = SourceImageManager()
        self.dst_img_manager = DestinationImageManager(self.src_img_manager)

        self.parent = parent
        self.entry = None
        self.label_text = None
        self.entry_text = None

        self.image_result = None

        self.initialize()

    def initialize(self):
        self.create_menu()
        self.create_widgets()

        self.src_img_manager.set_path('./testimages/test1_src.png')
        self.src_img_manager.load()

        self.dst_img_manager.set_path('./testimages/test1_target.png')
        self.dst_img_manager.load()

        self.src_img_manager.draw()

    def create_widgets(self):
        self.grid()

        # Source and Destination images
        label_dst = Tkinter.Label(self)
        label_dst.grid(row=0, column=0)
        self.dst_img_manager.set_tk_label(label_dst)

        Tkinter.Label(self, text="+").grid(row=0, column=1)

        label_src = Tkinter.Label(self)
        label_src.grid(row=0, column=2)
        self.src_img_manager.set_tk_label(label_src)

        # Draw/Erase/Move buttons
        edit_options_frame = Tkinter.Frame(self)
        edit_options_frame.grid(row=1, column=2)
        edit_mode = Tkinter.StringVar()
        edit_mode.set('draw')
        edit_options = (
            ('Draw', 'draw'),
            ('Erase', 'erase'),
            ('Move', 'move'),
        )
        for text, mode in edit_options:
            b = Tkinter.Radiobutton(edit_options_frame, text=text,
                                    variable=edit_mode, value=mode,
                                    indicatoron=0)
            b.pack(side=Tkinter.LEFT)
        self.src_img_manager.set_edit_mode_str(edit_mode)

        # Size buttons
        def _draw_size_buttons(row, column, functions):
            size_buttons = Tkinter.Frame(self)
            size_buttons.grid(row=row, column=column)
            plus_button = Tkinter.Button(size_buttons, text='+', width=2,
                                         command=functions['+'])
            original_buttton = Tkinter.Button(size_buttons, text='100%',
                                              width=5,
                                              command=functions['original'])
            minus_button = Tkinter.Button(size_buttons, text='-', width=2,
                                          command=functions['-'])
            minus_button.pack(side=Tkinter.LEFT)
            original_buttton.pack(side=Tkinter.LEFT)
            plus_button.pack(side=Tkinter.LEFT)

        # Size buttons for destination image
        # _draw_size_buttons(2, 0, self.dst_img_manager.ZOOM_FUNCTIONS)

        # Size buttons for source image
        _draw_size_buttons(2, 2, self.src_img_manager.ZOOM_FUNCTIONS)

        # Blend button
        Tkinter \
            .Button(self, text=u'Blend', command=self.blend) \
            .grid(row=3, column=0, columnspan=3)

    def create_menu(self):
        menu_bar = Tkinter.Menu(self)

        file_menu = Tkinter.Menu(menu_bar)
        file_menu.add_command(label='Open Source Image',
                              command=self.src_img_manager.open_from_dialog)
        file_menu.add_command(label='Open Destination Image',
                              command=self.dst_img_manager.open_from_dialog)
        menu_bar.add_cascade(label="File", menu=file_menu)

        run_menu = Tkinter.Menu(menu_bar)
        run_menu.add_command(label='Blend!', command=self.blend)
        menu_bar.add_cascade(label="Run", menu=run_menu)

        example_menu = Tkinter.Menu(menu_bar)
        for i in range(self.NUM_OF_EXAMPLES):
            i += 1
            example_menu.add_command(label="Example %d" % i,
                                     command=self.load_example(i))
        menu_bar.add_cascade(label="Examples", menu=example_menu)

        self.config(menu=menu_bar)

    def load_example(self, example_number):
        def _load_example():
            src_path = './testimages/test%d_src.png' % example_number
            dst_path = './testimages/test%d_target.png' % example_number
            self.src_img_manager.open(src_path)
            self.dst_img_manager.open(dst_path)

        return _load_example

    def blend(self):
        src = np.asarray(self.src_img_manager.image_src)
        src.flags.writeable = True
        dst = np.asarray(self.dst_img_manager.image)
        dst.flags.writeable = True
        mask = np.asarray(self.src_img_manager.image_mask)
        mask.flags.writeable = True

        # poissonblending.blend takes (y, x) as offset,
        # whereas gui has (x, y) as offset values so reverse these values.
        reversed_offset = self.dst_img_manager.offset[::-1]
        blended_image = poissonblending.blend(dst, src, mask, reversed_offset)
        self.image_result = PIL.Image.fromarray(np.uint8(blended_image))
        self.image_tk_result = PIL.ImageTk.PhotoImage(self.image_result)

        result_window = Tkinter.Toplevel()
        label = Tkinter.Label(result_window, image=self.image_tk_result)
        label.image = self.image_tk_result  # for holding reference counter
        label.pack()
        save_button = Tkinter.Button(result_window, text='Save',
                                     command=self.save_result(result_window))
        save_button.pack()

        result_window.title("Blended Result")

    def save_result(self, parent):
        def _save_result():
            file_name = tkFileDialog.asksaveasfilename(parent=parent)
            try:
                self.image_result.save(file_name)
            except KeyError:
                msg  = 'Unknown extension. Supported extensions:\n'
                msg += ' '.join(PIL.Image.EXTENSION.keys())
                tkMessageBox.showerror("Error", msg)

        return _save_result


if __name__ == "__main__":
    app = PoissonBlendingApp(None)
    app.title('Poisson Blending')
    app.mainloop()
