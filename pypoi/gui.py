import logging

import Tkinter
import tkFileDialog
import tkMessageBox

import PIL.Image
import PIL.ImageTk
import numpy as np

from pypoi import poissonblending
from pypoi.image_managers import SourceImageManager, DestinationImageManager
from pypoi.util import resource_path as rp


SAVE_MASK_ENABLED = False  # Show 'Save mask image' button

logger = logging.getLogger('GUI')


class PoissonBlendingApp(Tkinter.Tk):
    NUM_OF_EXAMPLES = 4  # Examples in the testimages folder.

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
        label_dst = Tkinter.Label(self)
        label_dst.grid(row=0, column=0)
        self.dst_img_manager.set_tk_label(label_dst)

        Tkinter.Label(self, text="+").grid(row=0, column=1)

        label_src = Tkinter.Label(self)
        label_src.grid(row=0, column=2)
        self.src_img_manager.set_tk_label(label_src)

        # Destination image buttons (Move, Rotate)
        dst_img_buttons = Tkinter.Frame(self)
        dst_img_buttons.grid(row=1, column=0)
        dst_edit_mode = Tkinter.StringVar()
        dst_edit_mode.trace('w', self.dst_img_manager.mode_changed)
        dst_edit_mode.set('move')
        for text, mode in self.dst_img_manager.EDIT_MODES:
            b = Tkinter.Radiobutton(
                dst_img_buttons, text=text, variable=dst_edit_mode, value=mode,
                indicatoron=0)
            b.pack(side=Tkinter.LEFT)
        self.dst_img_manager.set_edit_mode_str(dst_edit_mode)

        # Source image buttons (Draw/Erase/Move)
        src_img_buttons = Tkinter.Frame(self)
        src_img_buttons.grid(row=1, column=2)
        src_edit_mode = Tkinter.StringVar()
        src_edit_mode.set('draw')

        for text, mode in self.src_img_manager.EDIT_MODES:
            b = Tkinter.Radiobutton(src_img_buttons, text=text,
                                    variable=src_edit_mode, value=mode,
                                    indicatoron=0)
            b.pack(side=Tkinter.LEFT)
        self.src_img_manager.set_edit_mode_str(src_edit_mode)

        b = Tkinter.Button(src_img_buttons, text='Clear',
                           command=self.src_img_manager.clear_mask)
        b.pack(side=Tkinter.LEFT)

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

        # Size buttons for source image
        _draw_size_buttons(2, 2, self.src_img_manager.ZOOM_FUNCTIONS)

        # Blend button
        action_frame = Tkinter.Frame(self)
        action_frame.grid(row=3, column=0, columnspan=3)

        if SAVE_MASK_ENABLED:
            def save_mask():
                self.src_img_manager.save_mask_image()
                print self.dst_img_manager.offset

            Tkinter.Button(action_frame, text='Save mask image',
                           command=save_mask).pack()

        Tkinter.Button(action_frame, text=u'Blend', command=self.blend).pack()

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
                mask_path = rp('./testimages/test%d_mask.png' % example_id)
            except IndexError:
                pass

            self.src_img_manager.open(src_path, mask_path=mask_path)
            self.dst_img_manager.open(dst_path)

        return _load_example

    def blend(self):
        angle = self.dst_img_manager.rotate
        src = np.asarray(self.src_img_manager.image_src.rotate(angle))
        src.flags.writeable = True
        dst = np.asarray(self.dst_img_manager.image)
        dst.flags.writeable = True
        mask = np.asarray(self.src_img_manager.image_mask.rotate(angle))
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
                msg = 'Unknown extension. Supported extensions:\n'
                msg += ' '.join(PIL.Image.EXTENSION.keys())
                tkMessageBox.showerror("Error", msg)

        return _save_result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = PoissonBlendingApp(None)
    app.title('PyPoi: "Py"thon Program for "Poi"sson Image Editing')
    app.mainloop()
