import copy
import sys
from tkinter import Button, Frame, LEFT, Label, Menu, Tk, filedialog, messagebox, simpledialog

from PIL import Image, ImageTk

from binarization import change_to_simple_greyscale, perform_manual_binarization
from constant import HISTOGRAM_EQUALIZATION, HISTOGRAM_STRETCHING, MANUAL_BINARIZATION, MEDIAN_FILTER, SOBEL_FILTER
from histogram import calculate_distribution, calculate_equalization_lut, calculate_stretch_lut, check_max, check_min


def get_filename():
    return filedialog.askopenfilename()


def create_button(root, text, action=None):
    button = Button(root, text=text, command=action)
    button.pack(side=LEFT, padx=2, pady=2)


def ask_for_value(title, parent, min_value=0, max_value=255):
    return simpledialog.askinteger(title, 'Enter the value', parent=parent, minvalue=min_value, maxvalue=max_value)


class Runner:
    DEFAULT_PICTURE = 'pictures/lena.jpg'

    def __init__(self, master):
        menu = Menu(master)
        master.config(menu=menu)

        sub_menu_file = Menu(menu)
        menu.add_cascade(label='File', menu=sub_menu_file)
        sub_menu_file.add_command(label='Load', command=self.load_file)
        sub_menu_file.add_separator()
        sub_menu_file.add_command(label='Exit', command=sys.exit)

        menu.add_command(label='Reset', command=self.reset)

        main_frame = Frame(master)
        main_frame.pack()

        self.image_normalization_panel = Frame(main_frame)
        self.image_normalization_panel.grid(row=0, columnspan=3)
        self.create_image_normalization_panel()

        self.binarization_panel = Frame(main_frame)
        self.binarization_panel.grid(row=1, columnspan=3)
        self.create_binarization_panel()

        original_picture_panel = Frame(main_frame)
        original_picture_panel.grid(row=2, column=0)

        self.image = Image.open(self.DEFAULT_PICTURE).resize((300, 300))
        photo = ImageTk.PhotoImage(self.image)

        self.original_label = Label(original_picture_panel, image=photo)
        self.original_label.image = photo  # keep a reference!
        self.original_label.pack()

        modified_picture_panel = Frame(main_frame)
        modified_picture_panel.grid(row=2, column=2)

        self.image_copy = Image.open(self.DEFAULT_PICTURE).resize((300, 300))
        photo_copy = ImageTk.PhotoImage(self.image_copy)

        self.modified_label = Label(modified_picture_panel, image=photo_copy)
        self.modified_label.image = photo_copy  # keep a reference!
        self.modified_label.pack()

    def load_file(self):
        filename = get_filename()

        if filename.lower().endswith(('.png', 'jpg', 'jpeg')):
            self.image = Image.open(filename).resize((300, 300))
            photo = ImageTk.PhotoImage(self.image)

            self.original_label.config(image=photo)
            self.original_label.image = photo  # keep a reference!

            self.reset()
        else:
            messagebox.showerror('Error', 'Invalid format')

    def create_image_normalization_panel(self):
        create_button(self.image_normalization_panel, HISTOGRAM_STRETCHING, self.stretch_histogram)
        create_button(self.image_normalization_panel, HISTOGRAM_EQUALIZATION, self.equalize_histogram)

    def create_binarization_panel(self):
        create_button(self.binarization_panel, MANUAL_BINARIZATION, self.manual_binarization)
        create_button(self.binarization_panel, MEDIAN_FILTER)
        create_button(self.binarization_panel, SOBEL_FILTER)

    def reset(self):
        self.image_copy = copy.copy(self.image)
        photo_copy = ImageTk.PhotoImage(self.image)
        self.modified_label.config(image=photo_copy)
        self.modified_label.image = photo_copy  # keep a reference!

    def stretch_histogram(self):
        r_min, g_min, b_min = 255, 255, 255
        r_max, g_max, b_max = 1, 1, 1

        pixels = self.image_copy.load()
        for i in range(self.image_copy.size[0]):
            for j in range(self.image_copy.size[1]):
                (r, g, b) = pixels[i, j]
                r = int(r)
                g = int(g)
                b = int(b)
                r_min, g_min, b_min = check_min(r, g, b, r_min, g_min, b_min)
                r_max, g_max, b_max = check_max(r, g, b, r_max, g_max, b_max)

        red_lut = calculate_stretch_lut(r_min, r_max)
        green_lut = calculate_stretch_lut(g_min, g_max)
        blue_lut = calculate_stretch_lut(b_min, b_max)
        self.apply_lut_tables(red_lut, green_lut, blue_lut)

    def apply_lut_tables(self, red_lut, green_lut, blue_lut):
        pixels = self.image_copy.load()
        for i in range(self.image_copy.size[0]):
            for j in range(self.image_copy.size[1]):
                (r, g, b) = pixels[i, j]
                pixels[i, j] = (red_lut[r], green_lut[g], blue_lut[b])

        photo_copy = ImageTk.PhotoImage(self.image_copy)
        self.modified_label.config(image=photo_copy)
        self.modified_label.image = photo_copy  # keep a reference!

    def equalize_histogram(self):
        pixels = self.image_copy.load()
        width = self.image_copy.size[0]
        height = self.image_copy.size[1]
        r_dist, g_dist, b_dist = calculate_distribution(pixels, width, height)

        number_of_pixels = width * height
        sum_r, sum_g, sum_b = 0, 0, 0
        d_r, d_g, d_b = [0] * 256, [0] * 256, [0] * 256
        for i in range(256):
            sum_r += r_dist[i] / number_of_pixels
            sum_g += g_dist[i] / number_of_pixels
            sum_b += b_dist[i] / number_of_pixels

            d_r[i] += sum_r
            d_g[i] += sum_g
            d_b[i] += sum_b

        red_lut = calculate_equalization_lut(d_r)
        green_lut = calculate_equalization_lut(d_g)
        blue_lut = calculate_equalization_lut(d_b)
        self.apply_lut_tables(red_lut, green_lut, blue_lut)

    def manual_binarization(self):
        self.image_copy = change_to_simple_greyscale(self.image_copy)

        threshold = ask_for_value("Enter threshold", self.original_label)

        self.image_copy = perform_manual_binarization(self.image_copy, threshold)
        photo_copy = ImageTk.PhotoImage(self.image_copy)
        self.modified_label.config(image=photo_copy)
        self.modified_label.image = photo_copy  # keep a reference!


if __name__ == '__main__':
    root = Tk()
    app = Runner(root)
    root.mainloop()
