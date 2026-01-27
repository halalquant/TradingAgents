from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import functools

def create_trader(llm, memory, tools):
    def trader_node(state, name):
        # 1. Extract State Data
        ticker = state.get("ticker_of_interest", "")
        investment_plan = state.get("investment_plan", "")
        market_research_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        account_balance = state.get("account_balance", "")
        open_orders = state.get("open_orders", "")
        
        # 2. Context Construction
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        # 3. Memory Retrieval
        past_memories = memory.get_memories(curr_situation, n_matches=2)
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # 4. Symbol Context Parsing
        base_asset = ""
        quote_asset = ""
        if isinstance(ticker, str) and "/" in ticker:
            base_asset, quote_asset = ticker.split("/", 1)

        pair_context = ticker
        if base_asset and quote_asset:
            pair_context = f"{ticker} (base={base_asset}, quote={quote_asset})"

        # 5. Define System Message
        # Note: We removed the "FINAL TRANSACTION PROPOSAL" requirement.
        # We emphasize using the tools to record the decision.
        system_message = (
            f"You are a crypto trading agent analyzing cryptocurrency market data for a specific trading pair (e.g., BTC/USDT). "
            f"Your goal is to make a trading decision based on the analysis provided by your team.\n\n"
            
            f"### Tools & Execution\n"
            f"You have access to a proposal storage system via your tools. "
            f"**To execute a decision (Buy or Sell), you MUST use the `create_place_order_proposal` tool.** "
            f"Merely writing 'I want to buy' in the chat is insufficient; the tool call is required to record the order.\n"
            f"If you decide to HOLD (do nothing), simply state your reasoning in the final response without calling any order creation tools.\n\n"
            
            f"### Context Analysis\n"
            f"Review the following investment plan and reports:\n"
            f"**Proposed Investment Plan:** {investment_plan}\n"
            f"**Market Context:** {pair_context}\n\n"
            f"**Current Account Balance:** {account_balance}\n\n"
            f"**Current Open Orders in Exchange:** {open_orders}\n\n"
            
            f"### Past Reflections\n"
            f"Reflect on these lessons from similar past situations:\n{past_memory_str}\n\n"
            
            f"### Objective\n"
            f"1. Analyze the inputs.\n"
            f"2. Decide whether to Buy, Sell, or Hold.\n"
            f"3. If Buying or Selling, **CALL THE APPROPRIATE TOOL** with the correct quantity and price parameters.\n"
            f"4. Because the trading is done once a day, there might be any volatile changes, it is best for you to use Limit order.\n"
            f"5. You can make multiple proposal to secure the position and layered the risks.\n"
        )

        # 6. Construct Prompt Template
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " You have access to the following tools: {tool_names}.\n\n"
                    "{system_message}"
                    "Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # 7. Fill Partial Variables
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        
        # 8. Create Chain and Invoke
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        # 9. Handle Output
        # The 'trader_investment_plan' will be the text explanation accompanying the tool call (or the Hold explanation).
        trader_investment_plan = ""
        if len(result.tool_calls) == 0:
            trader_investment_plan = result.content

        return {
            "messages": [result],
            "trader_investment_plan": trader_investment_plan,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")