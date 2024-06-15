import sys
import os
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
     QApplication,                        
     QDialog, 
     QWidget,
     QVBoxLayout, 
     QHBoxLayout, 
     QLabel, 
     QLineEdit, 
     QTextEdit, 
     QComboBox, 
     QPushButton
     )
from PyQt5.QtGui import (
     QFont, 
     QFontDatabase, 
     QIcon
     )
from history import History, Conversation

MMI_Version = "MMI v0.12"
MMI_Icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
sysprompt = """You are a diligent, productive, very sharp programmer. You love explaining your code and mentoring others. You don't hesitate to say "I don't know." You are well-liked by your peers, and shine in teams, because your code is generally simple, easy to read, and understand."""
max_tokens = 4096


class InputDialog(QDialog):
    """
    QDialog window to select conversation and input a prompt.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        context = History()
        conv_list = context.list_conversations()
        model_list = [
            'Mixtral 8x7B', 
            # https://platform.openai.com/docs/models
            'GPT-3.5-Turbo', 
            'GPT-4-Turbo', 
            'GPT-4o', 
            # https://docs.anthropic.com/claude/docs/models-overview
            'claude-3-haiku-20240307',
            'Claude-3-Sonnet-20240229', 
            'Claude-3-Opus-20240229', 
            'claude-2.1', 
            'claude-2.0', 
            'claude-instant-1.2'
        ]
        self.conv_id        = None
        self.user_prompt    = None
        self.system_prompt  = None
        self.max_new_tokens = None
        self.setWindowTitle(MMI_Version)
        self.setWindowIcon(QIcon(MMI_Icon))

        # TODO:
        #    - set to default system fonts
        #    - keep size maybe
        #    - check out how to zoom in/out
        font = QFont("SauceCodePro Nerd Font", pointSize=13, weight=QFont.Normal)
        font2 = QFont("Source Sans Pro", pointSize=14, weight=QFont.Normal)

        # setup elements
        # TODO: move all aesthetics in their own category (functionalize them)

        # Select conversation
        self.conv_select = QComboBox(self)
        self.conv_select.addItems(conv_list)
        self.model_select = QComboBox(self)
        self.model_select.addItems(model_list)
        
        # New conversation
        self.conv_new = QLineEdit(self)

        # System prompt
        self.sysprompt_label = QLabel("🡇 System Prompt")
        self.sysprompt_edit = QTextEdit(self)
        self.sysprompt_edit.setAcceptRichText(False)

        # User prompt
        self.prompt_label = QLabel("🡇 New message:")
        self.prompt_edit = QTextEdit(self)
        self.prompt_edit.setAcceptRichText(False)

        # Max new tokens
        self.tokens_label = QLabel("Max new tokens:")
        self.tokens_edit = QLineEdit(self)

        # Button: Generate
        self.generate_btn = QPushButton("Let's gen!", self)

        # TODO: functionalize layout
        #       which we can call with proper args to set everything up

        # Font and size settings
        font_metrics = QApplication.fontMetrics()
        line_height = font_metrics.lineSpacing()
        
        self.sysprompt_edit.setMinimumHeight(
            int(line_height * 1.3 + 2 * self.sysprompt_edit.frameWidth())
        )
        self.sysprompt_edit.setMaximumHeight(
            int(line_height * 12.52 + 2 * self.sysprompt_edit.frameWidth())
        )
        self.sysprompt_label.setFont(font2)
        self.sysprompt_edit.setFont(font)
        self.prompt_label.setFont(font2)
        self.prompt_edit.setFont(font)
        self.tokens_edit.setFont(font)


        # Layouts
        layout_main = QVBoxLayout(self)

        conv_layout = QHBoxLayout()
        conv_layout.addWidget(self.conv_select)
        conv_layout.addWidget(self.conv_new)

        prompt_layout = QVBoxLayout()
        prompt_layout.addWidget(self.sysprompt_label)
        prompt_layout.addWidget(self.sysprompt_edit)
        prompt_layout.addWidget(self.prompt_label)
        prompt_layout.addWidget(self.prompt_edit)

        token_layout = QHBoxLayout()
        token_layout.addWidget(self.tokens_label)
        token_layout.addWidget(self.tokens_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.model_select)
        btn_layout.addWidget(self.generate_btn)

        # Main layout assembly
        layout_main.addLayout(conv_layout)
        layout_main.addLayout(prompt_layout)
        layout_main.addLayout(token_layout)
        layout_main.addLayout(btn_layout)

        # Assemble layout and connect signals to slots (e.g., button clicks to methods)
        self.setLayout(layout_main)
        self.generate_btn.clicked.connect(self.collect_inputs)
        self.generate_btn.clicked.connect(self.accept)

        # Live refresh
        self.conv_select.currentIndexChanged.connect(self.refresh_sysprompt)
        self.conv_select.currentIndexChanged.connect(self.refresh_conv_name)

        # Defaults
        self.refresh_sysprompt()
        self.refresh_conv_name()
        # clipboard = QApplication.clipboard()
        clipboard_text = QApplication.clipboard().text()
        self.prompt_edit.setText(clipboard_text)
        self.tokens_edit.setText(str(max_tokens))

        self.resize(720, 480)


    def refresh_conv_name(self):
        self.conv_new.setText(self.conv_select.currentText())
        return


    def refresh_sysprompt(self):
        # Logic to load and display the "System Prompt" for the selected conversation
        conv_id = self.conv_select.currentText()
        # Load the first message of the conversation
        conv = Conversation(conv_id)
        # setText to system_prompt_edit
        self.sysprompt_edit.setText(conv.get_sysprompt())
        return


    def set_conv_sysprompt(self, conv_id: str, sysprompt: str = sysprompt) -> None:
        conv = Conversation(conv_id)
        conv.set_sysprompt(sysprompt)
        return


    def collect_inputs(self):
        """
        Method to collect inputs and store them in 
        `self.conv_id`
        `self.user_prompt`
        `self.system_prompt`
        `self.max_new_tokens`
        """

        if self.conv_new.text() != "": # new conversation
            self.conv_id: str = self.conv_new.text()
        else: # existing conversation
            self.conv_id: str = self.conv_select.currentText()

        self.system_prompt: str = str(self.sysprompt_edit.toPlainText())
        self.user_prompt:   str = str(self.prompt_edit.toPlainText())
        self.model:         str = str(self.model_select.currentText())

        tokens: str = self.tokens_edit.text()
        self.max_new_tokens: int = int(tokens) if tokens else 1
        
        self.close()
        # print(f"self.conv_id: {self.conv_id}")
        return (self.conv_id.strip(),
                self.system_prompt.strip(),
                self.user_prompt.strip(),
                self.max_new_tokens,
                self.model.strip().lower())
