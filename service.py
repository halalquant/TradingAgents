from tradingagents.external.redis.repo import redis_queue, redis_repo
from tradingagents.domain.model import AnalysisMeta,  AnalysisStatus, JobResultStatus
from tradingagents.domain.response import EnqueueAnalysisResponse
from rq import get_current_job
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.dataflows.config import get_config
from tradingagents.dataflows.bybit import place_order, cancel_order, amend_order
import json
from tradingagents.dataflows.utils import (
    PLACE_ORDER,
    AMEND_ORDER,
    CANCEL_ORDER
)

trading_agent = None

def get_trading_agent():
    global trading_agent
    if trading_agent is None:
        print("INFO: Initializing TradingAgent (once per worker)")
        trading_agent = TradingAgentsGraph(
            debug=False,
            config=get_config()
        )
    return trading_agent

def process_job(user_id: str, symbol: str, date: str):
    print(f"INFO: Starting job for symbol {symbol} and date {date} by user {user_id}")
    try:
        job = get_current_job()
        attempt = job.meta.get("attempt", 1)
        job.meta["attempt"] = attempt
        job.save_meta()

        print(f"INFO: Processing job-id {job.id} for symbol {symbol} and date {date} by user {user_id}")

        # Update status to RUNNING
        redis_repo.update_status_analysis_meta(user_id=user_id, job_id=job.id, status=AnalysisStatus.RUNNING)

        final_state, decision = get_trading_agent().propagate(ticker=symbol, trade_date=date)

        print(f"INFO: Decision for job-id {job.id}: {decision}")

        # Get the logged state (JSON-serializable) from the trading agent
        logged_state = get_trading_agent().log_states_dict.get(str(date))
        full_state_json = json.dumps(logged_state, indent=2) if logged_state else None

        # Save the final result with full state
        redis_repo.save_result(
            job_id=job.id, 
            final_trade=final_state["final_trade_decision"],
            full_state=full_state_json
        )
        # Update status to DONE
        redis_repo.update_status_analysis_meta(user_id=user_id, job_id=job.id, status=AnalysisStatus.DONE)
        
        print(f"INFO: Completed job-id {job.id} for symbol {symbol}")
    except Exception as e:
        job.meta["attempt"] = attempt + 1
        job.save_meta()
        print(f"ERROR: Failed to process job-id {job.id}: {e} (Attempt {attempt})")
        # Update status to FAILED
        redis_repo.update_status_analysis_meta(user_id=user_id, job_id=job.id, status=AnalysisStatus.FAILED, message=str(e))
        raise e


def enqueue_analysis(user_id: str, symbol: str, date: str) -> EnqueueAnalysisResponse:
    """
    Enqueue a background task to analyze trading data for a given symbol and date.

    Args:
        user_id (str): The user ID requesting the analysis.
        symbol (str): The trading symbol to analyze (e.g., "BTC/USDT").
        date (str): The date for which to perform the analysis in YYYY-MM-DD format.
    Returns:
        EnqueueAnalysisResponse: The response containing job_id, status, and message.
    """
    try:
        # Check if the analysis is on cooldown, if cooldown return the job-id
        job_id, ttl = redis_repo.get_cooldown(user_id, symbol) 
        if job_id:
            return EnqueueAnalysisResponse(
                job_id=job_id,
                status="on_cooldown",
                message=f"Analysis for {symbol} is on cooldown. Please try again later. TTL: {ttl} seconds remaining.",
            )
        
        # If not on cooldown, enqueue the task, insert cooldown key with TTL 6 hours, insert with status pending redis key for analysis analysis:job:{job_id}
        task = redis_queue.enqueue(process_job, user_id, symbol, date, job_timeout=7200)

        redis_repo.save_cooldown(user_id, symbol, task.id)
        redis_repo.create_analysis_meta(AnalysisMeta.new(job_id=task.id, user_id=user_id, symbol=symbol, trade_date=date))

        return EnqueueAnalysisResponse(
            job_id=task.id,
            status="enqueued",
            message=f"Analysis for {symbol} has been enqueued successfully."
        )
    except Exception as e:
        print(f"ERROR: Failed to enqueue analysis task: {e}")
        return EnqueueAnalysisResponse(
            job_id=None,
            status="error",
            message=f"Failed to enqueue analysis task: {str(e)}"
        )

def get_status(user_id: str, job_id: str) -> JobResultStatus:
    """
    Get the status of a trading analysis job. Return the current status and final result if available.

    Args:
        user_id (str): The user ID requesting the status.
        job_id (str): The job ID to check.
    Returns:
        JobResultStatus: The current status and result of the job, or a failed status if not found.
    """
    print(f"INFO: Checking status for job-id {job_id}")
    meta = redis_repo.get_analysis_meta(user_id, job_id)
    result = redis_repo.get_result(job_id)
    
    # Extract the appropriate result format
    final_result = None
    if result:
        if isinstance(result, dict):
            # New format: prefer full_state JSON, fallback to final_trade
            final_result = result.get("full_state") or result.get("final_trade")
        else:
            # Old format: just a string
            final_result = result
    
    if meta:
        return JobResultStatus(status=meta.status, result=final_result, message=meta.message)
    return JobResultStatus(status=AnalysisStatus.NOT_FOUND, result=None, message="Job not found")


