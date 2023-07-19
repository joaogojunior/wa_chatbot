import os
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# bugfix PyYaml 3.12
import collections.abc
collections.Hashable = collections.abc.Hashable


class ChatBotBr:

    def __init__(self, nome_bot, nome_pasta='chats'):
        self.bot = ChatBot(nome_bot)
        self.list_trainer = ListTrainer(self.bot)
        trainer = ChatterBotCorpusTrainer(self.bot)
        trainer.train(
            "./corpus"
        )

        if os.path.isdir(nome_pasta):
            for treino in os.listdir(nome_pasta):
                conversas = open(nome_pasta + '/' + treino, 'r', encoding="utf-8").readlines()
                self.list_trainer.train(conversas)

    def responde(self, texto):
        return self.bot.get_response(texto)
