from simple_qq_parser import get_and_parse_messages
from llm import extract_time_info
from datetime import datetime
import os

def work():
    # Get messages from all configured groups
    results = get_and_parse_messages()
    
    # 创建输出文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/qq_messages_analysis_{timestamp}.txt"
    
    if results:
        print(f"\n=== Summary: Processed {len(results)} groups ===")
        print(f"Output will be saved to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"QQ Group Message Time Information Extraction Results\n")
            f.write(f"Number of groups processed: {len(results)}\n")
            f.write("="*60 + "\n\n")
            
            for group_id, group_data in results.items():
                group_name = group_data['group_name']
                message_count = len(group_data['messages'])
                
                print(f"\n=== Processing Group: {group_name} ({message_count} messages) ===")
                f.write(f"Group: {group_name}\n")
                f.write("-"*40 + "\n")
                
                for i, message in enumerate(group_data['messages'], 1):
                    print(f"\n--- Message {i} ---")
                    print("Original message:")
                    print(message)
                    
                    # Extract time information
                    print("\nTime information extraction:")
                    
                    try:
                        time_info = extract_time_info(message)
                        if time_info is not None:
                            result_line = f"{time_info}:\n{message}"
                            print(result_line)
                            f.write(f"{result_line}\n")
                        else:
                            print("No time information detected")
                    except Exception as e:
                        error_msg = f"Time extraction failed: {e}"
                        print(error_msg)
                    
                    print("\n" + "="*50)
        
        print(f"\nAnalysis completed! Results saved to: {output_file}")
    else:
        print("No groups processed")

if __name__ == "__main__":
    work()