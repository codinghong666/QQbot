from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# Global variables to store model and tokenizer
model = None
tokenizer = None

def load_model():
    """Load model and tokenizer to GPU, execute only once"""
    global model, tokenizer
    
    if model is not None and tokenizer is not None:
        print("Model already loaded, skipping reload")
        return
    
    print("Loading model to GPU...")
    model_name = "Qwen/Qwen3-8B"

    # Configure 4-bit quantization
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,  # Enable 4-bit quantization
        bnb_4bit_quant_type="nf4",  # Use NF4 data type, more friendly to normal distribution weights
        bnb_4bit_compute_dtype=torch.float16,  # Use float16 for computation
        bnb_4bit_use_double_quant=True,  # Enable nested quantization, saves additional ~0.5GB VRAM
    )

    # Load tokenizer and quantized model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
        quantization_config=quantization_config  # Key: pass quantization config
    )
    print("Model loading completed")

def extract_time_info(message_text):
    """
    Extract time information from message text
    
    Args:
        message_text: QQ group message text to analyze
        
    Returns:
        Extracted time information string
    """
    global model, tokenizer
    
    # Ensure model is loaded
    if model is None or tokenizer is None:
        load_model()
    
    prompt = open("prompt.txt", "r").read() 
    print(f"prompt: {prompt}")
    
    # Build complete prompt
    full_prompt = prompt + "\n" + message_text
    
    messages = [
        {"role": "user", "content": full_prompt}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True  # Switches between thinking and non-thinking modes. Default is True.
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # Perform text generation
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=2048,
        temperature=0.1,  # Lower temperature for more stable output
        top_p=0.9,        # Nucleus sampling parameter
        do_sample=True,   # Enable sampling
        repetition_penalty=1.1  # Repetition penalty
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    content = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
    if "<think>" in content:
        content = content.split("<think>")[1].split("</think>")[1]
    # Debug information
    # print(f"Thinking content: {thinking_content[:100]}...")
    print(f"Final content: {content}")
    
    # Check if contains time information
    if not content or content.lower() in ['无', '没有', 'none', 'no', '无时间信息', '未检测到时间信息', 'no time information detected']:
        return None
    
    # Check if contains time format (MM:DD:time)
    import re
    time_pattern = r'\d{2}:\d{2}:\d{2}:\d{2}'
    if not re.search(time_pattern, content):
        return None
    
    return content

def unload_model():
    """Unload model and tokenizer, release GPU memory"""
    global model, tokenizer
    
    if model is not None:
        del model
        model = None
        print("Model unloaded from GPU")
    
    if tokenizer is not None:
        del tokenizer
        tokenizer = None
        print("Tokenizer unloaded")
    
    # Force garbage collection
    import gc
    import torch
    gc.collect()
    torch.cuda.empty_cache()  # Clear CUDA cache
    print("GPU memory cleared")

