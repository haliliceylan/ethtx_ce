#  Copyright 2021 DAI Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

from ethtx import EthTx, EthTxConfig
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from cache import remember
from ethtx_ce import frontend, api
from ethtxcache import EthTxC

app = Flask(__name__)

ethtx_config = EthTxConfig(
    mongo_connection_string=os.getenv("MONGO_CONNECTION_STRING",os.getenv("MONGO_URL")),
    etherscan_api_key=os.getenv("ETHERSCAN_KEY"),
    web3nodes={
        "mainnet": dict(hook=os.getenv("MAINNET_NODE_URL", ""), poa=True),
        "tesnet": dict(hook=os.getenv("TESTNET_NODE_URL", ""), poa=True),
    },
    default_chain="mainnet",
    etherscan_urls={
        "mainnet": "https://api.bscscan.com/api",
        "testnet": "https://api-testnet.bscscan.com/api",
    },
)

class EthTxCache(EthTxC):
    def decode_transaction_cache(self, chain_id, tx_hash):
        return remember(f"transaction{chain_id}{tx_hash}", lambda: self.decoders.decode_transaction(chain_id=chain_id, tx_hash=tx_hash))

ethtx = EthTxCache.initialize(ethtx_config,EthTxCache)


app.wsgi_app = DispatcherMiddleware(
    frontend.create_app(engine=ethtx, settings_override=EthTxConfig),
    {"/api": api.create_app(engine=ethtx, settings_override=EthTxConfig)},
)

if __name__ == "__main__":
    app.run()
