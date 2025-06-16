import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.font import Font

import pandas as pd

from .hcluster import hcluster
from .utils import draw_graphics, get_cluster_report


class HCA(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.df = None
        app_font = Font(family='Arial', size=12)
        inner_text_font = Font(family='Arial', size=10)

        self.addition_label = tk.Label(self, 
                                       text='Входные данные:\n\n'
                                            '- Должны иметь 3 столбца;\n'
                                            '- 1 столбец - названия объектов;\n'
                                            '- 2 столбец - координата X;\n'
                                            '- 3 столбец - координата Y;\n'
                                            '- 1 строка - заголовки (любые).',
                                       font=app_font,
                                       justify='left'
                                       )
        self.example_label = tk.Label(self,
                                      text='Пример:\n\n'
                                           ' L  |  X  |  Y\n'
                                           ' 1  |  3  |  8\n'
                                           ' 2  |  4  |  7\n'
                                           ' 3  |  0  |  5\n'
                                           ' 4  |  7  |  2\n',
                                      font=app_font, 
                                      justify='center'
                                      )
        self.single_cluster_label = tk.Label(self, 
                                             text='Метод ближайшего соседа', 
                                             font=app_font
                                             )
        self.complete_cluster_label = tk.Label(self, 
                                               text='Метод дальнего соседа', 
                                               font=app_font
                                               )

        self.single_cluster_frame = tk.Frame(borderwidth=1)
        self.single_cluster_text = tk.Text(self.single_cluster_frame,
                                           font=inner_text_font,
                                           width=50,
                                           height=35,
                                           wrap=tk.WORD
                                           )
        self.single_cluster_text_scroll = tk.Scrollbar(self.single_cluster_frame, 
                                                       command=self.single_cluster_text.yview)

        self.complete_cluster_frame = tk.Frame(borderwidth=1)
        self.complete_cluster_text = tk.Text(self.complete_cluster_frame,
                                             font=inner_text_font,
                                             width=50,
                                             height=35,
                                             wrap=tk.WORD
                                             )
        self.complete_cluster_text_scroll = tk.Scrollbar(self.complete_cluster_frame,
                                                         command=self.complete_cluster_text.yview)

        self.open_file_btn = tk.Button(self, text='Загрузить датасет',
                                       command=self.load_dataset, 
                                       font=app_font
                                       )
        self.analysis_btn = tk.Button(self, text='Провести анализ',
                                      command=self.make_analysis, 
                                      font=app_font
                                      )

        self.draw_ui()

    def draw_ui(self):
        self.title('Иерархический кластерный анализ')
        self.geometry('1200x700')
        self.minsize(1200, 700)
        self.maxsize(1920, 1080)
        self.addition_label.place(relx=.02, rely=.2, anchor=tk.NW)
        self.example_label.place(relx=.02, rely=.4, anchor=tk.NW)
        self.single_cluster_label.place(relx=.25, rely=.02, anchor=tk.NW)
        self.complete_cluster_label.place(relx=.65, rely=.02, anchor=tk.NW)

        self.single_cluster_text.config(yscrollcommand=self.single_cluster_text_scroll.set)
        self.single_cluster_text_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.single_cluster_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.single_cluster_frame.place(relx=.25, rely=.06, relwidth=.32, relheight=.9, anchor=tk.NW)

        self.complete_cluster_text.config(yscrollcommand=self.complete_cluster_text_scroll.set)
        self.complete_cluster_text_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.complete_cluster_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.complete_cluster_frame.place(relx=.65, rely=.06, relwidth=.32, relheight=.9, anchor=tk.NW)

        self.open_file_btn.place(relx=.02, rely=.06)
        self.analysis_btn.place(relx=.02, rely=.6)

    def load_dataset(self):
        file_name = fd.askopenfilename(defaultextension='.csv',
                                       filetypes=[('CSV файлы', '*.csv'),
                                                  ('Excel файлы', '*.xlsx')])
        if file_name:
            extension = Path(file_name).suffix.lower()
            if extension == '.csv':
                self.df = pd.read_csv(file_name)
            elif extension == '.xlsx':
                self.df = pd.read_excel(file_name)
            if self.df is None or not len(self.df.columns) == 3:
                self.df = None
                mb.showerror('Ошибка', 'Некорректный датасет')
            else:
                mb.showinfo('Уведомление', 'Датасет загружен')

    def make_analysis(self):
        if self.df is None:
            mb.showerror('Ошибка', 'Некорректный датасет')
        else:
            self.df.columns = ['labels', 'X', 'Y']
            labels = self.df['labels'].tolist()
            data = self.df[['X', 'Y']].values.tolist()
            cluster_single_matrix = hcluster(data, method='single')
            single_string = get_cluster_report(cluster_single_matrix, labels)

            self.single_cluster_text.configure(state=tk.NORMAL)
            self.single_cluster_text.delete(1.0, tk.END)
            self.single_cluster_text.insert(tk.END, single_string)
            self.single_cluster_text.configure(state=tk.DISABLED)

            cluster_complete_matrix = hcluster(data, method='complete')
            complete_string = get_cluster_report(cluster_complete_matrix, labels)

            self.complete_cluster_text.configure(state=tk.NORMAL)
            self.complete_cluster_text.delete(1.0, tk.END)
            self.complete_cluster_text.insert(tk.END, complete_string)
            self.complete_cluster_text.configure(state=tk.DISABLED)

            draw_graphics(data, cluster_single_matrix, cluster_complete_matrix, labels)
