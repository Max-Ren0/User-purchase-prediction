# 数据文件说明

## 📊 数据文件

由于文件大小限制，以下数据文件未包含在GitHub仓库中：

### 训练数据
- **`Antai_hackathon_train.csv`** (274MB)
  - 用户购买记录数据
  - 包含字段：buyer_admin_id, item_id, create_order_time, irank
  - 约600万条记录，48万用户

### 商品属性数据
- **`Antai_hackathon_attr.csv`** (较小)
  - 商品属性信息
  - 包含字段：item_id, cate_id, store_id

### 测试数据
- **`dianshang_test.csv`** (较小)
  - 测试集用户数据
  - 包含字段：buyer_country_id, buyer_admin_id, item_id, create_order_time, irank

## 🔧 如何获取数据

1. 从比赛官网下载原始数据文件
2. 将文件放置在 `data/` 目录下
3. 确保文件命名与上述说明一致

## 📝 数据格式

所有CSV文件使用UTF-8编码，逗号分隔。

## ⚠️ 注意事项

- 数据文件较大，建议使用SSD存储
- 确保有足够的内存运行数据处理（推荐16GB+）
- 数据预处理会生成parquet格式的中间文件，这些文件已添加到.gitignore中
