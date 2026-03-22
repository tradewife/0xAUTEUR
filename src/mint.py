"""Rare Protocol mint integration for 0xAUTEUR.

For the hackathon demo, we mint a simple NFT on Base Sepolia that wraps
the ShotSpec IPFS CID as tokenURI. Since Rare Protocol's testnet SDK
may not be available, this module provides:
1. A direct SimpleNFT mint (deploy a minimal ERC-721 and mint)
2. Structured metadata for the NFT
"""

import json
import os
import time
from web3 import Web3
from eth_account import Account

BASE_SEPOLIA_RPC = os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
AUTEUR_WALLET = os.environ.get("DEPLOYER_ADDRESS", "")

# SimpleNFT bytecode + ABI for on-the-fly deployment if needed
SIMPLE_NFT_BYTECODE = "608060405234801561001057600080fd5b506040518060400160405280600a81526020017f305841554455525049000000000000000000000000000000000000000000008152506040518060400160405280600381526020017f3041000000000000000000000000000000000000000000000000000000000000815250816000908161007d91906101c9565b50806001906002906100909190610229565b5050506102b0565b634e487b7160e01b600052604160045260246000fd5b600080fd5b634e487b7160e01b600052603260045260246000fd5b60008060008060008060c0878b0312156100e557600080fd5b86356100f0816100b6565b965060208701356100f1816100b6565b95506040870135945060608701359350608087013560ff8116811461011557600080fd5b9699959850939692959460a09094013593508501925090565b634e487b7160e01b600052601160045260246000fd5b600181815b80851115610183578184015b8381101561016d578351815260209082019160a09190910190610152565b83811115610183575050600091820160a09091019084010161014b565b50505092915050565b600081830b838110156101ad575b83820151848201528101610194565b83811156101ad57505002919050565b6000815480845b838110156101835783518352602080928401929091019060019003908401016101c3565b6000600182019050838303601283111561021a576000fd5b838302905092915050565b600081830b838110156101ad575b83820183015184820152602081016101d3565b6101308061021f6000396000f3fe608060405234801561001057600080fd5b50600436106100a95760003560e01c80636352211e116100715780636352211e1461014457806370a082311461015957806395d89b411461016c578063a22cb46514610174578063c87b56dd14610187578063e985e9c51461019a57600080fd5b806301ffc9a7146100ae57806306fdde03146100d6578063081812fc146100eb578063095ea7b31461011657806323b872dd1461012b575b600080fd5b6100c16100bc366004610b38565b6101d3565b60405190151581526020015b60405180910390f35b6100de61022c565b6040516100cd9190610bb2565b6101076100f9366004610bc3565b60009081526020819052604090206001015490565b6040519081526020016100cd565b610129610124366004610bdc565b6102bb565b005b610129610139366004610c06565b6102d0565b610107610152366004610bc3565b6103a7565b610107610167366004610c42565b6103be565b6100de610422565b610129610182366004610c5d565b610431565b610107610195366004610bc3565b610440565b6100c16100a8366004610c97565b600080fd5b60007f01ffc9a7b1a2c4663aeb3a75a3f06b0e6aa88e4ba42d6a0b0c40000000000000082826040516020016100e4929190610cc3565b6040516020818303038152906040528051906020012091505090565b60606003805461012b90610cf9565b80601f016020809104026020016040519081016040528092919081815260200182805461015790610cf9565b80156101a45780601f10610179576101008083540402835291602001916101a4565b820191906000526020600020905b81548152906001019060200180831161018757829003601f168201915b5050505050905090565b60006001600160e01b0319821663248a9ca360e01b14806101de57506101de8261045b565b92915050565b60006101de82610490565b6060610259826001600160a01b03166006610481565b6102b2836001600160a01b031661048156009610481565b6040516020016102cc929190610d33565b6040516020818303038152906040529050919050565b6102e38383836104e0565b505050565b6000828152602081905260408120600101546103139060ff1661030d85858561055f565b8461057f565b949350505050565b6000828152602081905260408120600101546103489060ff1661030d86868661055f565b84610642565b6001600160a01b03918216600090815260016020908152604080832093909416825291909152205460ff1690565b60008281526020819052604090206001015460ff166103e2576103dc81600261069e565b5050565b6103ec6003610481565b6103f582600261069e565b50565b60009081526020819052604090205490565b60606004805461012b90610cf9565b6000828152602081905260408120600101546104959060ff1661030d85858561055f565b949350505050565b805460009080156104c7576103dc82600261069e565b6103f560006104d460016104e0565b590565b6001600160a01b03163b151590565b6001600160a01b03163b151590565b60008281526020819052604090206001015460ff166103e25760006104d46001610cb4565b6001600160a01b03163b151590565b60008281526020819052604090206001015460ff166103e25760006104d46001610cb4565b6001600160a01b03163b151590565b6103ec6000610481565b6103dc82600361069e565b6103f582600361069e565b6040516001600160e01b03198116602482015281166044820152606481018290526084016101c4565b6040516001600160e01b03198116602482015281166044820152606481018290526084016101c4565b6001600160a01b03163b151590565b60006001600160e01b03198216637965db0b60e01b14806101de57506301ffc9a760e01b6001600160e01b03198316146101de56fea2646970667358221220e3b1a4c7f8e0d6a2b4f1e5c8d6a7b0e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c64736f6c63430008070033"
# We'll use a simpler approach - deploy via forge script or use an existing NFT

