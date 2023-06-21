from llama_index.indices.composability import ComposableGraph
from llama_index import ListIndex


class IndexGraph:
    __instance = None

    @staticmethod
    def instance():
        """ Static access method. """
        if IndexGraph.__instance == None:
            IndexGraph()
        return IndexGraph.__instance

    def __init__(self, index_set, index_summaries, service_context, storage_context):
        """ Virtually private constructor. """
        if IndexGraph.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            IndexGraph.__instance = self
            self.graph = ComposableGraph.from_indices(
                ListIndex,
                index_set,
                index_summaries=index_summaries,
                service_context=service_context,
                storage_context=storage_context,
            )
