from typing import Optional, Union, List

from mido import MidiFile, MetaMessage, Message, tick2second


class SimpleMidiNoteOperation():
    ON = "note_on"
    OFF = "note_off"


class SimpleMidiNote():
    def __init__(self, operation, real_time, offset_time, note):
        self.operation = operation
        self.real_time = real_time
        self.offset_time = offset_time
        self.note = note

    def __str__(self):
        return "SimpleMidiNote: {} time={} offset={} note={}".format(self.operation,
                                                                     self.real_time,
                                                                     self.offset_time,
                                                                     self.note)

    def get_copy(self, note_offset=0):
        return self.__class__(self.operation, self.real_time, self.offset_time, self.note + note_offset)

    @classmethod
    def load_from_midi_message(cls, msg: Union[Message, MetaMessage]):
        if isinstance(msg, Message):
            msg_type = msg.dict()["type"]
            if msg_type not in ["note_on", "note_off"]:
                return None
            return cls(msg_type, 0, msg.dict()["time"], msg.dict()["note"])
        else:
            return None


class SimpleMidiFile():
    def __init__(self, name, tick_per_beat, tempo, notes):
        self.name = name
        self.tick_per_beat = tick_per_beat
        self.tempo = tempo
        self._notes: List[SimpleMidiNote] = notes
        self.__calculate_absolute_time()

    def get_copy(self, note_offset=0):
        return self.__class__(self.name, self.tick_per_beat, self.tempo, self.get_notes(note_offset=note_offset))

    @property
    def notes(self):
        return self._notes

    def get_notes(self, note_offset=0):
        return list(map(lambda n: n.get_copy(note_offset=note_offset),
                        self._notes))

    @classmethod
    def load_from_midi_file(cls, name, midifile: MidiFile, track_index=None):
        tpb = midifile.ticks_per_beat
        tempo = cls.__load_tempo(midifile)
        if track_index is None:
            notes = list(filter(lambda x: x is not None,
                                [SimpleMidiNote.load_from_midi_message(msg) for msg in midifile]))
        else:
            notes = cls.__load_track(midifile, track_index=track_index)
        return cls(name, tpb, tempo, notes)

    @classmethod
    def __load_track(cls, midifile, track_index):
        notes = []
        tpb = midifile.ticks_per_beat
        tempo = cls.__load_tempo(midifile)
        for i, track in enumerate(midifile.tracks):
            if track_index != i:
                continue
            for msg in track:
                msg: Message
                if msg.dict().get("time") is None:
                    continue
                if msg.dict()["time"] > 0:
                    delta = tick2second(msg.dict()["time"], tpb, tempo)
                else:
                    delta = 0
                notes.append(SimpleMidiNote.load_from_midi_message(msg.copy(time=delta)))
        return list(filter(lambda x: x is not None, notes))

    @classmethod
    def __load_tempo(cls, midifile: MidiFile):
        for msg in midifile:
            if isinstance(msg, MetaMessage):
                if msg.dict().get("tempo") is not None:
                    return msg.dict().get("tempo")
        return 500000

    def __calculate_absolute_time(self):
        now = 0
        for note in self._notes:
            now += note.offset_time
            note.real_time = now


# mid = MidiFile('rskl.mid', clip=True)
# simplemid = SimpleMidiFile.load_from_midi_file("test", mid, track_index=1)
# for n in simplemid.notes:
#     print(n)
    # a = print(n) if n.operation == SimpleMidiNoteOperation.ON else 0

# print(len(mid.tracks))
# print(mid.ticks_per_beat)
# for i, track in enumerate(mid.tracks):
#     print('Track {}: {}'.format(i, track.name))
#     print(len(track))
#     for msg in track:
#         msg:Message
#         print(mid.ticks_per_beat)
#         print(type(msg),msg,msg.dict())
#
# print("===========")
# print(mid.length)
# for msg in mid:
#     print(type(msg),msg,msg.dict())
