# -*- coding: utf-8 -*-
"""Audio_emotion

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13FAwhiRrScHx_wBn3_9O_kY9vrAIRxy1

Importing Important Libraries
"""

import kagglehub
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')
import librosa
import librosa.display
import IPython.display as ipd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping
import keras
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.layers import Dense, Conv1D, MaxPooling1D, Flatten, Dropout, BatchNormalization
import tensorflow as tf
from IPython.display import Audio
import random
from tensorflow.keras import layers, models
from sklearn.metrics import accuracy_score, classification_report
!pip install --upgrade librosa
print(librosa.__version__)
import soundfile as sf
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import cv2

"""Load the dataset

"""

# Download the dataset
path = kagglehub.dataset_download("uwrfkaggler/ravdess-emotional-speech-audio")

# Print the path where the dataset is saved
print("Path to dataset files:", path)
files_in_ravdess = os.listdir(path)
print(files_in_ravdess[:10])

"""Check if any metadata file or csv file"""

print("Files in dataset directory:", os.listdir(path))
possible_csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]

if possible_csv_files:
    # Load the first CSV file found (if any)
    csv_path = os.path.join(path, possible_csv_files[0])
    df = pd.read_csv(csv_path)

    # Print the columns in the DataFrame
    print("Columns in the dataset:", df.columns)
    print("First few rows of the dataset:\n", df.head())
else:
    print("No CSV file found in the dataset directory.")

actor_base_path = os.path.join(path, "audio_speech_actors_01-24")

# Define emotion labels based on the filename (RAVDESS emotion coding)
emotion_map = {
    '01': 'neutral',
    '02': 'calm',
    '03': 'happy',
    '04': 'sad',
    '05': 'angry',
    '06': 'fearful',
    '07': 'disgust',
    '08': 'surprised'
}

# Create a list to store the data
data = []

# List all actor directories in the base path
actor_dirs = [actor for actor in os.listdir(actor_base_path) if actor.startswith('Actor')]

# Process each actor folder
for actor_dir in actor_dirs:
    actor_path = os.path.join(actor_base_path, actor_dir)

    # List all audio files in the actor's folder
    audio_files = [f for f in os.listdir(actor_path) if f.endswith('.wav')]

    # Process each audio file
    for file in audio_files:
        # Split filename: <actor_id>-<emotion_id>-<intensity_id>-<file_name>.wav
        parts = file.split('-')

        actor_id = int(parts[0].replace('Actor', ''))  # Extract actor ID (e.g., "Actor_01" -> 1)
        emotion_code = parts[2]   # Emotion code is the third part
        intensity_code = parts[3] # Intensity is the fourth part

        # Map the emotion code to a human-readable label
        emotion = emotion_map.get(emotion_code, 'unknown')

        # Determine intensity (assuming 1 = low intensity, 2 = high intensity)
        intensity = 'high' if intensity_code == '2' else 'low'

        # Full file path
        file_path = os.path.join(actor_path, file)

        # Append the data as a row in the list
        data.append({
            'file_path': file_path,
            'actor_id': actor_id,
            'intensity': intensity,
            'emotion': emotion
        })

# Create the DataFrame
df_ravdess = pd.DataFrame(data)

# Display the first few rows of the DataFrame
print(df_ravdess.head())

"""Count the number of emotions"""



sad_count = df_ravdess[df_ravdess['emotion'] == 'sad'].shape[0]
print(f"Number of 'sad' emotion audio files: {sad_count}")

calm_count = df_ravdess[df_ravdess['emotion'] == 'calm'].shape[0]
print(f"Number of 'calm' emotion audio files: {calm_count}")

angry_count = df_ravdess[df_ravdess['emotion'] == 'angry'].shape[0]
print(f"Number of 'angry' emotion audio files: {angry_count}")

fearful_count = df_ravdess[df_ravdess['emotion'] == 'fearful'].shape[0]
print(f"Number of 'fearful' emotion audio files: {fearful_count}")

disgust_count = df_ravdess[df_ravdess['emotion'] == 'disgust'].shape[0]
print(f"Number of 'disgust' emotion audio files: {disgust_count}")

surprised_count = df_ravdess[df_ravdess['emotion'] == 'surprised'].shape[0]
print(f"Number of 'surprised' emotion audio files: {surprised_count}")

neutral_count = df_ravdess[df_ravdess['emotion'] == 'neutral'].shape[0]
print(f"Number of 'neutral' emotion audio files: {neutral_count}")

happy_count = df_ravdess[df_ravdess['emotion'] == 'happy'].shape[0]
print(f"Number of 'happy' emotion audio files: {happy_count}")



