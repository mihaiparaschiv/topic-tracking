from topic_tracking.processing.context import ProcessingContext
from topic_tracking.util.command import Command
import nltk


class ParsingCommand(Command):

    def execute(self, context):
        content = context[ProcessingContext.EXTRACTED_CONTENT]

        sentences = nltk.sent_tokenize(content)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]

        context[ProcessingContext.TAGGED_SENTENCES] = sentences
