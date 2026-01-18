from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor
@tool
def create_place_order_proposal(
    symbol: Annotated[str, "The trading pair symbol, e.g., 'BTC/USDT'"]="BTC/USDT",
    side: Annotated[str, "The order side, either 'Buy' or 'Sell'"]="Buy",
    order_type: Annotated[str, "The order type, either 'Market' or 'Limit'"]="Market",
    qty: Annotated[float, "The quantity of market unit asset"]=None,
    price: Annotated[float, "The price of the base coin (ignored if order_type is 'Market')"]=None,
    market_unit: Annotated[str, "The market unit, either 'baseCoin' or 'quoteCoin')"]="baseCoin",
    take_profit: Annotated[float, "The price of take profit"]=None,
    stop_loss: Annotated[float, "The price of stop loss"]=None
):
    """
    Create a trading place order proposal without executing it on the exchange.
    This tool records a proposed order in the internal proposal storage.
    It does NOT place any real orders on an exchange.
    Args:
        symbol: Trading pair symbol for the order.
        side: Direction of the order, either Buy or Sell.
        order_type: Order type, either Market or Limit.
        qty: Quantity of the asset specified by `market_unit`.
        price: Limit price for the order. Ignored if `order_type` is Market.
        market_unit: Unit used for `qty`, either baseCoin or quoteCoin.
        take_profit: Target price at which the position should take profit.
        stop_loss: Price at which the position should be stopped to limit loss.

    Returns:
        str: A human-readable description of the created order proposal,
        including its key parameters and current proposal status.
    """
    return route_to_vendor("create_place_order_proposal",
                        symbol,
                        side,
                        order_type,
                        qty,
                        price,
                        market_unit,
                        take_profit,
                        stop_loss)

@tool
def edit_place_order_proposal(
    proposal_id: Annotated[str, "The proposal id that needs to be edited"],
    symbol: Annotated[str, "The trading pair symbol, e.g., 'BTC/USDT'"]="BTC/USDT",
    side: Annotated[str, "The order side, either 'Buy' or 'Sell'"]=None,
    order_type: Annotated[str, "The order type, either 'Market' or 'Limit'"]=None,
    qty: Annotated[float, "The quantity of market unit asset"]=None, 
    price: Annotated[float, "The price of the base coin (ignored if order_type is 'Market')"]=None,
    market_unit: Annotated[str, "The market unit, either 'baseCoin' or 'quoteCoin')"]=None,
    take_profit: Annotated[float, "The price of take profit"]=None,
    stop_loss: Annotated[float, "The price of stop loss"]=None 
):
    """
    Edit an existing trading place order proposal without executing it on the exchange.
    This tool updates an already recorded order proposal in the internal proposal storage.
    It does NOT place any real orders on an exchange.

    Args:
        proposal_id: Unique identifier of the existing order proposal to be edited.
        symbol: Trading pair symbol for the order.
        side: Direction of the order, either Buy or Sell.
        order_type: Order type, either Market or Limit.
        qty: Quantity of the asset specified by `market_unit`.
        price: Limit price for the order. Ignored if `order_type` is Market.
        market_unit: Unit used for `qty`, either baseCoin or quoteCoin.
        take_profit: Target price at which the position should take profit.
        stop_loss: Price at which the position should be stopped to limit loss.

    Returns:
        str: A human-readable description of the updated order proposal,
        including its modified parameters and current proposal status.
    """
    return route_to_vendor("edit_place_order_proposal",
                            proposal_id,
                            symbol,
                            side,
                            order_type,
                            qty,
                            price,
                            market_unit,
                            take_profit,
                            stop_loss)

@tool
def create_amend_order_proposal(
    order_id: Annotated[str, "The order id"],
    symbol: Annotated[str, "The trading pair symbol, e.g., 'BTC/USDT'"]="BTC/USDT",
    qty: Annotated[float, "The quantity of market unit asset"]=None,
    price: Annotated[float, "The price of the base coin (ignored if order_type is 'Market')"]=None,
    take_profit: Annotated[float, "The price of take profit"]=None,
    stop_loss: Annotated[float, "The price of stop loss"]=None,
):
    """
    Create an amendment proposal for an existing exchange order without executing it.
    This tool records a proposed amendment to an already existing exchange order
    in the internal proposal storage. It does NOT modify any real orders on an exchange.

    Args:
        order_id: Identifier of the existing exchange order to be amended.
        symbol: Trading pair symbol associated with the order.
        qty: Updated quantity of the asset specified by the original order.
        price: Updated limit price for the order. Ignored if the original order type is Market.
        take_profit: Updated take profit price for the order.
        stop_loss: Updated stop loss price for the order.

    Returns:
        str: A human-readable description of the created amend-order proposal,
        including the proposed changes and current proposal status.
    """
    return route_to_vendor("create_amend_order_proposal",
                            order_id,
                            symbol,
                            qty,
                            price,
                            take_profit,
                            stop_loss)

