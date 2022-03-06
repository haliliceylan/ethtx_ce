
from typing import Dict

from mongoengine import connect
from pymongo import MongoClient
from ethtx import EthTx, EthTxConfig
from ethtx.decoders.abi.decoder import ABIDecoder
from ethtx.decoders.decoder_service import DecoderService
from ethtx.decoders.semantic.decoder import SemanticDecoder
from ethtx.models.decoded_model import Proxy, DecodedTransaction
from ethtx.models.objects_model import Call
from ethtx.providers import EtherscanProvider, Web3Provider, ENSProvider
from ethtx.providers.semantic_providers import (
    ISemanticsDatabase,
    SemanticsRepository,
    MongoSemanticsDatabase,
)
from ethtx.utils.validators import assert_tx_hash

class EthTxC(EthTx):

    @staticmethod
    def initialize(config: EthTxConfig, c):
        mongo_client: MongoClient = connect(host=config.mongo_connection_string)
        repository = MongoSemanticsDatabase(db=mongo_client.get_database())

        web3provider = Web3Provider(
            nodes=config.web3nodes, default_chain=config.default_chain
        )
        etherscan_provider = EtherscanProvider(
            api_key=config.etherscan_api_key,
            nodes=config.etherscan_urls,
            default_chain_id=config.default_chain,
        )

        ens_provider = ENSProvider

        return c(
            config.default_chain,
            repository,
            web3provider,
            etherscan_provider,
            ens_provider,
        )