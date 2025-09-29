#!/usr/bin/env python3
"""
自动破C段工具
功能：对IP文件进行排序，并根据相邻IP的差值进行补全
"""

import argparse
import sys
from typing import List, Tuple

def ip_to_int(ip: str) -> int:
    """将IP地址转换为整数"""
    parts = ip.split('.')
    if len(parts) != 4:
        raise ValueError(f"无效的IP地址: {ip}")
    
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

def int_to_ip(ip_int: int) -> str:
    """将整数转换为IP地址"""
    return f"{(ip_int >> 24) & 255}.{(ip_int >> 16) & 255}.{(ip_int >> 8) & 255}.{ip_int & 255}"

def sort_ips(ip_list: List[str]) -> List[str]:
    """对IP地址列表进行排序"""
    ip_ints = [ip_to_int(ip) for ip in ip_list]
    ip_ints.sort()
    return [int_to_ip(ip_int) for ip_int in ip_ints]

def generate_ip_range(start_ip: str, end_ip: str) -> List[str]:
    """生成从start_ip到end_ip的连续IP范围"""
    start_int = ip_to_int(start_ip)
    end_int = ip_to_int(end_ip)
    
    return [int_to_ip(i) for i in range(start_int, end_int + 1)]

def process_ips(sorted_ips: List[str]) -> List[str]:
    """处理排序后的IP列表，根据规则进行补全"""
    if not sorted_ips:
        return []
    
    result = []
    previous_ip = sorted_ips[0]
    previous_int = ip_to_int(previous_ip)
    start_ip = previous_ip
    end_ip = previous_ip
    
    for i in range(1, len(sorted_ips)):
        current_ip = sorted_ips[i]
        current_int = ip_to_int(current_ip)
        current_network = '.'.join(current_ip.split('.')[:3])
        previous_network = '.'.join(previous_ip.split('.')[:3])
        
        diff = current_int - previous_int
        
        # 检查是否属于同一C段且差值不超过6
        if current_network == previous_network and 0 < diff <= 6:
            end_ip = current_ip
        else:
            # 输出前一段的结果
            if start_ip == end_ip:
                result.append(start_ip)
            else:
                result.extend(generate_ip_range(start_ip, end_ip))
            
            # 开始新的段
            start_ip = current_ip
            end_ip = current_ip
        
        previous_ip = current_ip
        previous_int = current_int
    
    # 处理最后一段
    if start_ip == end_ip:
        result.append(start_ip)
    else:
        result.extend(generate_ip_range(start_ip, end_ip))
    
    return result

def read_ip_file(filename: str) -> List[str]:
    """从文件读取IP地址列表"""
    ips = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                ip = line.strip()
                if ip:  # 跳过空行
                    # 验证IP格式
                    parts = ip.split('.')
                    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                        ips.append(ip)
                    else:
                        print(f"警告: 跳过无效的IP地址: {ip}", file=sys.stderr)
    except FileNotFoundError:
        print(f"错误: 输入文件不存在: {filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件时发生错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    return ips

def write_output(result: List[str], output_file: str = None):
    """将结果写入文件或输出到控制台"""
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for ip in result:
                    f.write(ip + '\n')
            print(f"结果已保存到: {output_file}")
        except Exception as e:
            print(f"错误: 写入输出文件时发生错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("处理结果:")
        for ip in result:
            print(ip)
    
    print(f"总共生成 {len(result)} 个IP地址")

def main():
    parser = argparse.ArgumentParser(
        description="自动破C段工具 - 对IP文件进行排序并根据相邻IP的差值进行补全",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -l ip_list.txt -o result.txt
  %(prog)s -l ip_list.txt

说明:
  程序会对IP进行排序，当相邻IP的最后一个字节差值不超过6时进行补全
  例如: 192.168.1.1 和 192.168.1.7 会补全为 192.168.1.1-192.168.1.7
        """
    )
    
    parser.add_argument('-l', '--list', required=True, help='输入文件，包含IP地址列表')
    parser.add_argument('-o', '--output', help='输出文件（可选，默认输出到控制台）')
    
    args = parser.parse_args()
    
    # 读取输入文件
    print(f"开始处理IP文件: {args.list}")
    ip_list = read_ip_file(args.list)
    
    if not ip_list:
        print("错误: 输入文件中没有有效的IP地址", file=sys.stderr)
        sys.exit(1)
    
    print(f"读取到 {len(ip_list)} 个有效IP地址")
    print("排序IP地址...")
    
    # 排序IP
    sorted_ips = sort_ips(ip_list)
    
    print("分析IP段并补全...")
    
    # 处理IP并生成结果
    result = process_ips(sorted_ips)
    
    # 输出结果
    write_output(result, args.output)

if __name__ == "__main__":
    main()
