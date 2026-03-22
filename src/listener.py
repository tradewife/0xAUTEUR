"""Bid-responsive recomposition listener for 0xAUTEUR.

Listens for bid events on the NFT contract and adjusts
tension_level in the next ShotSpec based on bid dynamics:
- bid > 2x reserve: tension_level += 0.15 (more climactic)
- bid < reserve: tension_level -= 0.10 (more restrained)

For the hackathon demo, this simulates the auction mechanism
and demonstrates the bid → recomposition pipeline.
"""

import json
import os
import time
from web3 import Web3
from web3.contract import Contract

BASE_SEPOLIA_RPC = os.environ.get("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
AUTEUR_WALLET = os.environ.get("DEPLOYER_ADDRESS", "")


# Events to listen for (custom auction events or transfer events)
AUCTION_ABI = json.loads('''[
    {"anonymous":false,"inputs":[
        {"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},
        {"indexed":false,"internalType":"uint256","name":"bidAmount","type":"uint256"},
        {"indexed":false,"internalType":"uint256","name":"reservePrice","type":"uint256"}
    ],"name":"BidPlaced","type":"event"},
    {"anonymous":false,"inputs":[
        {"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},
        {"indexed":true,"internalType":"address","name":"from","type":"address"},
        {"indexed":true,"internalType":"address","name":"to","type":"address"}
    ],"name":"Transfer","type":"event"}
]''')


def adjust_tension(current_tension: float, bid_amount: int, reserve_price: int) -> float:
    """Adjust tension level based on bid dynamics.
    
    Args:
        current_tension: Current tension level (0.0 - 1.0)
        bid_amount: Bid amount in wei
        reserve_price: Reserve price in wei
        
    Returns:
        New tension level (clamped 0.0 - 1.0)
    """
    if reserve_price == 0:
        return current_tension
    
    ratio = bid_amount / reserve_price
    
    if ratio > 2.0:
        new_tension = current_tension + 0.15
    elif ratio < 1.0:
        new_tension = current_tension - 0.10
    else:
        # Moderate bid — slight increase for excitement
        new_tension = current_tension + 0.05
    
    return max(0.0, min(1.0, new_tension))


def recompose_shot(shot_spec: dict, new_tension: float) -> dict:
    """Recompose a ShotSpec with adjusted tension level.
    
    Creates a new ShotSpec based on the original but with the
    new tension level, and increments the beat position.
    """
    recomposed = dict(shot_spec)
    recomposed["tension_level"] = round(new_tension, 2)
    recomposed["recomposed"] = True
    recomposed["recomposition_reason"] = "bid_triggered"
    return recomposed


async def listen_for_bids(nft_address: str, callback=None, poll_interval: int = 5):
    """Poll for new bid events on the NFT contract.
    
    For Base Sepolia hackathon demo, this polls Transfer events
    since we may not have a full auction contract. In production,
    this would use websockets and listen for BidPlaced events.
    
    Args:
        nft_address: Address of the NFT/auction contract
        callback: async function(shot_spec, new_tension) called on bid
        poll_interval: Seconds between polls
    """
    w3 = Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))
    if not w3.is_connected():
        print("[listener] Cannot connect to RPC")
        return
    
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(nft_address),
        abi=AUCTION_ABI,
    )
    
    last_block = w3.eth.block_number
    print(f"[listener] Starting at block {last_block}, polling every {poll_interval}s")
    
    while True:
        try:
            current_block = w3.eth.block_number
            if current_block <= last_block:
                time.sleep(poll_interval)
                continue
            
            # Check for Transfer events (NFT sales indicate bids settled)
            transfer_filter = contract.events.Transfer.create_filter(
                fromBlock=last_block + 1,
                toBlock=current_block,
            )
            
            events = transfer_filter.get_all_entries()
            
            for event in events:
                token_id = event["args"]["tokenId"]
                print(f"[listener] Transfer detected: token #{token_id} block {event['blockNumber']}")
                
                if callback:
                    await callback(token_id, event)
            
            last_block = current_block
            time.sleep(poll_interval)
        except Exception as e:
            print(f"[listener] Error: {e}")
            time.sleep(poll_interval)


def simulate_bid_effect(shot_spec: dict, bid_eth: float, reserve_eth: float) -> dict:
    """Simulate a bid's effect on a ShotSpec without onchain interaction.
    
    Used for the demo to show tension adjustment.
    
    Args:
        shot_spec: Original ShotSpec
        bid_eth: Bid amount in ETH
        reserve_eth: Reserve price in ETH
        
    Returns:
        (recomposed_shot, old_tension, new_tension)
    """
    old_tension = shot_spec.get("tension_level", 0.5)
    
    bid_wei = int(bid_eth * 1e18)
    reserve_wei = int(reserve_eth * 1e18)
    
    new_tension = adjust_tension(old_tension, bid_wei, reserve_wei)
    recomposed = recompose_shot(shot_spec, new_tension)
    
    return recomposed, old_tension, new_tension
