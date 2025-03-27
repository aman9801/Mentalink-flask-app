import librosa
import numpy as np

# Function to extract MFCC features from audio
def extract_mfcc(audio_file, sr=16000, n_mfcc=13):
    y, sr = librosa.load(audio_file, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc.mean(axis=1)  # Return the mean of MFCC coefficients across time


# Function to extract Pitch (fundamental frequency) from audio
def extract_pitch(audio_file, sr=16000):
    y, sr = librosa.load(audio_file, sr=sr)
    pitch, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C1'), fmax=librosa.note_to_hz('C8'))
    pitch = pitch[voiced_flag]  # Use only voiced parts
    return np.mean(pitch) if len(pitch) > 0 else 0


# Function to extract Spectral Features: Centroid, Roll-off, Flux, Bandwidth
def extract_spectral_features(audio_file, sr=16000):
    y, sr = librosa.load(audio_file, sr=sr)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    spectral_flux = librosa.onset.onset_strength(y=y, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)

    # Return the mean value of these spectral features
    return spectral_centroid.mean(), spectral_rolloff.mean(), spectral_flux.mean(), spectral_bandwidth.mean()


# Function to extract all features from the audio file
def extract_features(audio_file):
    mfcc = extract_mfcc(audio_file)
    pitch = extract_pitch(audio_file)
    spectral_centroid, spectral_rolloff, spectral_flux, spectral_bandwidth = extract_spectral_features(audio_file)

    # Combine all the features into a single feature vector
    feature_vector = np.hstack([mfcc, pitch, spectral_centroid, spectral_rolloff, spectral_flux, spectral_bandwidth])

    return feature_vector