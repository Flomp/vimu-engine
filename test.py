import music21

from repositories.AugmentedNet.inference import augmented_net

if __name__ == '__main__':
    s = music21.corpus.parse('bwv66.6')
    s_annotated = augmented_net.predict(s)

    s_annotated.show()