# Create the count plot for emotions
plt.figure(figsize=(10, 6))
sns.countplot(data=df_ravdess, x='emotion', palette='Set2')

# Add title and labels
plt.title('Count of Audio Files by Emotion', fontsize=14)
plt.xlabel('Emotion', fontsize=12)
plt.ylabel('Count of Audio Files', fontsize=12)
# Display the plot
plt.tight_layout()
plt.show()

"""Sample Audio

"""



path = df_ravdess.iloc[0]['file_path']
data, sample_rate = librosa.load(path)

# Plot the waveform of the audio
plt.figure(figsize=(14, 4))
librosa.display.waveshow(y=data, sr=sample_rate)
plt.title("Audio Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.show()

# Play the audio
Audio(path)

"""Analyse the audio using spectrogram and waveform"""

def waveplot(data, sr, emotion):
    plt.figure(figsize=(5,5))
    plt.title(emotion, size=20)
    librosa.display.waveshow(data, sr=sr)
    plt.show()

def spectrogram(data, sr, emotion):
    x = librosa.stft(data)
    xdb = librosa.amplitude_to_db(abs(x))
    plt.figure(figsize=(5,5))
    plt.title(emotion, size=20)
    librosa.display.specshow(xdb, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar()
unique_emotions = df_ravdess['emotion'].unique()

for emotion in unique_emotions:
    # Filter the DataFrame for the current emotion
    matching_rows = df_ravdess[df_ravdess['emotion'] == emotion]

    if matching_rows.empty:
        print(f"No audio files found for emotion: {emotion}")
        continue

    # Get the file path for the first matching row
    path = matching_rows['file_path'].iloc[0]

    # Load the audio file
    data, sampling_rate = librosa.load(path)

    # Plot waveform
    waveplot(data, sampling_rate, emotion)

    # Plot spectrogram
    spectrogram(data, sampling_rate, emotion)

    print(f"Playing audio for emotion: {emotion}")
    display(Audio(path))

df_ravdess['emotion'].value_counts()

"""Data Augmentation"""



def noise(data):
    noise_amp = 0.035*np.random.uniform()*np.amax(data)
    data = data + noise_amp*np.random.normal(size=data.shape[0])
    return data

# Function for stretching the audio
def stretch(data, rate):
    return librosa.effects.time_stretch(data, rate=rate)

# Function for shifting the audio
def shift(data):
    shift_range = int(np.random.uniform(low=-5, high = 5)*1000)
    return np.roll(data, shift_range)

# Function for adding pitch to audio
def pitch(data, sampling_rate, pitch_factor):
    return librosa.effects.pitch_shift(data, sr=sampling_rate, n_steps=pitch_factor*12)

path = np.array(df_ravdess['file_path'])[1]  # Index 1 for the second file

# Load the audio file using librosa
data, sample_rate = librosa.load(path)

augmentations = [
    ('Noise', noise, None),  # Noise function with no extra parameters
    ('Time Stretch', stretch, {'rate': 1.2}),  # Stretch with a rate factor
    ('Pitch Shift', pitch, {'sampling_rate': sample_rate, 'pitch_factor': 1.0}),  # Pitch shift
    ('Time Shift', shift, None)  # Time shift function with no extra parameters
]

# Apply each augmentation in a loop and store results
augmented_data = {}

for name, func, params in augmentations:
    if params:
        augmented_data[name] = func(data, **params)  # Apply the function with parameters
    else:
        augmented_data[name] = func(data)  # Apply the function without parameters

# Plot the original and augmented waveforms
plt.figure(figsize=(14, 10))

# Original Audio
plt.subplot(5, 1, 1)
librosa.display.waveshow(data, sr=sample_rate)
plt.title("Original Audio")

# Plot augmented audio results from the loop
for i, (name, aug_data) in enumerate(augmented_data.items(), 2):
    plt.subplot(5, 1, i)
    librosa.display.waveshow(aug_data, sr=sample_rate)
    plt.title(f"Augmented Audio - {name}")

plt.tight_layout()
plt.show()
for name, aug_data in augmented_data.items():
    print(f"Playing {name} augmented audio...")
    display(Audio(aug_data, rate=sample_rate))

"""Features extraction

"""

def extract_features(data, sample_rate):
    # ZCR
    result = np.array([])
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
    result=np.hstack((result, zcr)) # stacking horizontally

    # Chroma_stft
    stft = np.abs(librosa.stft(data))
    chroma_stft = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
    result = np.hstack((result, chroma_stft)) # stacking horizontally

    # MFCC
    mfcc = np.mean(librosa.feature.mfcc(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mfcc)) # stacking horizontally

    # Root Mean Square Value
    rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
    result = np.hstack((result, rms)) # stacking horizontally

    # MelSpectogram
    mel = np.mean(librosa.feature.melspectrogram(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mel)) # stacking horizontally

    return result
def augment_and_extract_features(path, n_augment=100):
    data, sample_rate = librosa.load(path, duration=2.5, offset=0.6)

    # Extract features from the original audio
    original_features = extract_features(data, sample_rate)

    # Randomly choose an augmentation technique
    augmentation_methods = [noise, stretch, shift, pitch]
    method = random.choice(augmentation_methods)

    # Apply the chosen augmentation
    if method == pitch:
        augmented_data = method(data, sample_rate, pitch_factor=np.random.uniform(-5, 5))
    elif method == stretch:
        augmented_data = method(data, rate=np.random.uniform(0.5, 1.5))
    else:
        augmented_data = method(data)
        # Extract features from the augmented audio
    augmented_features = extract_features(augmented_data, sample_rate)

    # Stack original and augmented features vertically
    combined_features = np.vstack((original_features, augmented_features))

    return combined_features

X, Y = [], []
for path, emotion in zip(df_ravdess.file_path, df_ravdess.emotion):
    features = augment_and_extract_features(path)  # Assuming this returns a list of tensors
    for feature in features:
        X.append(feature)
        Y.append(emotion)


# Convert list to numpy arrays if necessary
X = np.array(X)
Y = np.array(Y)

# Shuffle the dataset
X, Y = shuffle(X, Y, random_state=42)
Features = pd.DataFrame(X)
Features['labels'] = Y
Features.to_csv('features.csv', index=False)
Features.head()

print(df_ravdess.shape)
df_ravdess.head()

len(X), len(Y)

"""We have applied data augmentation and extracted the features for each audio files and saved them.

As of now we have extracted the data, now we need to normalize and split our data for training and testing.
"""

X = Features.iloc[: ,:-1].values
Y = Features['labels'].values
#As this is a multiclass classification problem onehotencoding our Y.
encoder = OneHotEncoder()
Y = encoder.fit_transform(np.array(Y).reshape(-1,1)).toarray()

"""Splitting the data

"""

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0, shuffle=True)
x_train.shape, y_train.shape, x_test.shape, y_test.shape

"""Standardise the data"""

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test = scaler.transform(x_test)
x_train.shape, y_train.shape, x_test.shape, y_test.shape

x_train = np.expand_dims(x_train, axis=2)
x_test = np.expand_dims(x_test, axis=2)
x_train.shape, y_train.shape, x_test.shape, y_test.shape

"""Now Create Model"""



# Define a simple 1D CNN model
model = Sequential([
    Conv1D(256, kernel_size=5, activation='relu', padding='same', input_shape=(x_train.shape[1], 1)),
    MaxPooling1D(pool_size=5, strides=2, padding='same'),

    Conv1D(128, kernel_size=5, activation='relu', padding='same'),
    MaxPooling1D(pool_size=5, strides=2, padding='same'),
    Dropout(0.2),

    Conv1D(64, kernel_size=5, activation='relu', padding='same'),
    MaxPooling1D(pool_size=5, strides=2, padding='same'),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(8, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Display the model summary
model.summary()

print(x_train.shape,x_test.shape,y_train.shape,y_test.shape)

history = model.fit(
    x_train, y_train,
    validation_data=(x_test, y_test),
    batch_size=64,
    epochs=80,
    verbose=1
)

"""Evaluating the model"""

test_loss, test_accuracy = model.evaluate(x_test, y_test)
print(f"Test Accuracy: {test_accuracy*100:0.2f}")


train_loss,train_accuracy=model.evaluate(x_train,y_train)
print(f"Train Accuracy: {train_accuracy*100:.2f}")

"""Prediction

"""

pred_test = model.predict(x_test)
y_pred = encoder.inverse_transform(pred_test)

y_test = encoder.inverse_transform(y_test)

df = pd.DataFrame(columns=['Predicted Labels', 'Actual Labels'])
df['Predicted Labels'] = y_pred.flatten()
df['Actual Labels'] = y_test.flatten()
for i in range(14,18):
  print(df.loc[i])

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize = (12, 10))
cm = pd.DataFrame(cm , index = [i for i in encoder.categories_] , columns = [i for i in encoder.categories_])
sns.heatmap(cm, linecolor='white', cmap='Blues', linewidth=1, annot=True, fmt='')
plt.title('Confusion Matrix', size=20)
plt.xlabel('Predicted Labels', size=14)
plt.ylabel('Actual Labels', size=14)
plt.show()

print(classification_report(y_test, y_pred))