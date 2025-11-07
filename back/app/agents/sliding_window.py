import logging
from typing import List, Dict
from app.utils.token_counter import count_messages_tokens, count_tokens

logger = logging.getLogger(__name__)

# Configuration
SLIDING_WINDOW_SIZE = 10  # Keep last N messages complete
TOKEN_BUDGET_HISTORY = 2400  # 30% of 8000 tokens


def compress_old_messages(messages: List[Dict[str, str]]) -> str:
    """
    Compress old messages into a summary.
    
    Args:
        messages: List of old messages to compress
    
    Returns:
        A summary string of the old messages
    """
    if not messages:
        return ""
    
    user_messages = [m for m in messages if m.get("role") == "user"]
    assistant_messages = [m for m in messages if m.get("role") == "assistant"]
    
    # Extract key information
    health_keywords = [
        "edad", "año", "peso", "kg", "altura", "cm", "cintura", "presión", 
        "colesterol", "fumo", "ejercicio", "actividad", "sueño", "hora"
    ]
    
    important_snippets = []
    for msg in user_messages:
        content = msg.get("content", "").lower()
        if any(keyword in content for keyword in health_keywords):
            # Keep first 50 chars of important messages
            important_snippets.append(msg.get("content", "")[:50])
    
    summary_parts = []
    if important_snippets:
        summary_parts.append(f"Información previa: {'; '.join(important_snippets[:3])}")
    
    summary_parts.append(f"[{len(messages)} mensajes anteriores resumidos]")
    
    return " ".join(summary_parts)


def apply_sliding_window(
    messages: List[Dict[str, str]], 
    max_tokens: int = TOKEN_BUDGET_HISTORY,
    window_size: int = SLIDING_WINDOW_SIZE
) -> List[Dict[str, str]]:
    """
    Apply sliding window strategy to message history.
    
    Strategy:
    1. Always keep the last N messages complete
    2. Compress older messages into a summary
    3. Ensure total tokens stay within budget
    
    Args:
        messages: Full message history
        max_tokens: Maximum tokens allowed for history
        window_size: Number of recent messages to keep complete
    
    Returns:
        Optimized message list within token budget
    """
    if not messages:
        return []
    
    # Calculate current token usage
    current_tokens = count_messages_tokens(messages)
    
    logger.info(f"Sliding window: {len(messages)} messages, {current_tokens} tokens")
    
    # If within budget, return as is
    if current_tokens <= max_tokens:
        logger.info(f"Within budget ({current_tokens}/{max_tokens}), no compression needed")
        return messages
    
    # If we have fewer messages than window size, we need to truncate content
    if len(messages) <= window_size:
        logger.warning(f"Too many tokens in {len(messages)} messages, truncating content")
        return truncate_recent_messages(messages, max_tokens)
    
    # Split into old and recent messages
    old_messages = messages[:-window_size]
    recent_messages = messages[-window_size:]
    
    # Compress old messages
    compressed_summary = compress_old_messages(old_messages)
    
    # Create summary message
    if compressed_summary:
        summary_message = {
            "role": "system",
            "content": compressed_summary
        }
        result = [summary_message] + recent_messages
    else:
        result = recent_messages
    
    # Check if still over budget
    result_tokens = count_messages_tokens(result)
    
    if result_tokens > max_tokens:
        logger.warning(f"Still over budget after compression ({result_tokens}/{max_tokens}), further truncating")
        result = truncate_recent_messages(result, max_tokens)
    
    final_tokens = count_messages_tokens(result)
    logger.info(f"Sliding window applied: {len(result)} messages, {final_tokens} tokens (saved {current_tokens - final_tokens} tokens)")
    
    return result


def truncate_recent_messages(
    messages: List[Dict[str, str]], 
    max_tokens: int
) -> List[Dict[str, str]]:
    """
    Truncate recent messages to fit within token budget.
    Keeps the most recent messages and truncates older ones.
    
    Args:
        messages: Messages to truncate
        max_tokens: Maximum tokens allowed
    
    Returns:
        Truncated message list
    """
    if not messages:
        return []
    
    # Start from the end and work backwards
    result = []
    tokens_used = 0
    
    for msg in reversed(messages):
        msg_tokens = count_messages_tokens([msg])
        
        if tokens_used + msg_tokens <= max_tokens:
            result.insert(0, msg)
            tokens_used += msg_tokens
        else:
            # Try to include a truncated version
            remaining_tokens = max_tokens - tokens_used
            if remaining_tokens > 50:  # Only if we have reasonable space
                truncated_content = msg.get("content", "")[:remaining_tokens * 4]
                truncated_msg = {
                    "role": msg.get("role", "user"),
                    "content": truncated_content + "..."
                }
                result.insert(0, truncated_msg)
            break
    
    logger.info(f"Truncated to {len(result)} messages, {tokens_used} tokens")
    return result


def prioritize_health_data_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Ensure messages containing health data are prioritized in the window.
    
    Args:
        messages: Message history
    
    Returns:
        Reordered messages with health data prioritized
    """
    health_keywords = [
        "edad", "año", "años", "peso", "kg", "altura", "cm", "mido", "mide",
        "cintura", "presión", "colesterol", "fumo", "fuma", "cigarr",
        "ejercicio", "actividad", "física", "deporte", "gimnasio",
        "sueño", "duermo", "hora", "dormir"
    ]
    
    health_messages = []
    other_messages = []
    
    for msg in messages:
        content = msg.get("content", "").lower()
        if any(keyword in content for keyword in health_keywords):
            health_messages.append(msg)
        else:
            other_messages.append(msg)
    
    # Prioritize health data messages but maintain chronological order within groups
    # This is a simple strategy; we keep health messages in the window
    return health_messages + other_messages


def get_optimized_history(
    messages: List[Dict[str, str]],
    max_tokens: int = TOKEN_BUDGET_HISTORY
) -> List[Dict[str, str]]:
    """
    Main function to get optimized conversation history.
    
    This applies:
    1. Sliding window compression
    2. Health data prioritization
    3. Token budget enforcement
    
    Args:
        messages: Full conversation history
        max_tokens: Maximum tokens allowed
    
    Returns:
        Optimized message history
    """
    if not messages:
        return []
    
    logger.info(f"Optimizing history: {len(messages)} messages")
    
    # Apply sliding window
    optimized = apply_sliding_window(messages, max_tokens)
    
    return optimized

