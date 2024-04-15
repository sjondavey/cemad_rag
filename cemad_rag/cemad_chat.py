
from regulations_rag.regulation_index import EmbeddingParameters
from regulations_rag.regulation_chat import RegulationChat, ChatParameters
from regulations_rag.rerank import RerankAlgos

from cemad_rag.cemad_reference_checker import CEMADReferenceChecker
from cemad_rag.cemad_index import CEMADIndex
from cemad_rag.cemad_reader import CEMADReader

class CEMADChat(RegulationChat):
    def __init__(self, openai_client, decryption_key, rerank_algo = RerankAlgos.LLM, user_name_for_logging = 'test_user'):
        chat_parameters = ChatParameters(chat_model = "gpt-4-0125-preview", temperature = 0, max_tokens = 500)
        #model_to_use = "gpt-3.5-turbo"
        #model_to_use = "gpt-4-1106-preview"
        #model_to_use="gpt-3.5-turbo-16k"

        embedding_parameters = EmbeddingParameters("text-embedding-3-large", 1024)

        index = CEMADIndex(decryption_key)
        reader = CEMADReader()

        
        reference_checker = CEMADReferenceChecker()



        #rerank_algo = RerankAlgos.MOST_COMMON
        if rerank_algo == RerankAlgos.LLM:
            rerank_algo.params["openai_client"] = openai_client
            rerank_algo.params["model_to_use"] = chat_parameters.model


        super().__init__(openai_client = openai_client, 
                          embedding_parameters = embedding_parameters, 
                          chat_parameters = chat_parameters, 
                          regulation_reader = reader, 
                          regulation_index = index,
                          rerank_algo = rerank_algo,   
                          user_name_for_logging = 'test_user')
        