import music21
import numpy as np
import pandas as pd
from tensorflow import keras

from .cache import forceTonicization, getTonicizationScaleDegree
from .chord_vocabulary import frompcset, cosineSimilarity
from .input_representations import available_representations as availableInputs
from .output_representations import (
    available_representations as availableOutputs,
)
from .score_parser import parseScore
from .utils import padToSequenceLength

inversions = {
    "triad": {
        0: "",
        1: "6",
        2: "64",
    },
    "seventh": {
        0: "7",
        1: "65",
        2: "43",
        3: "2",
    },
}


def formatRomanNumeral(rn, key):
    """Format the Roman numeral label for end-user presentation."""
    # Something of "I" and "I" of something
    if rn == "I/I":
        rn = "I"
    return rn


def solveChordSegmentation(df):
    return df.dropna().loc[df.HarmonicRhythm7 == 0]


def resolveRomanNumeralCosine(b, t, a, s, pcs, key, numerator, tonicizedKey):
    pcsetVector = np.zeros(12)
    chord = music21.chord.Chord(f"{b}2 {t}3 {a}4 {s}5")
    for n in chord.pitches:
        pcsetVector[n.pitchClass] += 1
    for pc in pcs:
        pcsetVector[pc] += 1
    chordNumerator = music21.roman.RomanNumeral(
        numerator.replace("Cad", "Cad64"), tonicizedKey
    ).pitchClasses
    for pc in chordNumerator:
        pcsetVector[pc] += 1
    smallestDistance = -2
    for pcs in frompcset:
        v2 = np.zeros(12)
        for p in pcs:
            v2[p] = 1
        similarity = cosineSimilarity(pcsetVector, v2)
        if similarity > smallestDistance:
            pcset = pcs
            smallestDistance = similarity
    if tonicizedKey not in frompcset[pcset]:
        # print("Forcing a tonicization")
        candidateKeys = list(frompcset[pcset].keys())
        # prioritize modal mixture
        tonicizedKey = forceTonicization(key, candidateKeys)
    rnfigure = frompcset[pcset][tonicizedKey]["rn"]
    chord = frompcset[pcset][tonicizedKey]["chord"]
    quality = frompcset[pcset][tonicizedKey]["quality"]
    chordtype = "seventh" if len(pcset) == 4 else "triad"
    # if you can't find the predicted bass
    # in the pcset, assume root position
    inv = chord.index(b) if b in chord else 0
    invfigure = inversions[chordtype][inv]
    if invfigure in ["65", "43", "2"]:
        rnfigure = rnfigure.replace("7", invfigure)
    elif invfigure in ["6", "64"]:
        rnfigure += invfigure
    rn = rnfigure
    if numerator == "Cad" and inv == 2:
        rn = "Cad64"
    if tonicizedKey != key:
        denominator = getTonicizationScaleDegree(key, tonicizedKey)
        rn = f"{rn}/{denominator}"
    chordLabel = f"{chord[0]}{quality}"
    if inv != 0:
        chordLabel += f"/{chord[inv]}"
    return rn, chordLabel


class AugmentedNet:
    def __init__(self):
        self.model = keras.models.load_model('repositories/AugmentedNet/AugmentedNet.hdf5')

    def predict(self, s: music21.stream, include_roman_numerals=True):
        df = parseScore(s)
        inputs = [l.name.rsplit("_")[1] for l in self.model.inputs]
        encodedInputs = [availableInputs[i](df) for i in inputs]
        outputLayers = [l.name.split("/")[0] for l in self.model.outputs]
        seqlen = self.model.inputs[0].shape[1]
        modelInputs = [
            padToSequenceLength(i.array, seqlen, value=-1) for i in encodedInputs
        ]
        predictions = self.model.predict(modelInputs, verbose=0)
        predictions = [p.reshape(1, -1, p.shape[2]) for p in predictions]
        dfdict = {}
        for outputRepr, pred in zip(outputLayers, predictions):
            predOnehot = np.argmax(pred[0], axis=1).reshape(-1, 1)
            decoded = availableOutputs[outputRepr].decode(predOnehot)
            dfdict[outputRepr] = decoded
        dfout = pd.DataFrame(dfdict)
        scoreLength = len(dfout.index)
        paddedIndex = np.full((scoreLength,), np.nan)
        paddedMeasure = np.full((scoreLength,), np.nan)
        paddedIndex[: len(df.index)] = df.index
        paddedMeasure[: len(df.s_measure)] = df.s_measure
        dfout["offset"] = paddedIndex
        dfout["measure"] = paddedMeasure
        chords = solveChordSegmentation(dfout)

        ts = {
            (ts.measureNumber, float(ts.beat)): ts.ratioString
            for ts in s.flat.getElementsByClass("TimeSignature")
        }
        schord = s.flat.notesAndRests
        schord.metadata = s.metadata
        # remove all lyrics from score
        # for note in s.recurse().notes:
        #     note.lyrics = []
        prevkey = ""
        for analysis in chords.itertuples():
            notes = []
            for n in schord.getElementsByOffset(analysis.offset):
                if isinstance(n, music21.note.Note):
                    notes.append((n, n.pitch.midi))
                elif isinstance(n, music21.chord.Chord) and not isinstance(
                        n, music21.harmony.NoChord
                ):
                    notes.append((n, n[0].pitch.midi))
            if not notes:
                continue
            bass = sorted(notes, key=lambda n: n[1])[0][0]
            thiskey = analysis.LocalKey38
            tonicizedKey = analysis.TonicizedKey38
            pcset = analysis.PitchClassSet121
            numerator = analysis.RomanNumeral31
            rn2, _ = resolveRomanNumeralCosine(
                analysis.Bass35,
                analysis.Tenor35,
                analysis.Alto35,
                analysis.Soprano35,
                pcset,
                thiskey,
                numerator,
                tonicizedKey,
            )
            if thiskey != prevkey:
                bass.addLyric(f"{prevkey}→{thiskey}")
                prevkey = thiskey

            if include_roman_numerals:
                bass.addLyric(formatRomanNumeral(rn2, thiskey))
        return s


augmented_net = AugmentedNet()
