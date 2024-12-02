# -*- coding: utf-8 -*-
"""
Created on Sun Dic  01 14:18:41 2024

@author: DJIMENEZ
"""
# Librerias necesarias ------------------------------------------------------------------------------------------

import os

# NLP
import re
from collections import Counter

import gensim  # para cargar modelo w2v

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical

import tensorflow
from tensorflow.keras import Sequential, Model, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import (
    LSTM,
    Embedding,
    Dense,
    TimeDistributed,
    Dropout,
    Bidirectional,
    Flatten,
    GlobalAveragePooling1D,
    MaxPool1D,
    GRU,
    Concatenate
    )
from tensorflow.keras.initializers import Constant
from tensorflow.keras.utils import plot_model
from tensorflow.keras.callbacks import EarlyStopping
from keras.layers import GlobalMaxPooling1D

# Guardar
import pickle


# Funciones ------------------------------------------------------------------------------------------


def get_vocabulario(pandas_series):
    """
    Procesa una serie de pandas con cadenas de texto y devuelve una lista con todas las palabras y signos de puntuación
    que contiene, ordenadas de mayor a menor frecuencia.

    Args:
        pandas_series (pandas.Series): Serie de pandas que contiene frases o cadenas de texto.

    Returns:
        list: Lista de palabras y signos de puntuación ordenadas por frecuencia, desde la más común hasta la menos común.
    """
    # Unir todas las frases de la serie en una sola cadena de texto
    texto = " ".join(sec for sec in pandas_series)

    # Usar expresiones regulares para separar palabras y puntuaciones
    lista_palabras = re.findall(r'\w+|[^\w\s]', texto)

    # Contar la frecuencia de cada palabra o signo usando Counter
    x = Counter(lista_palabras)

    # Devolver solo las palabras, ordenadas por frecuencia de mayor a menor
    return [i for i, _ in x.most_common()]



def get_dict_map(token_or_tag,pandas_series):
    """
    Crea dos diccionarios de mapeo: uno que convierte tokens o etiquetas a índices y otro que convierte índices a tokens o etiquetas.

    Dependiendo de si `token_or_tag` es 'token' o 'tag', la función crea los diccionarios para tokens (palabras) o etiquetas
    (tags de clasificación, como etiquetas de secuencias en tareas de NLP).

    Args:
        token_or_tag (str): Si es 'token', se genera un diccionario para los tokens de las oraciones;
                            si es 'tag', se genera un diccionario para las etiquetas.

    Returns:
        tuple: Una tupla con dos diccionarios:
            - tok2idx (dict): Diccionario que mapea cada token o etiqueta a un índice.
            - idx2tok (dict): Diccionario que mapea cada índice a su token o etiqueta correspondiente.
    """
    if token_or_tag == 'token':
        # Si se están procesando los tokens, añadimos 'PAD_token' al vocabulario.
        # 'PAD_token' es un token especial que se usará para hacer padding de las oraciones, asegurando que todas
        # tengan la misma longitud.
        vocab = ['PAD_token'] + get_vocabulario(pandas_series)  # 'vocabulario' genera una lista de palabras a partir de las oraciones.

    elif token_or_tag == 'tag':
        # Si se están procesando las etiquetas (tags), se genera el vocabulario a partir de las etiquetas de las oraciones.
        vocab = get_vocabulario(pandas_series)

    # Crear un diccionario que mapea índices a tokens/etiquetas
    idx2tok = {idx: tok for idx, tok in enumerate(vocab)}

    # Crear un diccionario que mapea tokens/etiquetas a índices
    tok2idx = {tok: idx for idx, tok in enumerate(vocab)}

    # Retornar ambos diccionarios: de token/etiqueta a índice y de índice a token/etiqueta
    return tok2idx, idx2tok



