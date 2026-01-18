from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
import functools

def create_risk_manager(llm, memory, tools):
    def risk_manager_node(state):
        # 1. Extract State Data
        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        
        market_research_report = state.get("market_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        sentiment_report = state.get("sentiment_report", "")
        trader_plan = state.get("trader_investment_plan", "No plan provided.")
        trader_proposal = state.get("trader_proposal", "No proposal")
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

        # 4. Define System Message
        # system_message = (
        #     f"As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the final course of action.\n\n"
            
        #     f"### Tools & Execution\n"
        #     f"You have access to tools to **edit**, **cancel**, or **create** order proposals. "
        #     f"If the Trader's original plan poses unacceptable risks based on the debate, you MUST use the `edit_place_order_proposal` or `create_cancel_order_proposal` tools to adjust the strategy directly. "
        #     f"If the plan is sound, you may simply confirm it in text or use a tool to finalize parameters if necessary.\n\n"

        #     f"### Decision Guidelines\n"
        #     f"1. **Summarize Key Arguments**: Extract the strongest points from the debate history below.\n"
        #     f"2. **Refine the Plan**: Start with the trader's original plan: **{trader_plan}**. Adjust it based on the analysts' insights. Use tools to apply these adjustments formally.\n"
        #     f"3. **Learn from Past Mistakes**: Use lessons from: **{past_memory_str}** to avoid prior misjudgments.\n"
        #     f"4. **Final Verdict**: Your text response must be a clear recommendation: Buy, Sell, or Hold. (Choose Hold only if strongly justified).\n\n"

        #     f"### Current Account Balance\n"
        #     f"{account_balance}\n\n"
            
        #     f"### Current Open Orders in Exchange\n"
        #     f"{open_orders}\n\n"

        #     f"### Trader's Proposal\n"
        #     f"{trader_proposal}\n\n"

        #     f"### Analysts Debate History\n"
        #     f"{history}\n\n"

        #     f"### Objective\n"
        #     f"Focus on actionable insights. If the Trader's proposal (quantity, price, side) needs changing to mitigate risk, **CALL THE TOOL** to edit it.\n"
        #     f"Provide detailed reasoning anchored in the debate.\n"
        #     f"In the end, make a markdown style report of the final trade decision.\n"
        # )
        system_message = (
            f"As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the final course of action.\n\n"

            f"### Tools & Execution\n"
            f"You have access to tools to **create**, **edit**, or **cancel** orders. "
            f"**CRITICAL:** The 'Trader's Proposal' below is a suggestion only. It is not an active order.\n"
            f"1. **If you AGREE** with the Trader's proposal: You **MUST** call the `create_order_proposal` tool using the exact parameters to execute it.\n"
            f"2. **If you DISAGREE**: Simply **skip it** (do not call the tool). Do not attempt to 'edit' the Trader's proposal text.\n"
            f"**Note:** The `edit_order_proposal` and `cancel_order_proposal` tools are strictly for managing existing open orders or modifying your own active proposals, not the Trader's suggestion.\n\n"

            f"### Decision Guidelines\n"
            f"1. **Summarize Key Arguments**: Extract the strongest points from the debate history below.\n"
            f"2. **Evaluate the Plan**: Review the trader's plan: **{trader_plan}** against the analysts' insights.\n"
            f"3. **Learn from Past Mistakes**: Use lessons from: **{past_memory_str}** to avoid prior misjudgments.\n"
            f"4. **Final Verdict**: Your text response must be a clear recommendation: Buy, Sell, or Hold.\n\n"

            f"### Current Account Balance\n"
            f"{account_balance}\n\n"

            f"### Current Open Orders in Exchange\n"
            f"{open_orders}\n\n"

            f"### Trader's Proposal (Suggestion Only)\n"
            f"{trader_proposal}\n\n"

            f"### Analysts Debate History\n"
            f"{history}\n\n"

            f"### Objective\n"
            f"Focus on actionable insights. If the Trader's proposal is sound, **CALL THE TOOL** to execute it. If it is risky, skip it.\n"
            f"Provide detailed reasoning anchored in the debate.\n"
            f"In the end, make a markdown style report of the final trade decision.\n"
        )

        # 5. Construct Prompt Template
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

        # 6. Fill Partial Variables
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

        # 7. Create Chain and Invoke
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        judge_decision_text = ""
        if len(result.tool_calls) == 0:
            judge_decision_text = result.content

        # 9. Update Risk Debate State
        new_risk_debate_state = {
            "judge_decision": judge_decision_text,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "messages": [result], 
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": judge_decision_text, # Now contains the full concatenated history
        }

    return risk_manager_node