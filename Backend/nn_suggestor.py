import csv
import gensim
import numpy as np
import tensorflow as tf
import pickle
import random
import os
import re


class NNSuggestor(object):

    def __init__(self, d):
        self.x = []
        self.y = []
        self.graph = tf.get_default_graph()
        self.sess = tf.Session()
        self.saver = None
        self.ingr2vec = gensim.models.Word2Vec.load("Backend/data/ingr2vec_model_"+str(d))

    def build_graph(self, layer_sizes):

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
        cos_dist = tf.losses.cosine_distance(tf.nn.l2_normalize(y_ph, dim=1),
                                             tf.nn.l2_normalize(pred, dim=1), dim=1)
        tf.summary.scalar(name='cosine_distance', tensor=cos_dist)
        tf.identity(cos_dist, 'cos_dist')
        lr_ph = tf.placeholder("float", name='lr_ph')
        optimizer = tf.train.AdamOptimizer(learning_rate=lr_ph).minimize(cos_dist, name='minimize')

    def explore(self):
        prev_input = ''
        x_input = ' '
        while x_input:
            try:
                x_input = input('Enter ingredients with space between: ').split()
                if '+' in x_input:
                    x_input.remove('+')
                    x_input.extend(prev_input)
                x_input = [re.sub('_', ' ', i) for i in x_input]
                prev_input = x_input
                x_vec = np.sum([self.ingr2vec[ingr] for ingr in x_input], axis=0)

                x_ph = self.graph.get_tensor_by_name('x_ph:0')
                pred = self.graph.get_tensor_by_name('pred:0')

                y_pred = self.sess.run(pred, {x_ph: np.expand_dims(x_vec, axis=0)})
                print(self.ingr2vec.most_similar(y_pred, topn=6))
            except KeyError:
                print('One ingredient not in vocabulary, try again.')
                pass

    def generate_training_data_from_freq(self, n=10000, save=True):

        try:
            with open('Backend/data/nn_freq_training_data_weighted.csv', 'r', newline='') as nn_freq_training_data:
                reader = csv.reader(nn_freq_training_data, delimiter=';', quotechar='|')
                for i, row in enumerate(reader):
                    y_temp_vec = np.squeeze(self.ingr2vec[row[-1]])
                    x_temp_vec = np.sum([self.ingr2vec[ingr] for ingr in row[:-1]], axis=0)
                    self.y.append(y_temp_vec)
                    self.x.append(x_temp_vec)
                    if i == n-1:
                        print('{} rows loaded from {}'.format(i+1, 'Backend/data/nn_freq_training_data_weighted.csv'))
                        return
                print('{} rows loaded from {}'.format(len(self.y), 'Backend/data/nn_freq_training_data_weighted.csv'))
        except FileNotFoundError:
            pass

        with open('Backend/data/nn_freq_training_data_weighted.csv', 'a+', newline='') as nn_freq_training_data:
            master = pickle.load(open('Backend/data/tasteline.pickle', 'rb'))
            writer = csv.writer(nn_freq_training_data, delimiter=';', quotechar='|')
            ingredients = pickle.load(open('Backend/data/ingredients.pickle', 'rb'))

            max_chosen = 6
            while len(self.y) < n:
                try:
                    r = random.randint(0, len(master)-1)
                    r_ingredients = list(set(master[r]['ingredients']))
                    r_weights = [ingredients[i]['main_freq']/ingredients[i]['freq'] for i in r_ingredients]
                    k = random.choices(range(1, max_chosen+1), range(1, max_chosen+1), k=1)[0]
                    if sum(r_weights):
                        row = list(set(random.choices(r_ingredients, r_weights, k=min(k, len(r_ingredients)-1))))
                        if len(row) > 1:
                            try:
                                y_temp_vec = np.squeeze(self.ingr2vec[row[-1]])
                                x_temp_vec = np.sum([self.ingr2vec[ingr] for ingr in row[:-1]], axis=0)
                                self.y.append(y_temp_vec)
                                self.x.append(x_temp_vec)
                                if save:
                                    writer.writerow(row[:-1] + [row[-1]])
                            except KeyError:
                                pass
                except ValueError:
                    pass
        if save:
            print('{} rows saved to {}'.format(n, 'Backend/data/nn_freq_training_data_weighted.csv'))

    def read_data(self, freq=True):

        self.x = []
        self.y = []

        if freq:
            filename = 'nn_freq_training_weighted.csv'
        else:
            filename = 'nn_real_training_data.csv'

        with open('Backend/data/'+filename, 'r', newline='') as nn_training_data:
            reader = csv.reader(nn_training_data, delimiter=';', quotechar='|')
            prev_row = []
            for row in reader:
                diff = set(row) - set(prev_row)
                if len(diff) == 1 and len(row) > 1:
                    try:
                        y_temp = np.squeeze(self.ingr2vec[diff])
                        x_temp = np.sum([self.ingr2vec[ingr] for ingr in prev_row], axis=0)
                        self.y.append(y_temp)
                        self.x.append(x_temp)
                    except KeyError:
                        pass
                prev_row = row

    def restore_model(self):
        checkpoint_dir = 'Backend/data/trained_nn/'
        new_saver = tf.train.import_meta_graph(checkpoint_dir + 'model.meta')
        new_saver.restore(self.sess, tf.train.latest_checkpoint(checkpoint_dir))
        tf.constant(checkpoint_dir, name='restored_model')
        print('Model restored from {}'.format(checkpoint_dir))

    def save_model(self):
        self.saver = tf.train.Saver(max_to_keep=1)
        try:
            os.mkdir('Backend/data/trained_nn/')
        except FileExistsError:
            pass
        save_path = self.saver.save(self.sess, 'Backend/data/trained_nn/model')
        print('Trained model saved to {}'.format(save_path))

    def suggest(self, combo, n):
        x_vec = np.sum([self.ingr2vec[ingr] for ingr in combo], axis=0)

        x_ph = self.graph.get_tensor_by_name('x_ph:0')
        pred = self.graph.get_tensor_by_name('pred:0')

        y_pred = self.sess.run(pred, {x_ph: np.expand_dims(x_vec, axis=0)})
        return self.ingr2vec.most_similar(y_pred, topn=n)

    def train(self, training_epochs=1000):

        # Parameters
        init_learning_rate = 0.01
        decay_factor = 1
        decay_freq = 500
        batch_size = 128
        display_step = 1

        # Get variable handles
        optimizer = self.graph.get_operation_by_name('minimize')
        cos_dist = self.graph.get_tensor_by_name('cos_dist:0')
        x_ph = self.graph.get_tensor_by_name('x_ph:0')
        y_ph = self.graph.get_tensor_by_name('y_ph:0')
        lr_ph = self.graph.get_tensor_by_name('lr_ph:0')
        summaries = tf.summary.merge_all()

        # Initializing uninitialized variables
        uninitialized = self.sess.run(tf.report_uninitialized_variables())
        uninitialized = [str(v)[2:-1] + ':0' for v in uninitialized]
        uninitialized = [v for v in tf.global_variables() if v.name in uninitialized]
        self.sess.run(tf.variables_initializer(var_list=uninitialized))

        # Initialize saver
        self.saver = tf.train.Saver(max_to_keep=1)
        try:
            os.mkdir('Backend/data/trained_nn/')
        except FileExistsError:
            pass

        # Initialize writers
        train_writer = tf.summary.FileWriter('Backend/data/trained_nn/train/', flush_secs=10)
        val_writer = tf.summary.FileWriter('Backend/data/trained_nn/val/', flush_secs=10)

        # Training cycle
        lr = init_learning_rate
        for epoch in range(training_epochs):
            try:
                avg_cost = 0.
                total_batch = int(len(self.x[:-1000]) / batch_size)
                # Loop over all batches
                for i in range(total_batch):
                    batch_x = self.x[i * batch_size:min((i + 1) * batch_size, len(self.x)-1001)]
                    batch_y = self.y[i * batch_size:min((i + 1) * batch_size, len(self.x)-1001)]
                    # Run optimization and cost ops
                    _, c, train_sum = self.sess.run([optimizer, cos_dist, summaries],
                                                    feed_dict={x_ph: batch_x, y_ph: batch_y, lr_ph: lr})
                    # Compute average loss
                    avg_cost += c / total_batch
                # Display logs per epoch step
                if epoch % display_step == 0:
                    print("Epoch:", '%04d' % (epoch + 1), "cost=", "{:.9f}".format(avg_cost))
                    train_writer.add_summary(summary=train_sum, global_step=epoch)

                    x_val = self.x[-1000:]
                    y_val = self.y[-1000:]
                    val_sum = self.sess.run(summaries, feed_dict={x_ph: x_val, y_ph: y_val, lr_ph: lr})
                    val_writer.add_summary(summary=val_sum, global_step=epoch)

                    self.saver.save(self.sess, 'Backend/data/trained_nn/model')
                if epoch % decay_freq == decay_freq - 1:
                    lr *= decay_factor
            except KeyboardInterrupt:
                print('Training stopped at epoch {}.'.format(epoch))
                return
        print("Training finished after {} epochs.".format(training_epochs))


if __name__ == "__main__":

    dim = 200
    suggestor = NNSuggestor(d=dim)
    suggestor.generate_training_data_from_freq(1000000)
    suggestor.build_graph(layer_sizes=(150, 100, 150, 200))
    # suggestor.restore_model()
    suggestor.train(training_epochs=100000)
    suggestor.save_model()
    suggestor.explore()
