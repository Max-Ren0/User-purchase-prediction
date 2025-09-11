# 🏆 算法比赛配置管理脚本
# 用于在开发和生产环境之间切换

import os
import json
from datetime import datetime

class CompetitionConfig:
    """比赛配置管理类"""
    
    def __init__(self):
        self.config_file = 'competition_config.json'
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self):
        """默认配置"""
        return {
            "development": {
                "FAST_MODE": True,
                "N_SMOKE": 5000,
                "description": "开发调试模式 - 快速验证"
            },
            "production": {
                "FAST_MODE": False,
                "N_SMOKE": None,
                "description": "生产模式 - 完整数据运行"
            },
            "params": {
                "development": {
                    "covisit_window": 2,
                    "covisit_top_per_a": 100,
                    "recent_k": 3,
                    "cand_per_recent": 20,
                    "tau_days": 14,
                    "user_top_cates": 3,
                    "user_top_stores": 3,
                    "per_cate_pool": 50,
                    "per_store_pool": 40,
                    "pop_pool": 1000,
                    "recall_cap": 300,
                    "batch_size": 1000
                },
                "production": {
                    "covisit_window": 3,
                    "covisit_top_per_a": 200,
                    "recent_k": 5,
                    "cand_per_recent": 40,
                    "tau_days": 14,
                    "user_top_cates": 3,
                    "user_top_stores": 3,
                    "per_cate_pool": 80,
                    "per_store_pool": 60,
                    "pop_pool": 2000,
                    "recall_cap": 600,
                    "batch_size": 2000
                }
            },
            "current_mode": "development",
            "last_updated": datetime.now().isoformat()
        }
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def set_mode(self, mode):
        """设置运行模式"""
        if mode not in ['development', 'production']:
            raise ValueError("模式必须是 'development' 或 'production'")
        
        self.config['current_mode'] = mode
        self.config['last_updated'] = datetime.now().isoformat()
        self.save_config()
        
        print(f"✅ 已切换到 {mode} 模式")
        print(f"📊 当前配置: {self.config[mode]}")
    
    def get_current_config(self):
        """获取当前配置"""
        mode = self.config['current_mode']
        return {
            'mode': mode,
            'fast_mode': self.config[mode]['FAST_MODE'],
            'n_smoke': self.config[mode]['N_SMOKE'],
            'params': self.config['params'][mode],
            'description': self.config[mode]['description']
        }
    
    def update_production_params(self, new_params):
        """更新生产环境参数（基于开发调优结果）"""
        self.config['params']['production'].update(new_params)
        self.config['last_updated'] = datetime.now().isoformat()
        self.save_config()
        print("✅ 生产环境参数已更新")
    
    def print_status(self):
        """打印当前状态"""
        config = self.get_current_config()
        print(f"\n🏆 比赛配置状态")
        print(f"📊 当前模式: {config['mode']}")
        print(f"⚡ 快速模式: {config['fast_mode']}")
        if config['n_smoke']:
            print(f"👥 用户数量: {config['n_smoke']:,}")
        else:
            print(f"👥 用户数量: 全部用户")
        print(f"📝 描述: {config['description']}")
        print(f"⏰ 最后更新: {self.config['last_updated']}")

# 使用示例
if __name__ == "__main__":
    config = CompetitionConfig()
    
    print("🏆 算法比赛配置管理")
    print("=" * 50)
    
    # 显示当前状态
    config.print_status()
    
    print("\n📋 可用命令:")
    print("1. config.set_mode('development')  # 切换到开发模式")
    print("2. config.set_mode('production')   # 切换到生产模式")
    print("3. config.print_status()           # 显示当前状态")
    print("4. config.get_current_config()     # 获取当前配置")
