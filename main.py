# -*- coding: UTF-8 -*-
import os
from tkinter import *
from tkinter import filedialog as fd
from tkinter.font import Font
from tkinter import messagebox as mb
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import gridspec
from scipy.cluster.hierarchy import dendrogram


# функция Евклидового расстояния
def euclidean_dist_2d(start, end):
    x1, y1 = start[0], start[1]
    x2, y2 = end[0], end[1]
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5


# Класс, описывающий кластер
class Cluster:
    def __init__(self, objects, distance=0.0, name=None):
        self.name = name
        self.distance = distance
        self.objects = objects

    # Метод нахождения расстояния между кластерами (мин/макс)
    def get_distance(self, cluster, is_min_distance=True):
        base_dist = euclidean_dist_2d(self.objects[0], cluster.objects[0])
        for obj in self.objects:
            for other_object in cluster.objects:
                distance = euclidean_dist_2d(obj, other_object)
                if is_min_distance:
                    if distance < base_dist:
                        base_dist = distance
                else:
                    if distance > base_dist:
                        base_dist = distance
        return base_dist


# Функция кластерного анализа
# (по умолчанию - ближайший сосед, is_complete - дальний)
def hcluster(data, is_complete=False):
    is_min_distance = not is_complete
    clusters = [Cluster([data[i]], 0, i) for i in range(len(data))]
    clusters_merge_matrix = []
    cluster_name = len(clusters)

    while len(clusters) > 1:
        closest_clusters = (0, 1)
        min_distance = clusters[0].get_distance(clusters[1], is_min_distance=is_min_distance)
        length = len(clusters)
        for i in range(length):
            for j in range(i + 1, length):
                dist = clusters[i].get_distance(clusters[j], is_min_distance=is_min_distance)
                if dist < min_distance:
                    min_distance = dist
                    closest_clusters = (i, j)

        first_cluster = clusters[closest_clusters[0]]
        second_cluster = clusters[closest_clusters[1]]
        new_cluster = Cluster(first_cluster.objects + second_cluster.objects,
                              min_distance, cluster_name)

        clusters_merge_matrix.append([first_cluster.name, second_cluster.name,
                                      new_cluster.distance, len(new_cluster.objects)])
        cluster_name += 1

        del clusters[closest_clusters[1]]
        del clusters[closest_clusters[0]]
        clusters.append(new_cluster)

    return clusters_merge_matrix


# Получение строки для вывода
def get_report_string(cluster_matrix, labels):
    report_string = ""
    cluster_dict = {}
    for index, label in enumerate(labels):
        cluster_dict[index] = label
    for row in cluster_matrix:
        cluster_dict[len(cluster_dict)] = f"{cluster_dict[row[0]]},{cluster_dict[row[1]]}"

        report_string += f"Кластер ({cluster_dict[row[0]]}) и" \
                         f" ({cluster_dict[row[1]]}) объединяются в" \
                         f" ({cluster_dict[len(cluster_dict) - 1]}).\n" \
                         f"Расстояние равно {row[2]:.2f}\n\n"
    return report_string


