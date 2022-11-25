from ahk import AHK
from mido import MidiFile

from SimpleMidi import SimpleMidiFile, SimpleMidiNoteOperation

Note_Key_Map = {
    # C5
    72: "q",
    73: "q",
    74: "w",
    75: "w",
    76: "e",
    77: "r",
    78: "r",
    79: "t",
    80: "t",
    81: "y",
    82: "y",
    83: "u",

    # C4
    60: "a",
    61: "a",
    62: "s",
    63: "s",
    64: "d",
    65: "f",
    66: "f",
    67: "g",
    68: "g",
    69: "h",
    70: "h",
    71: "j",

    # C3
    48: "z",
    49: "z",
    50: "x",
    51: "x",
    52: "c",
    53: "v",
    54: "v",
    55: "b",
    56: "b",
    57: "n",
    58: "n",
    59: "m",
}


class AHK_Templates:
    KEY_DOWN = "Send {{{} down}}"
    KEY_UP = "Send {{{} up}}"

    KEY = "Send {{Blind}}{}"

    SLEEP = "Sleep {}"

def clear_delay(scripts):
    return ["SetKeyDelay, -1, -1, Play"]+scripts

def convert_midi_to_scripts(midi: SimpleMidiFile):
    pre_scripts_1 = []
    pre_scripts_2 = []
    scripts = []
    for note in midi.notes:
        if Note_Key_Map.get(note.note) is not None:
            key = Note_Key_Map.get(note.note)
            if note.operation == SimpleMidiNoteOperation.ON:
                pre_scripts_1.append(["send", "{{{}}}".format(key)])
        if note.offset_time == 0:
            continue
        pre_scripts_1.append(["sleep", round(note.offset_time * 1000)])
    if len(pre_scripts_1) == 0:
        return []
    pre_scripts_2.append(pre_scripts_1[0])

    for s in pre_scripts_1[1::]:
        if s[0] == "send" and pre_scripts_2[-1][0] == "send":
            pre_scripts_2[-1][1] = pre_scripts_2[-1][1]+s[1]
        elif s[0] == "sleep" and pre_scripts_2[-1][0] == "sleep":
            pre_scripts_2[-1][1] = pre_scripts_2[-1][1]+s[1]
        else:
            pre_scripts_2.append(s)

    for s in pre_scripts_2:
        if s[0] == "send":
            scripts.append(AHK_Templates.KEY.format(s[1]))
        if s[0] == "sleep":
            scripts.append(AHK_Templates.SLEEP.format(s[1]))
    return scripts


ahk = AHK()
mid = MidiFile('midi/Flower Dance.mid', clip=True)
simplemid = SimpleMidiFile.load_from_midi_file("test", mid).get_copy(note_offset=-11)
notesss = [note.note for note in simplemid.notes]
print(min(notesss), max(notesss))
s = clear_delay(convert_midi_to_scripts(simplemid))
with open("test.ahk", "w", encoding="utf-8") as f:
    f.write("\n".join(s))
# # print("\n".join(s))
print(len(simplemid.notes))
print(len(s))
import time
# time.sleep(4)
# ahk.run_script("\n".join(s))
