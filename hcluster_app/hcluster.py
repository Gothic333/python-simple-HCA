from .utils import euclidean_dist_2d


class Cluster:
    def __init__(self, objects, distance=0.0, name=None):
        self.name = name
        self.distance = distance
        self.objects = objects

    def get_distance(self, cluster, dist_func=euclidean_dist_2d, dist_compare=min):
        base_dist = dist_func(self.objects[0], cluster.objects[0])
        for obj in self.objects:
            for other_object in cluster.objects:
                distance = dist_func(obj, other_object)
                base_dist = dist_compare(base_dist, distance)
        return base_dist


def hcluster(data, method='single'):
    type_map = {
        'single': min,
        'complete': max
    }
    clusters = [Cluster([data[i]], 0, i) for i in range(len(data))]
    clusters_merge_matrix = []
    cluster_name = len(clusters)

    while len(clusters) > 1:
        min_distance = float('inf')
        for i in range(len(clusters) - 1):
            for j in range(i + 1, len(clusters)):
                dist = clusters[i].get_distance(clusters[j], dist_compare=type_map[method])
                if dist < min_distance:
                    min_distance = dist
                    closest_1, closest_2 = i, j

        first_cluster = clusters[closest_1]
        second_cluster = clusters[closest_2]
        new_cluster = Cluster(first_cluster.objects + second_cluster.objects,
                              min_distance, cluster_name)

        clusters_merge_matrix.append([first_cluster.name, second_cluster.name,
                                      new_cluster.distance, len(new_cluster.objects)])
        cluster_name += 1

        del clusters[closest_2]
        del clusters[closest_1]
        clusters.append(new_cluster)

    return clusters_merge_matrix