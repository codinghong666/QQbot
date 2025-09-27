from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# 全局变量存储模型和分词器
model = None
tokenizer = None

def load_model():
    """加载模型和分词器到显卡，只执行一次"""
    global model, tokenizer
    
    if model is not None and tokenizer is not None:
        print("Model already loaded, skipping reload")
        return
    
    print("Loading model to GPU...")
    model_name = "Qwen/Qwen3-8B"

    # 配置4-bit量化
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,  # 启用4-bit量化
        bnb_4bit_quant_type="nf4",  # 使用NF4数据类型，对正态分布权重更友好
        bnb_4bit_compute_dtype=torch.float16,  # 使用float16进行计算
        bnb_4bit_use_double_quant=True,  # 启用嵌套量化，可额外节省约0.5GB显存
    )

    # 加载分词器和量化模型
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
        quantization_config=quantization_config  # 关键：传入量化配置
    )
    print("Model loading completed")

def extract_time_info(message_text):
    """
    从消息文本中提取时间信息
    
    Args:
        message_text: 要分析的QQ群消息文本
        
    Returns:
        提取到的时间信息字符串
    """
    global model, tokenizer
    
    # 确保模型已加载
    if model is None or tokenizer is None:
        load_model()
    
    prompt = open("prompt.txt", "r").read() 
    print(f"prompt: {prompt}")
    
    # 构建完整的prompt
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

    # 进行文本生成
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=2048,
        temperature=0.1,  # 降低温度，让输出更稳定
        top_p=0.9,        # 核采样参数
        do_sample=True,   # 启用采样
        repetition_penalty=1.1  # 重复惩罚
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    content = tokenizer.decode(output_ids, skip_special_tokens=True).strip("\n")
    if "<think>" in content:
        content = content.split("<think>")[1].split("</think>")[1]
    # 调试信息
    # print(f"Thinking content: {thinking_content[:100]}...")
    print(f"Final content: {content}")
    
    # 检查是否包含时间信息
    if not content or content.lower() in ['无', '没有', 'none', 'no', '无时间信息', '未检测到时间信息', 'no time information detected']:
        return None
    
    # 检查是否包含时间格式（MM:DD:time）
    import re
    time_pattern = r'\d{2}:\d{2}:\d{2}:\d{2}'
    if not re.search(time_pattern, content):
        return None
    
    return content

def unload_model():
    """释放模型和分词器，释放GPU内存"""
    global model, tokenizer
    
    if model is not None:
        del model
        model = None
        print("Model unloaded from GPU")
    
    if tokenizer is not None:
        del tokenizer
        tokenizer = None
        print("Tokenizer unloaded")
    
    # 强制垃圾回收
    import gc
    import torch
    gc.collect()
    torch.cuda.empty_cache()  # 清空CUDA缓存
    print("GPU memory cleared")

