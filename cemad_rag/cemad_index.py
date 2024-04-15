from regulations_rag.standard_regulation_index import StandardRegulationIndex, load_index_data_from_files
from regulations_rag.regulation_reader import  load_regulation_data_from_files

from cemad_rag.cemad_reference_checker import CEMADReferenceChecker
from cemad_rag.cemad_reader import CEMADReader

class CEMADIndex(StandardRegulationIndex):

    def __init__(self, decryption_key):
        cemad_reference_checker = CEMADReferenceChecker()
        
        user_type = "an Authorised Dealer (AD)" 
        #regulation_name = "\'Currency and Exchange Manual for Authorised Dealers\' (Manual or CEMAD)"
        regulation_name = "South African Exchange Control Manual"


        path_to_manual_as_csv_file = "./inputs/ad_manual.csv"
        path_to_definitions_as_parquet_file = "./inputs/ad_definitions.parquet"
        path_to_index_as_parquet_file = "./inputs/ad_index.parquet"
        path_to_additional_manual_as_csv_file = "./inputs/ad_manual_plus.csv"
        path_to_additional_definitions_as_parquet_file = "./inputs/ad_definitions_plus.parquet"
        path_to_additional_index_as_parquet_file = "./inputs/ad_index_plus.parquet"
        path_to_workflow_as_parquet = "./inputs/workflow.parquet"

        # decryption_key = os.getenv('excon_encryption_key')
        df_definitions, df_index, df_workflow = load_index_data_from_files(path_to_definitions_as_parquet_file, 
                                                                           path_to_additional_definitions_as_parquet_file, 
                                                                           path_to_index_as_parquet_file, 
                                                                           path_to_additional_index_as_parquet_file, 
                                                                           path_to_workflow_as_parquet, 
                                                                           decryption_key=decryption_key)

        df_regulations = load_regulation_data_from_files(path_to_manual_as_csv_file, 
                                                         path_to_additional_manual_as_csv_file)

        reference_checker = CEMADReferenceChecker()
        reader = CEMADReader()

        super().__init__(user_type = user_type, 
                         regulation_name = regulation_name, 
                         regulation_reader = reader,
                         df_definitions = df_definitions, 
                         df_index = df_index, 
                         df_workflow = df_workflow)

