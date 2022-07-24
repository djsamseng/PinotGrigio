from pocketsphinx import LiveSpeech

import robot_managers

def main():
    motor_manager = robot_managers.MotorManager()
    speech = LiveSpeech(lm=False, kws='keywords.list', dic='keywords.dic')
    amt = 600
    adiff = 250
    for phrase in speech:
        for segment in phrase.segments():
            w = segment.strip(' ')
            print('-{0}-'.format(w))
            if w == "RIGHT":
                val = amt+adiff
                motor_manager.set_motors(val, -val)
            elif w == "LEFT":
                val = amt + adiff
                motor_manager.set_motors(-val, val)
            elif w == "FORWARD":
                motor_manager.set_motors(amt, amt)
            elif w == "BACK":
                motor_manager.set_motors(-amt, -amt)
            elif w == "STOP":
                motor_manager.set_motors(0, 0)
                break


if __name__ == "__main__":
    main()