@tool
def edit_amend_order_proposal(
    proposal_id: Annotated[str, "The proposal id that needs to be edited"],
    order_id: Annotated[str, "The order id"]=None,
    symbol: Annotated[str, "The trading pair symbol, e.g., 'BTC/USDT'"]="BTC/USDT",
    qty: Annotated[float, "The quantity of market unit asset"]=None,
    price: Annotated[float, "The price of the base coin (ignored if order_type is 'Market')"]=None,
    take_profit: Annotated[float, "The price of take profit"]=None,
    stop_loss: Annotated[float, "The price of stop loss"]=None,
):
    """
    Edit an existing amend-order proposal without executing it on the exchange.
    This tool updates a previously recorded amend-order proposal in the internal
    proposal storage. It does NOT modify any real orders on an exchange.

    Args:
        proposal_id: Unique identifier of the amend-order proposal to be edited.
        order_id: Identifier of the existing exchange order being amended.
        symbol: Trading pair symbol associated with the order.
        qty: Updated quantity of the asset specified by the original order.
        price: Updated limit price for the order. Ignored if the original order type is Market.
        take_profit: Updated take profit price for the order.
        stop_loss: Updated stop loss price for the order.

    Returns:
        str: A human-readable description of the updated amend-order proposal,
        including its modified parameters and current proposal status.
    """
    return route_to_vendor("edit_amend_order_proposal",
                            proposal_id,
                            order_id,
                            symbol,
                            qty,
                            price,
                            take_profit,
                            stop_loss)

@tool
def create_cancel_order_proposal(
    order_id: Annotated[str, "The order id"],
    symbol: Annotated[str, "The trading pair symbol, e.g., 'BTC/USDT'"]="BTC/USDT",
):
    """
    Create a cancel-order proposal without executing it on the exchange.
    This tool records a proposed cancellation for an existing exchange order
    in the internal proposal storage. It does NOT cancel any real orders on an exchange.

    Args:
        order_id: Identifier of the existing exchange order to be cancelled.
        symbol: Trading pair symbol associated with the order.

    Returns:
        str: A human-readable description of the created cancel-order proposal,
        including the referenced order and current proposal status.
    """
    return route_to_vendor("create_cancel_order_proposal",
                            order_id,
                            symbol,)

@tool
def edit_cancel_order_proposal(
    proposal_id: Annotated[str, "The proposal id that needs to be edited"],
    order_id: Annotated[str, "The order id"],
    symbol: Annotated[str, "The trading pair symbol, e.g., 'BTC/USDT'"]="BTC/USDT",
):
    """
    Edit an existing cancel-order proposal without executing it on the exchange.
    This tool updates a previously recorded cancel-order proposal in the internal
    proposal storage. It does NOT cancel any real orders on an exchange.

    Args:
        proposal_id: Unique identifier of the cancel-order proposal to be edited.
        order_id: Identifier of the existing exchange order to be cancelled.
        symbol: Trading pair symbol associated with the order.

    Returns:
        str: A human-readable description of the updated cancel-order proposal,
        including its modified parameters and current proposal status.
    """
    return route_to_vendor("edit_cancel_order_proposal",
                            proposal_id,
                            order_id,
                            symbol,)

@tool
def delete_proposal(
    proposal_id: Annotated[str, "The proposal id that needs to be edited"],
):
    """
    Delete an existing order proposal without executing any exchange action.
    This tool permanently removes a previously recorded order proposal from the
    internal proposal storage. It does NOT place, amend, or cancel any real orders
    on an exchange.

    Args:
        proposal_id: Unique identifier of the order proposal to be deleted.

    Returns:
        str: A human-readable confirmation message indicating that the proposal
        has been deleted, including the proposal identifier and deletion status.
    """
    return route_to_vendor("delete_proposal",
                            proposal_id,)