import tiktoken
import logging
from typing import List

logger = logging.getLogger(__name__)

# Encoding for GPT-4 models (cl100k_base)
ENCODING_NAME = "cl100k_base"

def get_encoding():
    """Get the tiktoken encoding for GPT-4 models."""
    try:
        return tiktoken.get_encoding(ENCODING_NAME)
    except Exception as e:
        logger.error(f"Error loading tiktoken encoding: {e}")
        return None

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens for
        model: The model name (default: gpt-4o-mini)
    
    Returns:
        Number of tokens in the text
    """
    if not text:
        return 0
    
    try:
        encoding = get_encoding()
        if encoding is None:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
        
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback estimate
        return len(text) // 4

def count_messages_tokens(messages: List[dict], model: str = "gpt-4o-mini") -> int:
    """
    Count the number of tokens in a list of messages.
    
    This accounts for the special tokens used in chat completions.
    Based on OpenAI's token counting guide.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: The model name (default: gpt-4o-mini)
    
    Returns:
        Total number of tokens including formatting
    """
    if not messages:
        return 0
    
    try:
        encoding = get_encoding()
        if encoding is None:
            # Fallback: estimate based on content
            return sum(count_tokens(msg.get("content", "")) for msg in messages) + len(messages) * 4
        
        num_tokens = 0
        
        for message in messages:
            # Every message follows <|start|>{role/name}\n{content}<|end|>\n
            num_tokens += 4  # Formatting tokens per message
            
            for key, value in message.items():
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                    
                if key == "name":  # If there's a name, it adds extra tokens
                    num_tokens += -1  # Role is always required and always 1 token
        
        num_tokens += 2  # Every reply is primed with <|start|>assistant
        
        return num_tokens
        
    except Exception as e:
        logger.error(f"Error counting message tokens: {e}")
        # Fallback estimate
        return sum(count_tokens(msg.get("content", "")) for msg in messages) + len(messages) * 4

def truncate_to_budget(text: str, max_tokens: int, model: str = "gpt-4o-mini") -> str:
    """
    Truncate text to fit within a token budget.
    
    Args:
        text: The text to truncate
        max_tokens: Maximum number of tokens allowed
        model: The model name (default: gpt-4o-mini)
    
    Returns:
        Truncated text that fits within the budget
    """
    if not text:
        return ""
    
    current_tokens = count_tokens(text, model)
    
    if current_tokens <= max_tokens:
        return text
    
    try:
        encoding = get_encoding()
        if encoding is None:
            # Fallback: rough character-based truncation
            chars_per_token = len(text) / current_tokens
            target_chars = int(max_tokens * chars_per_token * 0.95)  # 5% safety margin
            return text[:target_chars] + "..."
        
        # Encode and truncate
        tokens = encoding.encode(text)
        truncated_tokens = tokens[:max_tokens]
        truncated_text = encoding.decode(truncated_tokens)
        
        return truncated_text + "..."
        
    except Exception as e:
        logger.error(f"Error truncating text: {e}")
        # Fallback: rough character-based truncation
        chars_per_token = len(text) / current_tokens if current_tokens > 0 else 4
        target_chars = int(max_tokens * chars_per_token * 0.95)
        return text[:target_chars] + "..."

def estimate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4o-mini") -> float:
    """
    Estimate the cost of a request in USD.
    
    Pricing (as of 2024):
    - gpt-4o-mini: $0.150 / 1M input, $0.600 / 1M output
    - gpt-4o: $2.50 / 1M input, $10.00 / 1M output
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: The model name
    
    Returns:
        Estimated cost in USD
    """
    if "gpt-4o-mini" in model:
        input_cost_per_m = 0.150
        output_cost_per_m = 0.600
    elif "gpt-4o" in model:
        input_cost_per_m = 2.50
        output_cost_per_m = 10.00
    else:
        # Default to gpt-4o-mini pricing
        input_cost_per_m = 0.150
        output_cost_per_m = 0.600
    
    input_cost = (input_tokens / 1_000_000) * input_cost_per_m
    output_cost = (output_tokens / 1_000_000) * output_cost_per_m
    
    return input_cost + output_cost

