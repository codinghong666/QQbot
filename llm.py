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
    
    prompt = """请从以下QQ群消息中提取所有绝对时间信息，只输出时间，不要包含原文。

任务要求：
# 只输出时间，不要包含任何原文内容，不要输出任何无关内容，如果看起来不像需要执行的任务，只输出none
1. 提取绝对时间信息，包括：
   - 具体日期（如：9月17日、12月25日、9月24日）
   - 具体时刻（如：18:00、17:00、14:30）
   - 完整日期时间（如：9月24日18:00、9月17日17:00）
2. 即使包含相对时间词汇（如：明天、后天），只要后面有具体日期，也要提取
   - 例如："明日下午（9月17日）17:00" → 提取 "09:17:17:00"
3. 时间格式统一为：MM:DD:time
   - 如果只有日期没有时间，时间部分设为00:00
4. 每条时间信息单独一行输出

示例输出格式：
09:24:18:00
09:17:17:00
09:24:00:00

请分析以下QQ群消息：\n"""
    
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
        max_new_tokens=2048
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    # 解析thinking内容
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    
    # 检查是否包含时间信息
    if not content or content.lower() in ['无', '没有', 'none', 'no', '无时间信息', '未检测到时间信息', 'no time information detected']:
        return None
    
    # 检查是否包含时间格式（MM:DD:time）
    import re
    time_pattern = r'\d{2}:\d{2}:\d{2}:\d{2}'
    if not re.search(time_pattern, content):
        return None
    
    return content

