from langchain_core.messages import HumanMessage, RemoveMessage, AIMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_crypto_tools import (
    get_crypto_data
)
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data,
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators,
    get_indicators_bulk
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_whitepaper,
    get_market_cap
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_sentiment,
    get_insider_transactions,
    get_global_news
)
from tradingagents.agents.utils.sentiment_tools import (
    get_fear_and_greed,
)
from tradingagents.agents.utils.proposal_tools import (
    create_place_order_proposal,
    edit_place_order_proposal,
    create_amend_order_proposal,
    edit_amend_order_proposal,
    create_cancel_order_proposal,
    edit_cancel_order_proposal,
    delete_proposal
)
from tradingagents.dataflows.utils import (
    PLACE_ORDER,
    AMEND_ORDER,
    CANCEL_ORDER,
    CANCEL_PROPOSAL
)
import json

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages

def create_apply_proposal(name):
    def apply_proposal_node(state):
        """
        Apply tool output (create / edit / cancel) into state["proposals"].
        Assumes:
        - tools return dict
        - tool call is the last message
        """

        # Get last tool output
        last_message = state["messages"][-1]
        try:
            result = json.loads(last_message.content)
        except:
            return {}

        # Copy proposals (important: avoid in-place mutation)
        proposals = dict(state[f"{name}_proposal"])
        feedback = []
        messages = state["messages"]

        account_balance = state["account_balance"]
        open_orders = state["open_orders"]

        action_type = result["type"]
        proposal_id = result["id"]

        is_valid = True

        if action_type == CANCEL_ORDER:
            order_id_found = False
            for oo in open_orders:
                if oo["orderId"] == result["order_id"]:
                    order_id_found = True
                    break
            if not order_id_found:
                is_valid = False
        if "order_type" in result.keys():
            order_type = result["order_type"]
            if order_type == "Limit":
                if action_type == PLACE_ORDER:
                    if result["side"] == "Buy":
                        quote_qty = result["qty"] if result["market_unit"] == "quoteCoin" else result["qty"]*result["price"]
                        if quote_qty > account_balance["quote"]["walletBalance"]:
                            feedback.append({
                                "level": "error",
                                "code": "INSUFFICIENT_BALANCE",
                                "message": f'Insufficient quote balance {quote_qty} > {account_balance["quote"]["walletBalance"]} {account_balance["quote"]["symbol"]}'
                            })
                            is_valid = False
                    else:
                        base_qty = result["qty"] if result["market_unit"] == "baseCoin" else result["qty"]/result["price"]
                        if base_qty > account_balance["base"]["walletBalance"]:
                            feedback.append({
                                "level": "error",
                                "code": "INSUFFICIENT_BALANCE",
                                "message": f'Insufficient base balance {base_qty} > {account_balance["base"]["walletBalance"]} {account_balance["base"]["symbol"]}'
                            })
                            is_valid = False
                elif action_type == AMEND_ORDER:
                    for oo in open_orders:
                        if oo["orderId"] == result["order_id"]:
                            if oo["side"] == "Buy":
                                quote_qty = result["qty"] if result["market_unit"] == "quoteCoin" else result["qty"]*result["price"]
                                if quote_qty > account_balance["quote"]["walletBalance"]:
                                    feedback.append({
                                        "level": "error",
                                        "code": "INSUFFICIENT_BALANCE",
                                        "message": f'Insufficient quote balance {quote_qty} > {account_balance["quote"]["walletBalance"]} {account_balance["quote"]["symbol"]}'
                                    })
                                    is_valid = False
                            else:
                                base_qty = result["qty"] if result["market_unit"] == "baseCoin" else result["qty"]/result["price"]
                                if base_qty > account_balance["base"]["walletBalance"]:
                                    feedback.append({
                                        "level": "error",
                                        "code": "INSUFFICIENT_BALANCE",
                                        "message": f'Insufficient base balance {base_qty} > {account_balance["base"]["walletBalance"]} {account_balance["base"]["symbol"]}'
                                    })
                                    is_valid = False
                            break
        if is_valid:
            if proposal_id in proposals:
                if action_type != CANCEL_PROPOSAL:
                    if action_type == proposals[proposal_id]["type"]:
                        proposals[proposal_id].update(result)
                    else:
                        feedback.append({
                            "level": "error",
                            "code": "PROPOSAL_DIFFERENT_TYPE",
                            "message": f'Proposal id `{proposal_id}` type is {proposals[proposal_id]["type"]}, you enter {action_type}'
                        })
                else:
                    del proposals[proposal_id]
            else:
                if action_type == CANCEL_PROPOSAL:
                    feedback.append({
                        "level": "error",
                        "code": "PROPOSAL_NOT_FOUND",
                        "message": f"Proposal id `{proposal_id}` not found"
                    })
                else:
                    proposals[proposal_id] = result

        for el in feedback:
            messages.append(AIMessage(role="system", content=el["message"]))

        return {
            "messages" : messages,
            f"{name}_proposal": proposals,
            f"{name}_feedback" : feedback,
        }
    return apply_proposal_node