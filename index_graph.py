from llama_index.indices.composability import ComposableGraph
from llama_index import GPTSimpleKeywordTableIndex


class IndexGraph:
    __instance = None

    @staticmethod
    def instance():
        """ Static access method. """
        if IndexGraph.__instance == None:
            IndexGraph()
        return IndexGraph.__instance

    def __init__(self, index_set, index_summaries):
        """ Virtually private constructor. """
        if IndexGraph.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            IndexGraph.__instance = self
            self.graph = ComposableGraph.from_indices(
                GPTSimpleKeywordTableIndex,
                index_set,
                index_summaries=index_summaries,
                max_keywords_per_chunk=50
            )
