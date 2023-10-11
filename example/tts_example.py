from robot_hat import TTS


if __name__ == "__main__":
    try:


        words = ["Hello", "Hi", "Good bye", "Nice to meet you"]
        tts_robot = TTS()
        for i in words:
            print(i)
            tts_robot.say(i)

    except Exception as e:
        print("Error: ", e)
