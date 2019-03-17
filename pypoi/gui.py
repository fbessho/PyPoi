from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import range
import logging

import tkinter
import tkinter.filedialog
import tkinter.messagebox

import PIL.Image
import PIL.ImageTk
import numpy as np

from pypoi import poissonblending
from pypoi.image_managers import SourceImageManager, DestinationImageManager
from pypoi.util import resource_path as rp


SAVE_MASK_ENABLED = False  # Show 'Save mask image' button

logger = logging.getLogger('GUI')


class PoissonBlendingApp(tkinter.Tk):
    NUM_OF_EXAMPLES = 4  # Examples in the testimages folder.

    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
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

        self.src_img_manager.set_path(rp('./testimages/test1_src.png'))
        self.src_img_manager.load(rp('./testimages/test1_mask.png'))

        self.dst_img_manager.set_path(rp('./testimages/test1_target.png'))
        self.dst_img_manager.load()
        from pypoi.testimages.config import offset
        self.dst_img_manager.offset = offset[0]

        self.src_img_manager.draw()

    def create_widgets(self):
        self.grid()

        # Source and Destination images
        label_dst = tkinter.Label(self)
        label_dst.grid(row=0, column=0)
        self.dst_img_manager.set_tk_label(label_dst)

        tkinter.Label(self, text="+").grid(row=0, column=1)

        label_src = tkinter.Label(self)
        label_src.grid(row=0, column=2)
        self.src_img_manager.set_tk_label(label_src)

        # Destination image buttons (Move, Rotate)
        dst_img_buttons = tkinter.Frame(self)
        dst_img_buttons.grid(row=1, column=0)
        dst_edit_mode = tkinter.StringVar()
        dst_edit_mode.trace('w', self.dst_img_manager.mode_changed)
        dst_edit_mode.set('move')
        for text, mode in self.dst_img_manager.EDIT_MODES:
            b = tkinter.Radiobutton(
                dst_img_buttons, text=text, variable=dst_edit_mode, value=mode,
                indicatoron=0)
            b.pack(side=tkinter.LEFT)
        self.dst_img_manager.set_edit_mode_str(dst_edit_mode)

        # Source image buttons (Draw/Erase/Move)
        src_img_buttons = tkinter.Frame(self)
        src_img_buttons.grid(row=1, column=2)
        src_edit_mode = tkinter.StringVar()
        src_edit_mode.set('draw')

        for text, mode in self.src_img_manager.EDIT_MODES:
            b = tkinter.Radiobutton(src_img_buttons, text=text,
                                    variable=src_edit_mode, value=mode,
                                    indicatoron=0)
            b.pack(side=tkinter.LEFT)
        self.src_img_manager.set_edit_mode_str(src_edit_mode)

        b = tkinter.Button(src_img_buttons, text='Clear',
                           command=self.src_img_manager.clear_mask)
        b.pack(side=tkinter.LEFT)

        # Size buttons
        def _draw_size_buttons(row, column, functions):
            size_buttons = tkinter.Frame(self)
            size_buttons.grid(row=row, column=column)
            plus_button = tkinter.Button(size_buttons, text='+', width=2,
                                         command=functions['+'])
            original_buttton = tkinter.Button(size_buttons, text='100%',
                                              width=5,
                                              command=functions['original'])
            minus_button = tkinter.Button(size_buttons, text='-', width=2,
                                          command=functions['-'])
            minus_button.pack(side=tkinter.LEFT)
            original_buttton.pack(side=tkinter.LEFT)
            plus_button.pack(side=tkinter.LEFT)

        # Size buttons for source image
        _draw_size_buttons(2, 2, self.src_img_manager.ZOOM_FUNCTIONS)

        # Blend button
        action_frame = tkinter.Frame(self)
        action_frame.grid(row=3, column=0, columnspan=3)

        if SAVE_MASK_ENABLED:
            def save_mask():
                self.src_img_manager.save_mask_image()
                print(self.dst_img_manager.offset)

            tkinter.Button(action_frame, text='Save mask image',
                           command=save_mask).pack()

        tkinter.Button(action_frame, text=u'Blend', command=self.blend).pack()

    def create_menu(self):
        menu_bar = tkinter.Menu(self)

        file_menu = tkinter.Menu(menu_bar)
        file_menu.add_command(label='Open Source Image',
                              command=self.src_img_manager.open_from_dialog)
        file_menu.add_command(label='Open Destination Image',
                              command=self.dst_img_manager.open_from_dialog)
        menu_bar.add_cascade(label="File", menu=file_menu)

        run_menu = tkinter.Menu(menu_bar)
        run_menu.add_command(label='Blend!', command=self.blend)
        menu_bar.add_cascade(label="Run", menu=run_menu)

        example_menu = tkinter.Menu(menu_bar)
        for i in range(self.NUM_OF_EXAMPLES):
            i += 1
            example_menu.add_command(label="Example %d" % i,
                                     command=self.load_example(i))
        menu_bar.add_cascade(label="Examples", menu=example_menu)

        self.config(menu=menu_bar)

    def load_example(self, example_id):
        """
         Load an example to GUI.
        :param example_id: id starts with *one*
        """

        def _load_example():
            src_path = rp('./testimages/test%d_src.png' % example_id)
            dst_path = rp('./testimages/test%d_target.png' % example_id)
            mask_path = None

            try:
                from pypoi.testimages.config import offset

                self.dst_img_manager.offset = offset[example_id - 1]
                self.dst_img_manager.rotate = 0
                mask_path = rp('./testimages/test%d_mask.png' % example_id)
            except IndexError:
                pass

            self.src_img_manager.open(src_path, mask_path=mask_path)
            self.dst_img_manager.open(dst_path)

        return _load_example

    def blend(self):
        angle = self.dst_img_manager.rotate
        src = np.array(self.src_img_manager.image_src.rotate(angle))
        dst = np.array(self.dst_img_manager.image)
        mask = np.array(self.src_img_manager.image_mask.rotate(angle))

        # poissonblending.blend takes (y, x) as offset,
        # whereas gui has (x, y) as offset values so reverse these values.
        reversed_offset = self.dst_img_manager.offset[::-1]
        blended_image = poissonblending.blend(dst, src, mask, reversed_offset)
        self.image_result = PIL.Image.fromarray(np.uint8(blended_image))
        self.image_tk_result = PIL.ImageTk.PhotoImage(self.image_result)

        result_window = tkinter.Toplevel()
        label = tkinter.Label(result_window, image=self.image_tk_result)
        label.image = self.image_tk_result  # for holding reference counter
        label.pack()
        save_button = tkinter.Button(result_window, text='Save',
                                     command=self.save_result(result_window))
        save_button.pack()

        result_window.title("Blended Result")

    def save_result(self, parent):
        def _save_result():
            file_name = tkinter.filedialog.asksaveasfilename(parent=parent)
            try:
                self.image_result.save(file_name)
            except KeyError:
                msg = 'Unknown extension. Supported extensions:\n'
                msg += ' '.join(list(PIL.Image.EXTENSION.keys()))
                tkinter.messagebox.showerror("Error", msg)

        return _save_result


def main():
    global app
    logging.basicConfig(level=logging.INFO)
    app = PoissonBlendingApp(None)
    app.title('PyPoi: "Py"thon Program for "Poi"sson Image Editing')
    app.mainloop()


if __name__ == "__main__":
    main()
