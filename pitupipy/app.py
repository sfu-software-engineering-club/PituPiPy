import utils
from pynput import keyboard
from client.client import Client
from tracker.tracker import Tracker


if __name__ == "__main__":
    chosen = False
    selection = 0

    """
    client = Client()
    client.listen(port)
    """
    """
    tracker = Tracker(port)

    tracker.start()
    """

    def on_release(key):
        global chosen
        global selection
        if key == keyboard.Key.down or key == keyboard.Key.up:
            selection = 1 if selection == 0 else 0
            return False
        if key == keyboard.Key.enter:
            chosen = True
            return False

    while True:
        utils.clear_window()
        utils.draw_line()
        utils.draw_center_text("PituPiPy")
        utils.draw_center_text("Chat and File Transfer in P2P network")
        utils.draw_line()
        if selection == 0:
            utils.draw_center_text("▶  " + "Host a Network.".ljust(16))
            utils.draw_center_text("▷  " + "Join a Network.".ljust(16))
        elif selection == 1:
            utils.draw_center_text("▷  " + "Host a Network.".ljust(16))
            utils.draw_center_text("▶  " + "Join a Network.".ljust(16))
        utils.draw_line()
        utils.draw_center_text("By SFU SDC")
        with keyboard.Listener(
            on_press=lambda k: None, on_release=on_release
        ) as listener:
            listener.join()

        if chosen:
            if selection == 0:
                input()
                try:
                    port = int(input("Tracker Port >> "))
                except:
                    chosen = False
                    continue
                utils.clear_window()
                tracker = Tracker(port)
                tracker.start()
                break
            elif selection == 1:
                input()
                try:
                    port = int(input("Client Port >> "))
                except Exception as e:
                    chosen = False
                    continue
                utils.clear_window()
                client = Client()
                client.listen(port)
                break
