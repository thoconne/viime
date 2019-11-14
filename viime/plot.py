from numpy import sqrt
from pandas import pd
from sklearn.decomposition import PCA


def pca(measurements: pd.DataFrame, max_components: int):
    pca = PCA(n_components=max_components)
    x = pca.fit_transform(measurements)
    rotation = pca.components_.T
    sdev = sqrt(pca.explained_variance_)
    return {
        'x': x.tolist(),
        'rotation': rotation.tolist(),
        'sdev': sdev.tolist()
    }
