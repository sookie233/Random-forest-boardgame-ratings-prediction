from __future__ import division
import random
import numpy as np
from scipy.stats import mode
from tools import information_gain, entropy


class DecisionTreeClassifier(object):

    def __init__(self, max_features=lambda x: x, max_depth=10,
                 min_samples_split=2):
        """
        Arguments:
            max_features: A function that controls the number of features to
                randomly consider at each split. The argument will be the number
                of features in the data.
            max_depth: The maximum number of levels the tree can grow downwards
                before forcefully becoming a leaf.
            min_samples_split: The minimum number of samples needed at a node to
                justify a new node split.
        """

        self.max_features = max_features
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split

    def fit(self, X, y):
       # Build the tree by choosing decision rules for each node based on the data.

        n_features = X.shape[1]
        n_sub_features = int(self.max_features(n_features))
        feature_indices = random.sample(xrange(n_features), n_sub_features)

        self.trunk = self.create_tree(X, y, feature_indices, 0)

    def predict(self, X):
        #Predict the class of each sample in X.

        num_samples = X.shape[0]
        y = np.empty(num_samples)
        for j in xrange(num_samples):
            node = self.trunk

            while isinstance(node, Node):
                if X[j][node.feature_index] <= node.threshold:
                    node = node.branch_true
                else:
                    node = node.branch_false
            y[j] = node

        return y

    def create_tree(self, X, y, feature_indices, depth):

        if depth is self.max_depth or len(y) < self.min_samples_split or entropy(y) is 0:
            return mode(y)[0][0]

        feature_index, threshold = find_split(X, y, feature_indices)

        X_true, y_true, X_false, y_false = split(X, y, feature_index, threshold)
        if y_true.shape[0] is 0 or y_false.shape[0] is 0:
            return mode(y)[0][0]

        branch_true = self.create_tree(X_true, y_true, feature_indices, depth + 1)
        branch_false = self.create_tree(X_false, y_false, feature_indices, depth + 1)

        return Node(feature_index, threshold, branch_true, branch_false)


def find_split(X, y, feature_indices):
    #Return the best split rule for a tree node.

    n_features = X.shape[1]

    best_gain = 0
    best_feature_index = 0
    best_threshold = 0
    for feature_index in feature_indices:
        values = sorted(set(X[:, feature_index]))
        print values
        for j in xrange(len(values) - 1):
            threshold = (values[j] + values[j + 1]) / 2
            X_true, y_true, X_false, y_false = split(X, y, feature_index, threshold)
            gain = information_gain(y, y_true, y_false)

            if gain > best_gain:
                best_gain = gain
                best_feature_index = feature_index
                best_threshold = threshold
                print best_threshold
    return best_feature_index, best_threshold


class Node(object):
    #A node in a decision tree with the binary condition xi <= t.

    def __init__(self, feature_index, threshold, branch_true, branch_false):
        self.feature_index = feature_index
        self.threshold = threshold
        self.branch_true = branch_true
        self.branch_false = branch_false


def split(X, y, feature_index, threshold):
    #Splits X and y based on the binary condition xi <= threshold.

    X_true = []
    y_true = []
    X_false = []
    y_false = []

    for j in xrange(len(y)):
        if X[j][feature_index] <= threshold:
            X_true.append(X[j])
            y_true.append(y[j])
        else:
            X_false.append(X[j])
            y_false.append(y[j])

    X_true = np.array(X_true)
    y_true = np.array(y_true)
    X_false = np.array(X_false)
    y_false = np.array(y_false)

    return X_true, y_true, X_false, y_false


from sklearn import cross_validation
import numpy as np

f = open('dataset/iris.data', 'r')
X = []
y = []
for line in f:
    line = line.strip('\n').split(',')
    if len(line) != 5:
        continue
    if line[4] == "Iris-setosa":
        line[4] = 0
    elif line[4] == "Iris-versicolor":
        line[4] = 1
    elif line[4] == "Iris-virginica":
        line[4] = 2
    line_x = map(float, line[:4])
    X.append(line_x)
    y.append(line[4])
    
#print (X)

X = np.asarray(X)
y = np.asarray(y)

print y
train_X, test_X, train_y, test_y = cross_validation.train_test_split(X, y)

rfc_model = DecisionTreeClassifier()
rfc_model.fit(train_X,train_y)
prediction = rfc_model.predict(test_X)
print prediction