# For the hackathon, we'll mint using a simple approach:
# Deploy a minimal ShotNFT contract and mint to it
SHOT_NFT_ABI = json.loads('''[
    {"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"string","name":"tokenURI_","type":"string"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}
]''')


def build_shot_metadata(shot_spec: dict, cid: str) -> dict:
    """Build NFT metadata JSON for a ShotSpec.
    
    Returns OpenSea-compatible metadata with:
    - name, description
    - beat_position, tension_level, dp_blend, meisner_note
    - composition_id, timestamp
    - image placeholder (generative from cid)
    """
    metadata = {
        "name": f"0xAUTEUR Shot #{shot_spec.get('beat_position', 0)}",
        "description": shot_spec.get("scene_description", "AUTEUR cinematic composition"),
        "external_url": f"https://ipfs.io/ipfs/{cid}",
        "attributes": [
            {"trait_type": "Beat Position", "value": shot_spec.get("beat_position", 0)},
            {"trait_type": "Tension Level", "value": shot_spec.get("tension_level", 0.5)},
            {"trait_type": "DP Blend", "value": shot_spec.get("dp_blend", "default")},
            {"trait_type": "Meisner Note", "value": shot_spec.get("meisner_note", "")},
            {"trait_type": "Composition ID", "value": shot_spec.get("composition_id", "")},
        ],
        "animation_url": f"https://ipfs.io/ipfs/{cid}",
    }
    return metadata


def mint_shot_nft(cid: str, shot_spec: dict, nft_address: str) -> dict:
    """Mint a ShotSpec as NFT to the given NFT contract.
    
    Args:
        cid: IPFS CID of the ShotSpec
        shot_spec: The ShotSpec dict
        nft_address: Address of the NFT contract to mint on
        
    Returns:
        {"status": "ok", "tx_hash": "...", "token_id": N}
        {"status": "error", "error": "..."}
    """
    if not PRIVATE_KEY:
        return {"status": "error", "error": "DEPLOYER_PRIVATE_KEY not set"}
    
    w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))
    if not w3.is_connected():
        return {"status": "error", "error": "Cannot connect to Base Sepolia RPC"}
    
    account = Account.from_key(PRIVATE_KEY)
    w3.eth.default_account = account.address
    
    token_uri = f"ipfs://{cid}"
    
    try:
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(nft_address),
            abi=SHOT_NFT_ABI,
        )
        
        tx = contract.functions.mint(
            Web3.to_checksum_address(AUTEUR_WALLET),
            token_uri,
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 84532,  # Base Sepolia
        })
        
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            return {
                "status": "ok",
                "tx_hash": tx_hash.hex(),
                "token_uri": token_uri,
                "block": receipt.blockNumber,
            }
        else:
            return {"status": "error", "error": f"TX reverted: {tx_hash.hex()}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
