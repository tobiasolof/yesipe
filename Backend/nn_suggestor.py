import csv
import gensim
import numpy as np
import tensorflow as tf
import pickle
import random


class NNSuggestor(object):

    def __init__(self):
        self.x = []
        self.y = []
        self.graph = tf.get_default_graph()
        self.sess = tf.Session()

    def read_data(self):
        ingr2vec = gensim.models.Word2Vec.load("Backend/data/ingr2vec_model")

        with open('Backend/data/nn_training_data.csv', 'r', newline='') as nn_training_data:
            reader = csv.reader(nn_training_data, delimiter=';', quotechar='|')
            prev_row = []
            for row in reader:
                diff = set(row) - set(prev_row)
                if len(diff) == 1 and len(row) > 1:
                    try:
                        y_temp = np.squeeze(ingr2vec[diff])
                        x_temp = np.sum([ingr2vec[ingr] for ingr in prev_row], axis=0)
                        self.y.append(y_temp)
                        self.x.append(x_temp)
                    except KeyError:
                        pass
                prev_row = row

    def generate_training_data_from_freq(self, n=5000):
        ingr2vec = gensim.models.Word2Vec.load("Backend/data/ingr2vec_model")
        master = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))

        while len(self.y) < n:
            try:
                r = random.randint(0, len(master)-1)
                ingredients = master[r]['tags']['main_ingr']
                k = random.randint(1, 5)
                x_temp = random.sample(ingredients, k)
                y_temp = random.sample(ingredients, 1)
                if y_temp[0] not in x_temp:
#                    continue
#                    y_temp = random.sample(ingredients, 1)
#                    print(x_temp)
#                    input(y_temp)
                    try:
                        y_temp = np.squeeze(ingr2vec[y_temp])
                        x_temp = np.sum([ingr2vec[ingr] for ingr in x_temp], axis=0)
                        self.y.append(y_temp)
                        self.x.append(x_temp)
                    except KeyError:
                        pass
            except ValueError:
                pass

    def train_nn(self, layer_sizes=(30, 50), training_epochs=100):

        # Parameters
        init_learning_rate = 0.01
        decay_factor = 0.96
        decay_freq = 500
        batch_size = 128
        display_step = 10
        embedding_size = np.shape(self.x)[1]

        # tf Graph input
        x_ph = tf.placeholder("float", [None, embedding_size], name='x_ph')
        y_ph = tf.placeholder("float", [None, embedding_size], name='y_ph')

        # Create model
        def multilayer_perceptron(x, weights, biases):
            layers = []
            for i in range(len(layer_sizes)):
                if i == 0:
                    layers.append(tf.add(tf.matmul(x, weights['h' + str(i)]), biases['b' + str(i)]))
                else:
                    layers.append(tf.add(tf.matmul(layers[i - 1], weights['h' + str(i)]), biases['b' + str(i)]))
                if i != len(layer_sizes) - 1:
                    layers[i] = tf.nn.relu(layers[i])
            return layers[-1]

        # Store layers weight & bias
        weights = {}
        for i in range(len(layer_sizes)):
            if i == 0:
                weights['h' + str(i)] = tf.Variable(tf.random_normal([embedding_size, layer_sizes[i]]))
            else:
                weights['h' + str(i)] = tf.Variable(tf.random_normal([layer_sizes[i - 1], layer_sizes[i]]))
        biases = {}
        for i in range(len(layer_sizes)):
            biases['b' + str(i)] = tf.Variable(tf.random_normal([layer_sizes[i]]))

        # Construct model
        pred = multilayer_perceptron(x_ph, weights, biases)
        tf.identity(pred, 'pred')

        # Define loss and optimizer
        cos_dist = tf.losses.cosine_distance(tf.nn.l2_normalize(y_ph, dim=1), tf.nn.l2_normalize(pred, dim=1), dim=1)
        lr_ph = tf.placeholder("float")
        optimizer = tf.train.AdamOptimizer(learning_rate=lr_ph).minimize(cos_dist)

        # Initializing the variables
        init = tf.global_variables_initializer()

        # Launch the graph
        self.sess.run(init)

        # Training cycle
        lr = init_learning_rate
        for epoch in range(training_epochs):
            avg_cost = 0.
            total_batch = int(len(self.x) / batch_size)
            # Loop over all batches
            for i in range(total_batch):
                batch_x = self.x[i * batch_size:(i + 1) * batch_size]
                batch_y = self.y[i * batch_size:(i + 1) * batch_size]
                # Run optimization op (backprop) and cost op (to get loss value)
                _, c = self.sess.run([optimizer, cos_dist], feed_dict={x_ph: batch_x, y_ph: batch_y, lr_ph: lr})
                # Compute average loss
                avg_cost += c / total_batch
            # Display logs per epoch step
            if epoch % display_step == 0:
                print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))
            if epoch % decay_freq == decay_freq-1:
                lr *= decay_factor
        print("Optimization Finished.")

    def predict(self):
        x_input = ' '
        while x_input:
            try:
                ingr2vec = gensim.models.Word2Vec.load("Backend/data/ingr2vec_model")

                x_input = input('Enter ingredients with space between: ').split()
                x_vec = np.sum([ingr2vec[ingr] for ingr in x_input], axis=0)

                x_ph = tf.get_default_graph().get_tensor_by_name('x_ph:0')
                pred = tf.get_default_graph().get_tensor_by_name('pred:0')

                y_pred = self.sess.run(pred, {x_ph: np.expand_dims(x_vec, axis=0)})
                print(ingr2vec.most_similar(y_pred, topn=6))
            except KeyError:
                print('One ingredient not in vocabulary, try again.')
                pass

if __name__ == "__main__":

    suggestor = NNSuggestor()
    suggestor.generate_training_data_from_freq(1000000)
    # suggestor.read_data()
    suggestor.train_nn(layer_sizes=(40, 40, 50), training_epochs=1000)
    suggestor.predict()
