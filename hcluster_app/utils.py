import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.cluster.hierarchy import dendrogram


def euclidean_dist_2d(start, end):
    (x1, y1), (x2, y2) = start, end
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5


def get_cluster_report(cluster_matrix, labels):
    report_string = ''
    cluster_dict = {idx: label for idx, label in enumerate(labels)}

    for row in cluster_matrix:
        cluster_dict[len(cluster_dict)] = f'{cluster_dict[row[0]]},{cluster_dict[row[1]]}'

        report_string += f'Кластер ({cluster_dict[row[0]]}) и' \
                         f' ({cluster_dict[row[1]]}) объединяются в' \
                         f' ({cluster_dict[len(cluster_dict) - 1]}).\n' \
                         f'Расстояние равно {row[2]:.2f}\n\n'
    return report_string


def dendrogram_with_dots(*args, **kwargs):
    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        for i, d in zip(ddata['icoord'], ddata['dcoord']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            plt.plot(x, y, 'ro')
            plt.annotate(f'{y:.3g}', (x, y), xytext=(0, -8),
                         textcoords='offset points',
                         va='top', ha='center')
    return ddata


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
    plt.title('График разброса')
    for i, label in enumerate(labels):
        x_coord = x[i]
        y_coord = y[i]
        plt.annotate(label, (x_coord, y_coord), xytext=(5, 0), textcoords='offset points')

    plt.subplot(gs[1, :2])

    dendrogram_with_dots(single_clusters, labels=labels)

    plt.xlabel('X')
    plt.ylabel('P')
    plt.title('Дендрограмма метод ближайшего соседа')

    plt.subplot(gs[1, 2:])

    dendrogram_with_dots(complete_clusters, labels=labels)

    plt.title('Дендрограмма метод дальнего соседа')
    plt.xlabel('X')
    plt.ylabel('P')

    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.state('zoomed')
    fig_manager.set_window_title('Графики')
    plt.show()
