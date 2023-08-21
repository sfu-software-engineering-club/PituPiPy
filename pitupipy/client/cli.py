import os
import uuid


class CLI:
    def __init__(self):
        self.message_chunk_file_name = "message-" + str(uuid.uuid4())
        self.message_chunk_location = os.path.join(
            os.getcwd(), f"{self.message_chunk_file_name}.txt"
        )

        # CLI Update Flag
        self.wait_for_input = False

        # CLI Elements
        self.header_texts = []
        self.body_texts = []
        self.network_status_text = ""
        self.command_info = ""
        self.command_prompt = ""
        self.reset_command_prompt()

        # CLI Properties
        self.MAX_BODY_LENGTH = 5

    """
    CLI Methods
    """

    def input(self):
        self.wait_for_input = True
        self.cli_render()
        cmd = input()
        self.command_info = ""
        self.wait_for_input = False
        return cmd

    def add_header_text(self, header_text):
        assert isinstance(header_text, str)
        self.header_texts.append(header_text)
        if self.wait_for_input:
            self.cli_render()

    def add_body_text(self, body_text):
        assert isinstance(body_text, str)
        self.body_texts.append(body_text)
        if self.wait_for_input:
            self.cli_render()

    def set_network_status_text(self, network_status_text):
        assert isinstance(network_status_text, str)
        self.network_status_text = network_status_text
        if self.wait_for_input:
            self.cli_render()

    def set_command_info(self, command_info):
        assert isinstance(command_info, str)
        self.command_info = command_info
        if self.wait_for_input:
            self.cli_render()

    def set_command_prompt(self, command_prompt):
        assert isinstance(command_prompt, str)
        self.command_prompt = command_prompt
        if self.wait_for_input:
            self.cli_render()

    def reset_command_prompt(self):
        self.command_prompt = "COMMAND? [/q or /help] >> /"
        if self.wait_for_input:
            self.cli_render()

    """
    CLI Rendering
    """

    def cli_render(self):
        os.system("cls" if os.name == "nt" else "clear")
        rows, columns = os.popen("stty size", "r").read().split()

        draw_border = lambda: print(("{0:─^" + columns + "}").format(""))
        draw_empty_line = lambda: print(
            "│" + ("{0:^" + str(int(columns) - 2) + "}").format("") + "│"
        )
        draw_text = lambda text: print(
            "│"
            + text
            + ("{0:^" + str(int(columns) - 2 - len(text)) + "}").format("")
            + "│"
        )
        draw_text_center = lambda text: print(
            "│" + ("{0:^" + str(int(columns) - 2) + "}").format(text) + "│"
        )

        # CLI Header
        draw_border()
        for h in self.header_texts:
            draw_text_center(h)
        # CLI Body
        draw_border()
        draw_text(self.network_status_text)
        draw_border()
        if len(self.body_texts) < self.MAX_BODY_LENGTH:
            for p in self.body_texts:
                draw_text(p)
        else:
            for p in self.body_texts[
                len(self.body_texts) - self.MAX_BODY_LENGTH : len(self.body_texts)
            ]:
                draw_text(p)
        draw_empty_line()
        # CLI Input
        draw_border()
        if self.command_info != "":
            print(self.command_info)
        print(self.command_prompt, end="")
