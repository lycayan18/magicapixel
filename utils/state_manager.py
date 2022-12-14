# StateManager manages application's state and allows application to cancel last
# action and recover cancelled action

class StateManager:
    def __init__(self):
        self.states = list()
        self.current_state_index = -1

    def push_state(self, state):
        # "Hard" delete all "soft" deleted states
        if self.current_state_index < len(self.states) - 1:
            self.states = self.states[:self.current_state_index + 1]

        self.states.append(state)
        self.current_state_index += 1

    def pop_state(self):
        if self.current_state_index <= 0:
            self.current_state_index = -1
            return None

        # Do "soft" deletion of state to have ability recover it
        self.current_state_index -= 1

        return self.states[self.current_state_index]

    def recover_last_state(self):
        if self.current_state_index >= len(self.states) - 1:
            return None

        # Recover "soft" deleted state
        self.current_state_index += 1

        # If all states are "soft" deleted and we're in starting point now, then automatically move to
        # second state. If you won't do that, you have to recover last state two times to go to first
        # state change.
        if self.current_state_index == 0 and len(self.states) > 1:
            self.current_state_index = 1

        return self.states[self.current_state_index]