def execute_trader_proposal(user_id: str, job_id: str) -> dict:
    """
    Execute trader proposals from a completed job result.
    
    Args:
        user_id (str): The user ID requesting the execution.
        job_id (str): The job ID to fetch the proposal from.
        
    Returns:
        dict: Execution results containing success status, executed orders, and any errors.
    """
    print(f"INFO: Executing trader proposal for job-id {job_id}")
    
    try:
        meta = redis_repo.get_analysis_meta(user_id, job_id)
        
        if not meta:
            return {
                "success": False,
                "error": "Job not found",
                "job_id": job_id
            }
        
        if meta.status != AnalysisStatus.DONE:
            return {
                "success": False,
                "error": f"Job is not in DONE status. Current status: {meta.status.value}",
                "job_id": job_id,
                "current_status": meta.status.value
            }
        
        result = redis_repo.get_result(job_id)
        
        if not result:
            return {
                "success": False,
                "error": "Job result not found",
                "job_id": job_id
            }
        
        full_state = None
        if isinstance(result, dict):
            full_state_str = result.get("full_state")
            if full_state_str:
                full_state = json.loads(full_state_str) if isinstance(full_state_str, str) else full_state_str
        
        if not full_state:
            return {
                "success": False,
                "error": "No full_state found in job result",
                "job_id": job_id
            }
        
        trader_proposal = full_state.get("trader_proposal")
        
        if not trader_proposal:
            return {
                "success": False,
                "error": "No trader_proposal found in job result",
                "job_id": job_id
            }
        
        if not isinstance(trader_proposal, dict):
            return {
                "success": False,
                "error": "trader_proposal is not in expected format",
                "job_id": job_id
            }
        
        execution_results = []
        errors = []
        
        for proposal_id, proposal_data in trader_proposal.items():
            try:
                proposal_type = proposal_data.get("type")
                
                if proposal_type == PLACE_ORDER:
                    result = _execute_place_order(proposal_data)
                    execution_results.append({
                        "proposal_id": proposal_id,
                        "type": proposal_type,
                        "status": "success",
                        "result": result
                    })
                    
                elif proposal_type == CANCEL_ORDER:
                    result = _execute_cancel_order(proposal_data)
                    execution_results.append({
                        "proposal_id": proposal_id,
                        "type": proposal_type,
                        "status": "success",
                        "result": result
                    })
                    
                elif proposal_type == AMEND_ORDER:
                    result = _execute_amend_order(proposal_data)
                    execution_results.append({
                        "proposal_id": proposal_id,
                        "type": proposal_type,
                        "status": "success",
                        "result": result
                    })
                    
                else:
                    errors.append({
                        "proposal_id": proposal_id,
                        "error": f"Unknown proposal type: {proposal_type}"
                    })
                    
            except Exception as e:
                errors.append({
                    "proposal_id": proposal_id,
                    "error": str(e)
                })
                print(f"ERROR: Failed to execute proposal {proposal_id}: {e}")
        
        execution_success = len(errors) == 0
        
        if execution_success:
            redis_repo.update_status_analysis_meta(
                user_id=user_id, 
                job_id=job_id, 
                status=AnalysisStatus.EXECUTED,
                message="All proposals executed successfully"
            )
        
        return {
            "success": execution_success,
            "job_id": job_id,
            "total_proposals": len(trader_proposal),
            "executed": len(execution_results),
            "failed": len(errors),
            "results": execution_results,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        print(f"ERROR: Failed to execute trader proposal for job-id {job_id}: {e}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}",
            "job_id": job_id
        }


def _execute_place_order(proposal: dict) -> dict:
    """Execute a place_order proposal."""
    return place_order(
        symbol=proposal.get("symbol"),
        side=proposal.get("side"),
        order_type=proposal.get("order_type"),
        qty=proposal.get("qty"),
        price=proposal.get("price"),
        market_unit=proposal.get("market_unit"),
        stop_loss=proposal.get("stop_loss"),
        take_profit=proposal.get("take_profit"),
        category=proposal.get("category", "spot")
    )


def _execute_cancel_order(proposal: dict) -> dict:
    """Execute a cancel_order proposal."""
    return cancel_order(
        order_id=proposal.get("order_id"),
        symbol=proposal.get("symbol"),
        category=proposal.get("category", "spot")
    )


def _execute_amend_order(proposal: dict) -> dict:
    """Execute an amend_order proposal."""
    return amend_order(
        order_id=proposal.get("order_id"),
        symbol=proposal.get("symbol"),
        qty=proposal.get("qty"),
        price=proposal.get("price"),
        stop_loss=proposal.get("stop_loss"),
        take_profit=proposal.get("take_profit"),
        category=proposal.get("category", "spot")
    )
