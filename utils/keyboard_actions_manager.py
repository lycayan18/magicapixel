from typing import Callable

# Key code to key name decoding
KEY_TRANSCRIPT = {
    81: "q",
    87: "w",
    69: "e",
    82: "r",
    84: "t",
    89: "y",
    85: "u",
    73: "i",
    79: "o",
    80: "p",
    65: "a",
    83: "s",
    68: "d",
    70: "f",
    71: "g",
    72: "h",
    74: "j",
    75: "k",
    76: "l",
    90: "z",
    88: "x",
    67: "c",
    86: "v",
    66: "b",
    78: "n",
    77: "m"
}

SPECIAL_KEY_TRANSCRIPT = {
    32: "shift",
    33: "ctrl",
    35: "alt",
    48: "f1",
    49: "f2",
    50: "f3",
    51: "f4",
    52: "f5",
    53: "f6",
    54: "f7",
    55: "f8",
    56: "f9",
    57: "f10",
    58: "f11",
    59: "f12"
}


class KeyboardActionsManager:
    def __init__(self):
        self.subscribers = dict()
        self.keys = [False for _ in range(255)]
        self.special_keys = [False for _ in range(255)]

    def subscribe(self, combination: str, callback: Callable):
        lowercase_combination = combination.lower()

        if lowercase_combination not in self.subscribers:
            self.subscribers[lowercase_combination] = []

        self.subscribers[lowercase_combination].append(callback)

    def keypress_event(self, key: int):
        self.set_key(key, True)
        self.check_for_combinations()

    def keyrelease_event(self, key: int):
        self.set_key(key, False)

    def set_key(self, key: int, value: bool):
        if key < 255:
            self.keys[key] = value

        if key >= 16777216 and key < 16777471:
            self.special_keys[key - 16777216] = value

    def check_for_combinations(self):
        combination = list()

        special_keys = list(
            filter(lambda x: x[1], enumerate(self.special_keys)))
        keys = list(filter(lambda x: x[1], enumerate(self.keys)))

        for index, key in special_keys:
            if index in SPECIAL_KEY_TRANSCRIPT:
                combination.append(SPECIAL_KEY_TRANSCRIPT[index])

        for index, key in keys:
            if index in KEY_TRANSCRIPT:
                combination.append(KEY_TRANSCRIPT[index])

        string_combination = '+'.join(combination)

        if string_combination in self.subscribers:
            for callback in self.subscribers[string_combination]:
                callback()
