import base64
import httpx
from app.core.config import settings
from common.logger import get_logger

logger = get_logger(__name__)

class ImageAnalysisService:
    @staticmethod
    async def analyze_infra_image(file_content: bytes, content_type: str) -> str:
        """
        Analyzes an infrastructure diagram image using a vision-capable LLM.
        Returns a text description of the architecture.
        """
        system_prompt = "You are an expert software architect. Analyze the provided diagram and describe the system architecture, components, and data flows."

        try:
            logger.info("Starting image analysis...")

            # Validate file size
            file_size_mb = len(file_content) / (1024 * 1024)
            if len(file_content) > settings.max_file_size:
                raise ValueError(
                    f"Image file too large ({file_size_mb:.2f}MB). "
                    f"Maximum allowed: {settings.max_file_size / (1024 * 1024):.0f}MB"
                )
            logger.info(f"Image size: {file_size_mb:.2f}MB")
            
            # Check if SVG
            if content_type == "image/svg+xml":
                try:
                    svg_content = file_content.decode('utf-8')
                    logger.info("Processing SVG as text content")

                    # Check SVG content size (rough token estimate: 1 token ≈ 4 chars)
                    estimated_tokens = len(svg_content) / 4
                    max_svg_tokens = 50000  # Conservative limit for most models
                    if estimated_tokens > max_svg_tokens:
                        logger.warning(
                            f"SVG content very large (~{estimated_tokens:.0f} tokens). "
                            "Truncating to prevent context overflow."
                        )
                        # Truncate SVG content to fit within token limits
                        svg_content = svg_content[: int(max_svg_tokens * 4)]

                    user_prompt = (
                        "Analyze this software architecture diagram (provided as SVG code) in detail. "
                        "1. List all components (services, databases, queues, external systems).\n"
                        "2. Describe the relationships and data flows between them.\n"
                        "3. Identify any technologies or protocols mentioned (e.g., HTTP, gRPC, Kafka).\n"
                        "4. Provide a summary of what this system does based on the visual information.\n"
                        "Be strictly factual based on the code provided.\n\n"
                        f"SVG Content:\n```xml\n{svg_content}\n```"
                    )
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                except UnicodeDecodeError:
                    # Fallback if svg is not utf-8 text (unlikely for svg)
                    logger.warning("Failed to decode SVG as text, attempting base64 image flow")
                    # Proceed to default image flow (might fail if model doesn't support svg image url)
                    base64_image = base64.b64encode(file_content).decode('utf-8')
                    image_url = f"data:{content_type};base64,{base64_image}"
                    
                    user_prompt_text = (
                        "Analyze this software architecture diagram in detail. "
                        "1. List all components (services, databases, queues, external systems).\n"
                        "2. Describe the relationships and data flows between them.\n"
                        "3. Identify any technologies or protocols mentioned (e.g., HTTP, gRPC, Kafka).\n"
                        "4. Provide a summary of what this system does based on the visual information.\n"
                        "Be strictly factual based on what you see in the image."
                    )

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": user_prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url}
                                }
                            ]
                        }
                    ]

            else:
                # Standard Image Flow (PNG, JPEG, etc.)
                base64_image = base64.b64encode(file_content).decode('utf-8')
                image_url = f"data:{content_type};base64,{base64_image}"

                user_prompt_text = (
                    "Analyze this software architecture diagram in detail. "
                    "1. List all components (services, databases, queues, external systems).\n"
                    "2. Describe the relationships and data flows between them.\n"
                    "3. Identify any technologies or protocols mentioned (e.g., HTTP, gRPC, Kafka).\n"
                    "4. Provide a summary of what this system does based on the visual information.\n"
                    "Be strictly factual based on what you see in the image."
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ]

            # Prepare request to LLM provider (using OpenRouter/OpenAI compatible API)
            api_key = settings.api_key
            if not api_key:
                raise ValueError("API_KEY is not configured. Please set API_KEY in your .env file.")

            base_url = settings.openrouter_api_url

            # Use a vision-capable model for image analysis
            model = settings.default_model_image
            if not model:
                # Fallback to default_model if default_model_image is not set
                model = settings.default_model
                if not model:
                    raise ValueError(
                        "DEFAULT_MODEL_IMAGE is not configured. Please set DEFAULT_MODEL_IMAGE "
                        "in your .env file to a vision-capable model (e.g., 'openai/gpt-4-vision-preview', "
                        "'anthropic/claude-3-sonnet', or 'google/gemini-pro-1.5')."
                    )
                logger.warning(f"DEFAULT_MODEL_IMAGE not set, falling back to DEFAULT_MODEL: {model}")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.openrouter_http_referer,
                "X-Title": settings.openrouter_title,
            }

            # Configure max tokens for response
            max_response_tokens = settings.image_analysis_max_tokens

            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": max_response_tokens,
            }

            logger.info(f"Sending image to {model} (max_tokens: {max_response_tokens})")

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(base_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extract content from response
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    content = choice["message"]["content"]

                    # Check if response was truncated
                    finish_reason = choice.get("finish_reason", "unknown")
                    if finish_reason == "length":
                        logger.warning(
                            f"Response truncated due to max_tokens limit ({max_response_tokens}). "
                            "Consider increasing image_analysis_max_tokens in settings."
                        )
                        content += "\n\n[Note: Analysis may be incomplete due to length limits]"

                    logger.info(f"Analysis complete. Finish reason: {finish_reason}")
                    return content
                else:
                    logger.error(f"Unexpected LLM response format: {result}")
                    return "Failed to analyze image: Unexpected response from AI provider."

        except Exception as e:
            logger.error(f"Error during image analysis: {str(e)}")
            raise e
