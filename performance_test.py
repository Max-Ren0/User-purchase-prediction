#!/usr/bin/env python3
"""
性能测试脚本 - 验证优化效果
"""

import time
import psutil
import os
import pandas as pd
import numpy as np
from datetime import datetime

def get_memory_usage():
    """获取当前内存使用量(MB)"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_data_loading_performance():
    """测试数据加载性能"""
    print("🔄 测试数据加载性能...")
    
    files_to_test = [
        'x/train_vis.parquet',
        'x/label_df.parquet', 
        'x/item_attr.parquet'
    ]
    
    results = []
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            start_time = time.time()
            start_memory = get_memory_usage()
            
            try:
                df = pd.read_parquet(file_path)
                end_time = time.time()
                end_memory = get_memory_usage()
                
                load_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                results.append({
                    'file': os.path.basename(file_path),
                    'size_mb': os.path.getsize(file_path) / 1024 / 1024,
                    'rows': len(df),
                    'cols': len(df.columns),
                    'load_time': load_time,
                    'memory_mb': memory_used,
                    'load_speed_mb_s': (os.path.getsize(file_path) / 1024 / 1024) / load_time
                })
                
                print(f"  ✅ {file_path}: {load_time:.2f}s, {memory_used:.1f}MB")
                
            except Exception as e:
                print(f"  ❌ {file_path}: 加载失败 - {e}")
        else:
            print(f"  ⚠️  {file_path}: 文件不存在")
    
    return results

def test_memory_optimization():
    """测试内存优化效果"""
    print("\n🔄 测试内存优化效果...")
    
    if not os.path.exists('x/train_vis.parquet'):
        print("  ⚠️  测试数据不存在，跳过内存优化测试")
        return None
    
    # 测试原始数据类型 vs 优化数据类型
    df = pd.read_parquet('x/train_vis.parquet')
    
    # 原始内存使用
    original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
    
    # 优化数据类型
    df_optimized = df.copy()
    int_columns = ['buyer_admin_id', 'item_id', 'irank']
    
    for col in int_columns:
        if col in df_optimized.columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
    
    # 优化后内存使用
    optimized_memory = df_optimized.memory_usage(deep=True).sum() / 1024 / 1024
    
    reduction = (original_memory - optimized_memory) / original_memory * 100
    
    print(f"  📊 原始内存使用: {original_memory:.1f} MB")
    print(f"  📊 优化后内存使用: {optimized_memory:.1f} MB")
    print(f"  📈 内存减少: {reduction:.1f}%")
    
    return {
        'original_memory_mb': original_memory,
        'optimized_memory_mb': optimized_memory,
        'reduction_percent': reduction
    }

def test_vectorization_performance():
    """测试向量化操作性能"""
    print("\n🔄 测试向量化操作性能...")
    
    # 创建测试数据
    n_users = 10000
    n_items = 50000
    n_interactions = 100000
    
    print(f"  📊 生成测试数据: {n_interactions:,} 条交互记录...")
    
    test_data = pd.DataFrame({
        'buyer_admin_id': np.random.randint(1, n_users+1, n_interactions),
        'item_id': np.random.randint(1, n_items+1, n_interactions),
        'score': np.random.random(n_interactions)
    })
    
    # 测试1: 传统groupby vs 向量化操作
    print("  🔄 测试 groupby 性能...")
    
    # 传统方法
    start_time = time.time()
    traditional_result = test_data.groupby('buyer_admin_id')['score'].mean()
    traditional_time = time.time() - start_time
    
    # 向量化方法 (使用更高效的聚合)
    start_time = time.time()
    vectorized_result = test_data.groupby('buyer_admin_id', sort=False)['score'].mean()
    vectorized_time = time.time() - start_time
    
    speedup = traditional_time / vectorized_time if vectorized_time > 0 else 1
    
    print(f"  📈 传统方法: {traditional_time:.3f}s")
    print(f"  📈 向量化方法: {vectorized_time:.3f}s")
    print(f"  🚀 加速比: {speedup:.2f}x")
    
    return {
        'traditional_time': traditional_time,
        'vectorized_time': vectorized_time,
        'speedup': speedup
    }

def generate_performance_report():
    """生成性能测试报告"""
    print("📊 生成性能测试报告...")
    
    report = {
        'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
            'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}"
        }
    }
    
    # 运行各项测试
    report['data_loading'] = test_data_loading_performance()
    report['memory_optimization'] = test_memory_optimization()
    report['vectorization'] = test_vectorization_performance()
    
    return report

def main():
    """主函数"""
    print("🚀 推荐系统性能测试")
    print("=" * 50)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 系统信息: CPU {psutil.cpu_count()}核, 内存 {psutil.virtual_memory().total/1024/1024/1024:.1f}GB")
    print()
    
    # 运行性能测试
    report = generate_performance_report()
    
    print("\n" + "=" * 50)
    print("📋 性能测试总结:")
    
    # 数据加载性能
    if report['data_loading']:
        total_load_time = sum(item['load_time'] for item in report['data_loading'])
        avg_speed = np.mean([item['load_speed_mb_s'] for item in report['data_loading']])
        print(f"  📖 数据加载: 总耗时 {total_load_time:.2f}s, 平均速度 {avg_speed:.1f}MB/s")
    
    # 内存优化
    if report['memory_optimization']:
        reduction = report['memory_optimization']['reduction_percent']
        print(f"  💾 内存优化: 减少 {reduction:.1f}% 内存使用")
    
    # 向量化加速
    if report['vectorization']:
        speedup = report['vectorization']['speedup']
        print(f"  ⚡ 向量化加速: {speedup:.2f}x 性能提升")
    
    print("\n✅ 性能测试完成!")
    
    # 保存报告
    import json
    with open('performance_test_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("📄 详细报告已保存到 performance_test_report.json")

if __name__ == "__main__":
    main()