# Ejemplo de uso
if __name__ == "__main__":

    import sys

    # Obtener la ruta del directorio del archivo de script actual para establecer el directorio de trabajo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(script_dir)
    os.chdir(script_dir)

    # Definimos la longitud de la reseñas a ingresar al modelo. Tomamos el cuantil 90%
    max_len = int(df.loc[df['polarity']=='negative', 'length'].quantile(0.90))+1
    max_len

    # Creamos las secuencias de los textos y la variable objetivo
    df['text_idx'] = df['text'].apply(lambda x: list(map(token2idx.get, re.findall(r'\w+|[^\w\s]', x))))
    df['polarity_val'] = np.where(df['polarity'] == 'positive', 1, 0).astype(int)
    

    # Ajustamos las secuencias de las reseñas para fijar el largo
    pad_tokens = pad_sequences(df['text_idx'], maxlen=max_len,
                            dtype='int32', padding='post',
                            value = token2idx['PAD_token'])

    df['polarity_val'] = df['polarity_val'].astype(int)
    tags = df['polarity_val']

    # Obtenemos el modelo preentrenado de word2vec

    # file_w2vec =  '/content/drive/MyDrive/ML_&_AI_for_the_Working_Analyst/Examen_modulo_3_RNN/GoogleNews-vectors-negative300.bin.gz'
    # w2v = gensim.models.KeyedVectors.load_word2vec_format(file_w2vec,  binary=True)

    # Creamos un diccionario de nuestro vocabulario y su correspondiente representacion de vectores
    # dic_tokens_word2vec  = {}
    # palabras_sin_embedding =[]
    # for token in token2idx.keys():
    #   try:
    #     dic_tokens_word2vec[token] = w2v[token]
    #   except:
    #     palabras_sin_embedding.append(token)

    # Guardamos el diccionario acotado para uso posterior
    dic_tokens_word2vec_path = '/content/drive/MyDrive/ML_&_AI_for_the_Working_Analyst/Examen_modulo_3_RNN'
    # pickle.dump(dic_tokens_word2vec, open (dic_tokens_word2vec_path + "dic_tokens_ner_w2v.pkl", 'wb'))

    # Importamos el diccionario de vectores para su uso
    dic_tokens_word2vec = pickle.load(open(dic_tokens_word2vec_path + "dic_tokens_ner_w2v.pkl", 'rb'))
    palabras_sin_embedding = [tok for tok in token2idx.keys() if tok not in dic_tokens_word2vec.keys()]

    # Vemos cuantas palabras no tienen un vector asociado
    print(f'Palabras sin embedding: {len(palabras_sin_embedding)}')

    # Creamos la matriz de embeddings para inicializar el modelo
    num_tokens = len(token2idx.keys())
    n_tags = df['polarity_val'].nunique()
    embedding_dim = 300
    embedding_matrix = np.zeros((num_tokens, embedding_dim))
    for token, i in token2idx.items():
        if token in dic_tokens_word2vec.keys():
            embedding_matrix[i] = dic_tokens_word2vec[token]

    # Fijamos las semillas
    from numpy.random import seed
    seed(25102024)
    tensorflow.random.set_seed(25102024)

    # Dividimos los datos en train y test
    train_tokens, test_tokens, train_tags, test_tags = train_test_split(
    pad_tokens, tags, test_size=0.1, train_size=0.9, random_state=2020)

    print(
    f'''train_tokens: {len(train_tokens)}
    train_tags: {len(train_tags)}

    test_tokens: {len(test_tokens)}
    test_tags: {len(test_tags)}'''
    )

    # Arquitectura del modelo

    input = Input(shape = (max_len,))

    # Capa de Embedding
    embedding = Embedding(input_dim = num_tokens,
                        output_dim = 300,
                        embeddings_initializer = Constant(embedding_matrix),
                        trainable = False)(input)
    # Capa 1 LSTM Bidireccional
    LSTM_Bi = Bidirectional(LSTM(units = 200,
                                return_sequences = False, # Solo se quiere el último estado oculto
                                recurrent_dropout = 0.2, dropout = 0.2  # Para evitar sobreajuste
                                ))(embedding)

    # Capa de Salida con funcion de activacion sigmoide para poder interpretar como la probabilidad y hacer la clasifiacion binaria
    output = Dense(1, activation="sigmoid")(LSTM_Bi)

    Classification_model = Model(input, output)  # unión del modelo
    Classification_model.summary()

    # Grafica de la arquitectura del modelo
    plot_model(
        Classification_model,
        show_shapes=True,
        show_dtype=False,
        show_layer_names=True,
        rankdir="TD",
        dpi=50,
    )

    # Compile model
    # Classification_model.compile(optimizer='adam',         # el optimizador sirve para encontrar los pesos que minimizan la función de pérdida
    #                                             # adam: stochastic gradient descent adaptativo
    #                                             # https://www.tensorflow.org/api_docs/python/tf/keras/optimizers
    #                   loss="binary_crossentropy", # función que evalua que tan bien el algoritmo modela el conjunto de datos
    #                                                    # https://www.tensorflow.org/api_docs/python/tf/keras/losses
    #                   metrics=['accuracy'])