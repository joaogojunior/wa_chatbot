import time

from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# bugfix PyYaml 3.12
import collections.abc

collections.Hashable = collections.abc.Hashable

# bugfix pytz
time.clock = time.perf_counter


class ChatBotBr:

    def __init__(self, nome_bot, train=False):
        self.bot = ChatBot(nome_bot,
                           # logic_adapters=[
                           #     {
                           #         'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                           #         'input_text': 'fazer pedido',
                           #         'output_text': 'Para realizar seu pedido acesse https://whatsmenu.com.br/akisushibar e informe'
                           #                        ' endereço,\n'
                           #                        'bairro, ponto de referência, apartamento e andar se houver mais a forma de pagamento.\n'
                           #                        'Se o pagamento for por pix, favor enviar o comprovante!'
                           #                        ' \0xF0\0x9F\0x98\0x89\0xF0\0x9F\0x98\0x8A\0xF0\0x9F\0x8D\0xA3\n'
                           #     },
                           #     {
                           #         'import_path': 'chatterbot.logic.SpecificResponseAdapter',
                           #         'input_text': 'me ajude',
                           #         'output_text': 'Para realizar seu pedido acesse https://whatsmenu.com.br/akisushibar e informe'
                           #                        ' endereço,\n'
                           #                        'bairro, ponto de referência, apartamento e andar se houver mais a forma de pagamento.\n'
                           #                        'Se o pagamento for por pix, favor enviar o comprovante!'
                           #                        ' \0xF0\0x9F\0x98\0x89\0xF0\0x9F\0x98\0x8A\0xF0\0x9F\0x8D\0xA3\n'
                           #     },
                           #     {
                           #         'import_path': 'chatterbot.logic.BestMatch',
                           #         'default_response': 'Não consegui te entender bem... por favor, tente explicar melhor o que deseja ou\n'
                           #                             'digite me ajude para mais instruções.',
                           #         'maximum_similarity_threshold': 0.80
                           #     }
                           # ]
                           )
        self.list_trainer = ListTrainer(self.bot)
        trainer = ChatterBotCorpusTrainer(self.bot)

        if train:
            print("Treinando modelo...")
            trainer.train(
                "./corpus"
            )

            # if os.path.isdir(nome_pasta):
            #     for treino in os.listdir(nome_pasta):
            #         conversas = open(nome_pasta + '/' + treino, 'r', encoding="utf-8").readlines()
            #         self.list_trainer.train(conversas)

    def responde(self, texto):
        # parse new lines and 4bytes utf8 encoded chars
        return str(self.bot.get_response(texto))
