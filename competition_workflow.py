# 🏆 算法比赛完整工作流程脚本
# 自动化处理从开发到生产的完整流程

import os
import subprocess
import time
from datetime import datetime
from competition_config import CompetitionConfig

class CompetitionWorkflow:
    """比赛工作流程管理"""
    
    def __init__(self):
        self.config = CompetitionConfig()
        self.notebooks = [
            'notebooks/0_prep.ipynb',
            'notebooks/1_recall.ipynb', 
            'notebooks/2_rank.ipynb',
            'notebooks/3_eval.ipynb',
            'notebooks/4_online.ipynb'
        ]
    
    def run_notebook(self, notebook_path, mode='development'):
        """运行单个notebook"""
        print(f"\n🔄 运行 {notebook_path} ({mode} 模式)")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # 使用jupyter nbconvert执行notebook
            cmd = [
                'jupyter', 'nbconvert', 
                '--execute', 
                '--to', 'notebook',
                '--inplace',
                notebook_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                end_time = time.time()
                print(f"✅ {notebook_path} 执行成功")
                print(f"⏰ 耗时: {end_time - start_time:.2f}秒")
                return True
            else:
                print(f"❌ {notebook_path} 执行失败")
                print(f"错误信息: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 执行 {notebook_path} 时出错: {e}")
            return False
    
    def development_phase(self):
        """开发阶段：快速验证"""
        print("\n🚀 开始开发阶段")
        print("=" * 50)
        
        # 切换到开发模式
        self.config.set_mode('development')
        
        # 运行notebooks
        for notebook in self.notebooks:
            if os.path.exists(notebook):
                success = self.run_notebook(notebook, 'development')
                if not success:
                    print(f"❌ 开发阶段在 {notebook} 失败，请检查")
                    return False
            else:
                print(f"⚠️  {notebook} 不存在，跳过")
        
        print("\n✅ 开发阶段完成！")
        print("📊 请检查结果，进行参数调优")
        return True
    
    def production_phase(self, optimized_params=None):
        """生产阶段：完整数据运行"""
        print("\n🏭 开始生产阶段")
        print("=" * 50)
        
        # 切换到生产模式
        self.config.set_mode('production')
        
        # 如果提供了优化参数，更新配置
        if optimized_params:
            self.config.update_production_params(optimized_params)
            print("✅ 已应用优化参数")
        
        # 运行notebooks
        for notebook in self.notebooks:
            if os.path.exists(notebook):
                success = self.run_notebook(notebook, 'production')
                if not success:
                    print(f"❌ 生产阶段在 {notebook} 失败，请检查")
                    return False
            else:
                print(f"⚠️  {notebook} 不存在，跳过")
        
        print("\n✅ 生产阶段完成！")
        print("📄 提交文件已生成")
        return True
    
    def full_pipeline(self, optimized_params=None):
        """完整流水线：开发 + 生产"""
        print("\n🏆 开始完整比赛流水线")
        print("=" * 60)
        
        # 开发阶段
        if not self.development_phase():
            return False
        
        # 等待用户确认
        print("\n" + "=" * 60)
        print("⏸️  开发阶段完成，请检查结果")
        print("📊 如果满意，请输入 'y' 继续生产阶段")
        print("🔧 如需调优参数，请修改 competition_config.py 后重新运行")
        
        user_input = input("\n是否继续生产阶段？(y/n): ").strip().lower()
        
        if user_input != 'y':
            print("⏸️  已暂停，请调优后重新运行")
            return False
        
        # 生产阶段
        if not self.production_phase(optimized_params):
            return False
        
        print("\n🎉 完整流水线执行成功！")
        print("📄 请检查生成的提交文件")
        return True
    
    def quick_test(self):
        """快速测试：只运行关键notebooks"""
        print("\n⚡ 快速测试模式")
        print("=" * 40)
        
        # 只运行召回和排序
        key_notebooks = [
            'notebooks/1_recall.ipynb',
            'notebooks/2_rank.ipynb'
        ]
        
        self.config.set_mode('development')
        
        for notebook in key_notebooks:
            if os.path.exists(notebook):
                success = self.run_notebook(notebook, 'development')
                if not success:
                    return False
            else:
                print(f"⚠️  {notebook} 不存在")
        
        print("\n✅ 快速测试完成！")
        return True

# 使用示例
if __name__ == "__main__":
    workflow = CompetitionWorkflow()
    
    print("🏆 算法比赛工作流程管理")
    print("=" * 50)
    print("1. workflow.development_phase()     # 开发阶段")
    print("2. workflow.production_phase()      # 生产阶段") 
    print("3. workflow.full_pipeline()         # 完整流水线")
    print("4. workflow.quick_test()            # 快速测试")
    
    # 显示当前配置
    workflow.config.print_status()
