from keras.models import Sequential
import keras.layers as layers
from keras import callbacks
import numpy as np
from sklearn.cross_validation import train_test_split
from lib import data_handler
import argparse

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--positive", help="input positive training dataset path")
parser.add_argument("-n", "--negative", help="input negative training dataset path")
parser.add_argument("-s", "--patchsize", help="pixel size of training dataset as tuple (height, width)")
parser.add_argument("-P", "--positivedatasize", help="number of positive training data")
parser.add_argument("-N", "--negativedatasize", help="number of negative training data")
args = parser.parse_args()

if args.positive:
    train_dir_pos = args.positive
if args.negative:
    train_dir_neg = args.negative
if args.patchsize:
    patchsize = args.patchsize
if args.positivedatasize:
    datasize_pos = args.positivedatasize
if args.negativedatasize:
    datasize_neg = args.negativedatasizea

X_train = []
y_train = []

# temporary variable declaration
train_dir_pos = "/mnt/hgfs/Shared/DaimlerBenchmark/Data/TrainingData/Pedestrians/48x96"
train_dir_neg = "/mnt/hgfs/Shared/DaimlerBenchmark/Data/TrainingData/NonPedestrians"
patchsize = (96, 48)
datasize_pos = 20000
datasize_neg = 60000
test_split = 0.1
###########################################################################################
print 'loading pedestrian dataset...'
data_handler.load_data_general(train_dir_pos, X_train, y_train,
                               format='pgm', label=1, datasize=datasize_pos)
data_handler.load_data_random_patches(train_dir_neg, X_train, y_train,
                                      format='pgm', label=0, patchsize=patchsize, datasize=datasize_neg)

print 'converting dataset to numpy format...'
X_train = np.asarray(X_train)
y_train = np.asarray(y_train)

# split training data for test usage
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=test_split)

print 'data preparation complete'

print 'training data shape : ' + str(X_train.shape)

print 'building model...'
model = Sequential()
model.add(layers.BatchNormalization(axis=1, input_shape=X_train[0].shape))
model.add(layers.Convolution2D(nb_filter=12, nb_row=5, nb_col=5,
                               activation='relu', border_mode='valid'))
model.add(layers.MaxPooling2D())
model.add(layers.Convolution2D(nb_filter=24, nb_row=3, nb_col=3,
                               activation='relu', border_mode='valid'))
model.add(layers.MaxPooling2D())
model.add(layers.Flatten())
model.add(layers.Dense(1000, activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(500, activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(1, activation='sigmoid'))

# "class_mode" defaults to "categorical". For correctly displaying accuracy
# in a binary classification problem, it should be set to "binary".
model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              class_mode='binary')
print 'building complete'

print 'training model...'
model.fit(X_train, y_train,
          nb_epoch=100,
          batch_size=32,
          verbose=1,
          shuffle=True,
          show_accuracy=True,
          validation_split=0.1,
          callbacks=[callbacks.EarlyStopping(patience=5, verbose=True)])
print 'training complete'

# temporary : skip evaluation for testing
"""
print 'evaluating model...'
score = model.evaluate(X_test, y_test, batch_size=32, verbose=1, show_accuracy=True)
print 'test accuracy : ' + str(score[1])
"""

print 'saving architecture and weights...'
json_string = model.to_json()
open('model.json', 'w').write(json_string)
model.save_weights('weights.h5')