# Настройка дендрограммы, добавление маркеров
def custom_dendrogram(*args, **kwargs):
    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        for i, d in zip(ddata['icoord'], ddata['dcoord']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            plt.plot(x, y, 'ro')
            plt.annotate(f"{y:.3g}", (x, y), xytext=(0, -8),
                         textcoords='offset points',
                         va='top', ha='center')
    return ddata


# Функция отрисовки графиков
def draw_graphics(data, single_clusters, complete_clusters, labels):
    plt.switch_backend('TkAgg')
    gs = gridspec.GridSpec(2, 4)
    gs.update(wspace=0.5)
    plt.subplot(gs[0, 1:3])
    x = [row[0] for row in data]
    y = [row[1] for row in data]
    plt.scatter(x=x, y=y)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title("График разброса")
    for i, label in enumerate(labels):
        x_coord = x[i]
        y_coord = y[i]
        plt.annotate(label, (x_coord, y_coord), xytext=(5, 0), textcoords='offset points')

    plt.subplot(gs[1, :2])

    custom_dendrogram(single_clusters, labels=labels)

    plt.xlabel('X')
    plt.ylabel('P')
    plt.title('Дендрограмма метод ближайшего соседа')

    plt.subplot(gs[1, 2:])

    custom_dendrogram(complete_clusters, labels=labels)

    plt.title("Дендрограмма метод дальнего соседа")
    plt.xlabel('X')
    plt.ylabel('P')

    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.state('zoomed')
    fig_manager.set_window_title("Графики")
    plt.show()


# Класс, описывающий графический интерфейс
class Window(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataframe = None
        font = Font(family='Arial', size=12)
        text_font = Font(family='Arial', size=10)

        self.addition_label = Label(self, text="Условия датасета:\n\n"
                                               "1) Должен иметь 3 столбца;\n"
                                               "2) 1 столбец - названия объектов;\n"
                                               "3) 2 столбец - координата X;\n"
                                               "4) 3 столбец - координата Y;\n"
                                               "5) 1 строка - заголовки (любые).",
                                    font=font,
                                    justify="left")
        self.example_label = Label(self, text="Пример:\n\n"
                                              " L  |  X  |  Y\n"
                                              " 1  |  3  |  8\n"
                                              " 2  |  4  |  7\n"
                                              " 3  |  0  |  5\n"
                                              " 4  |  7  |  2\n",
                                   font=font, justify='center')
        self.single_cluster_label = Label(self, text="Метод ближайшего соседа", font=font)
        self.complete_cluster_label = Label(self, text="Метод дальнего соседа", font=font)

        self.single_cluster_frame = Frame(borderwidth=1)
        self.single_cluster_text = Text(self.single_cluster_frame, font=text_font, width=50, height=35, wrap=WORD)
        self.single_cluster_text_scroll = Scrollbar(self.single_cluster_frame, command=self.single_cluster_text.yview)

        self.complete_cluster_frame = Frame(borderwidth=1)
        self.complete_cluster_text = Text(self.complete_cluster_frame, font=text_font, width=50, height=35, wrap=WORD)
        self.complete_cluster_text_scroll = Scrollbar(self.complete_cluster_frame,
                                                      command=self.complete_cluster_text.yview)

        self.open_file_btn = Button(self, text="Загрузить датасет", command=self.openDataset, font=font)
        self.analysis_btn = Button(self, text="Провести анализ", command=self.doAnalysis, font=font)

        self.drawUI()

    def drawUI(self):
        self.title("Кластерный анализ")
        self.geometry("1200x700")
        self.resizable(0, 0)
        self.attributes("-topmost", True)
        self.addition_label.place(relx=.02, rely=.2)
        self.example_label.place(relx=.07, rely=.4)
        self.single_cluster_label.place(relx=.25, rely=.1)
        self.complete_cluster_label.place(relx=.65, rely=.1)

        self.single_cluster_text.config(yscrollcommand=self.single_cluster_text_scroll.set)
        self.single_cluster_text_scroll.pack(fill=Y, side=RIGHT)
        self.single_cluster_text.pack(side=LEFT, fill=BOTH, expand=True)
        self.single_cluster_frame.place(relx=.25, rely=.15)

        self.complete_cluster_text.config(yscrollcommand=self.complete_cluster_text_scroll.set)
        self.complete_cluster_text_scroll.pack(fill=Y, side=RIGHT)
        self.complete_cluster_text.pack(side=LEFT, fill=BOTH, expand=True)
        self.complete_cluster_frame.place(relx=.65, rely=.15)

        self.open_file_btn.place(relx=.05, rely=.1)
        self.analysis_btn.place(relx=.05, rely=.8)

    def openDataset(self):
        file_name = fd.askopenfilename(defaultextension='.csv',
                                       filetypes=[('CSV файлы', '*.csv'),
                                                  ('Excel файлы', '*.xlsx')])
        if not file_name:
            pass
        else:
            _, extension = os.path.splitext(file_name)
            if extension.lower() == '.csv':
                self.dataframe = pd.read_csv(file_name)
            elif extension.lower() == '.xlsx':
                self.dataframe = pd.read_excel(file_name)
            if self.dataframe is None or not len(self.dataframe.columns) == 3:
                self.dataframe = None
                mb.showerror("Ошибка", "Некорректный датасет")
            else:
                mb.showinfo("Уведомление", "Датасет загружен")

    def doAnalysis(self):
        if self.dataframe is None:
            mb.showerror("Ошибка", "Некорректный датасет")
        else:
            self.dataframe.columns = ["labels", "X", "Y"]
            labels = self.dataframe["labels"].tolist()
            data = self.dataframe[["X", "Y"]].values.tolist()
            cluster_single = hcluster(data)
            single_string = get_report_string(cluster_single, labels)

            self.single_cluster_text.configure(state=NORMAL)
            self.single_cluster_text.delete(1.0, END)
            self.single_cluster_text.insert(END, single_string)
            self.single_cluster_text.configure(state=DISABLED)

            cluster_complete = hcluster(data, is_complete=True)
            complete_string = get_report_string(cluster_complete, labels)
            self.complete_cluster_text.configure(state=NORMAL)
            self.complete_cluster_text.delete(1.0, END)
            self.complete_cluster_text.insert(END, complete_string)
            self.complete_cluster_text.configure(state=DISABLED)

            draw_graphics(data, cluster_single, cluster_complete, labels)


if __name__ == "__main__":
    window = Window()
    window.mainloop()
