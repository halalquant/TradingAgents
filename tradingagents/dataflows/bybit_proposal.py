from .bybit import get_symbol
from .utils import (
    PLACE_ORDER,
    AMEND_ORDER,
    CANCEL_ORDER,
    CANCEL_PROPOSAL
)
import uuid


def create_place_order_proposal(
    symbol: str="BTC/USDT", 
    side: str="Buy", # Buy, Sell
    order_type: str="Market", # Market, Limit
    qty: float=None, 
    price: float = None, 
    market_unit: str = "baseCoin", # baseCoin, quoteCoin
    take_profit: float = None, 
    stop_loss: float = None,
):
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
        return "Error: side must be 'Buy' or 'Sell'."
    if not order_type_condition:
        return "Error: order_type must be 'Market' or 'Limit'."
    if not market_unit_condition:
        return "market_unit must be 'baseCoin' or 'quoteCoin'."

    proposal = {
        "type" : PLACE_ORDER,
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
    return proposal

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
    ):
    proposal = {
        "type" : PLACE_ORDER,
        "id" : proposal_id
    }
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
    return proposal

def create_amend_order_proposal(
    order_id: str=None,
    symbol: str="BTC/USDT", 
    qty: float=None,
    price: float = None,
    take_profit: float = None,
    stop_loss: float = None,
):
    
    if "/" not in symbol:
        return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
    base_coin, quote_coin = symbol.split("/")
    symbol_name = get_symbol(base_coin, quote_coin)
    if not symbol_name:
        return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"

    proposal = {
        "type" : AMEND_ORDER,
        "id": str(uuid.uuid4()),
        "category": "spot",
        "symbol": symbol_name,
        "order_id": order_id,
        "qty": qty,
        "price": price,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
    }
    return proposal

def edit_amend_order_proposal(
        proposal_id: str,
        order_id: str=None,
        symbol: str=None,
        qty: float=None,
        price: float = None,
        take_profit: float = None,
        stop_loss: float = None,
    ):
    proposal = {
        "type" : AMEND_ORDER,
        "id" : proposal_id
    }
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
    return proposal

def create_cancel_order_proposal(
    order_id: str=None,
    symbol: str="BTC/USDT", 
):
    if "/" not in symbol:
        return f"Error: Symbol '{symbol}' is not in the correct format. Please use 'BASE/QUOTE' format, e.g., 'BTC/USDT'."
    base_coin, quote_coin = symbol.split("/")
    symbol_name = get_symbol(base_coin, quote_coin)
    if not symbol_name:
        return f"Error: No valid spot symbol found for {base_coin}/{quote_coin}"

    proposal = {
        "type" : CANCEL_ORDER,
        "id": str(uuid.uuid4()),
        "category": "spot",
        "symbol": symbol_name,
        "order_id": order_id,
    }
    return proposal

def edit_cancel_order_proposal(
        proposal_id: str,
        order_id: str=None,
        symbol: str=None,
    ):
    proposal = {
        "type" : CANCEL_ORDER,
        "id" : proposal_id
    }
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
    return proposal


def delete_proposal(
    proposal_id: str,
):
    proposal = {
        "type" : CANCEL_PROPOSAL,
        "id" : proposal_id
    }
    return proposal