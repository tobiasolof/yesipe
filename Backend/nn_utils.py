import numpy as np
from keras import backend as k
from keras import Model
from keras.layers import Input, Embedding, Lambda, Dense


MAX_SEQUENCE_LENGTH = 20


def chosen_to_ind_array(chosen, ingr2vec):
    chosen_ind = [ingr2vec.wv.index2word.index(i) + 1 for i in chosen]
    chosen_ind += [0] * (MAX_SEQUENCE_LENGTH - len(chosen_ind))
    chosen_ind = np.array([chosen_ind])
    return chosen_ind


def recreate_w2v_model(ingr2vec):
    input_layer = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')

    embedding_layer = Embedding(
        ingr2vec.wv.vectors.shape[0] + 1,
        ingr2vec.wv.vectors.shape[1],
        weights=[np.insert(ingr2vec.wv.vectors, 0, np.zeros(ingr2vec.wv.vectors.shape[1]), axis=0)],
        input_length=MAX_SEQUENCE_LENGTH,
        trainable=True
    )(input_layer)

    embedding_sum = Lambda(lambda x: k.sum(x, axis=1), name='embedding_sum')(embedding_layer)

    prediction_layer = Dense(
        units=ingr2vec.trainables.syn1neg.shape[0],
        weights=(ingr2vec.trainables.syn1neg.T, np.zeros(ingr2vec.trainables.syn1neg.shape[0])),
        activation='softmax'
    )(embedding_sum)

    model = Model(inputs=input_layer, outputs=prediction_layer)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model


# TODO: Add min_conf
def predict_next(chosen, model, ingr2vec, n=1):
    x = chosen_to_ind_array(chosen, ingr2vec)
    pred_vector = model.predict(x)
    pred_ingr = [(ingr2vec.wv.index2word[i], pred_vector[0][i])
                 for i in pred_vector[0].argsort()[::-1][:n]]
    return pred_ingr


def get_embedding(chosen, model, ingr2vec):
    f = k.function([model.input], [model.get_layer('embedding_sum').output])
    x = chosen_to_ind_array(chosen, ingr2vec)
    return f([x])[0][0]


def train(model, ingr2vec, chosen, choice):
    x = chosen_to_ind_array(chosen, ingr2vec)
    y = np.zeros(len(ingr2vec.wv.vocab))
    y[ingr2vec.wv.index2word.index(choice)] = 1
    y = np.expand_dims(y, 0)
    model.fit(x, y, epochs=1, verbose=0)


# TODO: Implement this
def most_similar():
    return
