from .bybit import get_symbol
import uuid
import json

def create_place_order_proposal(
    symbol: str="BTC/USDT", 
    side: str="Buy", # Buy, Sell
    order_type: str="Market", # Market, Limit
    qty: float=None, 
    price: float = None, 
    market_unit: str = "baseCoin", # baseCoin, quoteCoin
    take_profit: float = None, 
    stop_loss: float = None, 
    storage = None
):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    
    if "/" not in symbol:
        return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
    base_coin, quote_coin = symbol.split("/")
    symbol_name = get_symbol(base_coin, quote_coin)
    if not symbol_name:
        return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"

    side_condition = side in ["Buy", "Sell"]
    order_type_condition = order_type in ["Market", "Limit"]
    market_unit_condition = market_unit in ["baseCoin", "quoteCoin"]

    if not side_condition:
        return "side must be 'Buy' or 'Sell'."
    if not order_type_condition:
        return "order_type must be 'Market' or 'Limit'."
    if not market_unit_condition:
        return "market_unit must be 'baseCoin' or 'quoteCoin'."

    proposal = {
        "type" : "place order",
        "id": str(uuid.uuid4()),
        "category": "spot",
        "symbol": symbol_name,
        "side": side,
        "order_type": order_type,
        "qty": qty,
        "market_unit": market_unit,
        "price": price,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
    }

    storage.add_proposal(proposal["id"], proposal)
    string = f"Successfully created place order proposal (proposal_id: {proposal['id']}):\n"
    string += json.dumps(proposal, indent=4)
    return string

def edit_place_order_proposal(
        proposal_id: str,
        symbol: str=None,
        side: str=None, # Buy, Sell
        order_type: str=None, # Market, Limit
        qty: float=None, 
        price: float = None, 
        market_unit: str = None, # baseCoin, quoteCoin
        take_profit: float = None, 
        stop_loss: float = None, 
        storage = None
    ):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    if proposal_id not in storage.proposal:
        return f"Error: Proposal with id {proposal_id} does not exist."
    proposal = storage.proposal[proposal_id]
    if symbol is not None:
        if "/" not in symbol:
            return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
        base_coin, quote_coin = symbol.split("/")
        symbol_name = get_symbol(base_coin, quote_coin)
        if not symbol_name:
            return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"
        proposal["symbol"] = symbol_name
    if side is not None:
        proposal["side"] = side
    if order_type is not None:
        proposal["order_type"] = order_type
    if qty is not None:
        proposal["qty"] = qty
    if price is not None:
        proposal["price"] = price
    if market_unit is not None:
        proposal["market_unit"] = market_unit
    if take_profit is not None:
        proposal["take_profit"] = take_profit
    if stop_loss is not None:
        proposal["stop_loss"] = stop_loss
    storage.add_proposal(proposal_id, proposal)

    string = f"Successfully edited place order proposal (proposal_id: {proposal_id}):\n"
    string += json.dumps(proposal, indent=4)
    return string

def create_amend_order_proposal(
    symbol: str="BTC/USDT", 
    order_id: str=None,
    qty: float=None,
    price: float = None,
    take_profit: float = None,
    stop_loss: float = None,
    storage = None
):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    
    if "/" not in symbol:
        return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
    base_coin, quote_coin = symbol.split("/")
    symbol_name = get_symbol(base_coin, quote_coin)
    if not symbol_name:
        return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"

    proposal = {
        "type" : "amend order",
        "id": str(uuid.uuid4()),
        "category": "spot",
        "symbol": symbol_name,
        "order_id": order_id,
        "qty": qty,
        "price": price,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
    }

    storage.add_proposal(proposal["id"], proposal)
    string = f"Successfully created amend order proposal (proposal_id: {proposal['id']} & order_id: {proposal['order_id']}):\n"
    string += json.dumps(proposal, indent=4)
    return string

def edit_amend_order_proposal(
        proposal_id: str,
        symbol: str=None,
        order_id: str=None,
        qty: float=None,
        price: float = None,
        take_profit: float = None,
        stop_loss: float = None,
        storage = None
    ):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    if proposal_id not in storage.proposal:
        return f"Proposal with id {proposal_id} does not exist."
    proposal = storage.proposal[proposal_id]
    if symbol is not None:
        if "/" not in symbol:
            return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
        base_coin, quote_coin = symbol.split("/")
        symbol_name = get_symbol(base_coin, quote_coin)
        if not symbol_name:
            return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"
        proposal["symbol"] = symbol_name
    if order_id is not None:
        proposal["order_id"] = order_id
    if qty is not None:
        proposal["qty"] = qty
    if price is not None:
        proposal["price"] = price
    if take_profit is not None:
        proposal["take_profit"] = take_profit
    if stop_loss is not None:
        proposal["stop_loss"] = stop_loss
    storage.add_proposal(proposal_id, proposal)
    string = f"Successfully edited amend order proposal (proposal_id: {proposal_id} & order_id: {proposal['order_id']}):\n"
    string += json.dumps(proposal, indent=4)
    return string

def create_cancel_order_proposal(
    symbol: str="BTC/USDT", 
    order_id: str=None,
    storage = None
):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    
    if "/" not in symbol:
        return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
    base_coin, quote_coin = symbol.split("/")
    symbol_name = get_symbol(base_coin, quote_coin)
    if not symbol_name:
        return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"

    proposal = {
        "type" : "cancel order",
        "id": str(uuid.uuid4()),
        "category": "spot",
        "symbol": symbol_name,
        "order_id": order_id,
    }

    storage.add_proposal(proposal["id"], proposal)
    string = f"Successfully created cancel order proposal (proposal_id: {proposal['id']} & order_id: {proposal['order_id']}):\n"
    string += json.dumps(proposal, indent=4)
    return string

def edit_cancel_order_proposal(
        proposal_id: str,
        symbol: str=None,
        order_id: str=None,
        storage = None
    ):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    if proposal_id not in storage.proposal:
        return f"Error: Proposal with id {proposal_id} does not exist."
    proposal = storage.proposal[proposal_id]
    if symbol is not None:
        if "/" not in symbol:
            return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
        base_coin, quote_coin = symbol.split("/")
        symbol_name = get_symbol(base_coin, quote_coin)
        if not symbol_name:
            return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"
        proposal["symbol"] = symbol_name
    if order_id is not None:
        proposal["order_id"] = order_id
    storage.add_proposal(proposal_id, proposal)
    string = f"Successfully edited cancel order proposal (proposal_id: {proposal_id} & order_id: {proposal['order_id']}):\n"
    string += json.dumps(proposal, indent=4)
    return string


def delete_proposal(
    proposal_id: str,
    storage = None
):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    if proposal_id not in storage.proposal:
        return f"Error: Proposal with id {proposal_id} does not exist."
    del storage.proposal[proposal_id]
    return f"Successfully deleted proposal with id {proposal_id}."

def show_proposal(storage = None):
    if storage is None:
        raise ValueError("ProposalStorage instance is required.")
    string = "Current proposal:\n"
    string += str(storage)
    return string