# 資料分析流程（標準規格）

## Step 0 - 初始化（Initialization）

輸入：

- dataset
- metadata（如果有）

必須先：

1. 讀取資料
2. 確認格式
3. 建立資料摘要

輸出：

- dataset shape
- column list
- data types

---

## Step 1 - 結構檢查（Schema Inspection）

必須判斷：

- number of rows
- number of columns
- column type

分類為：

- numeric
- categorical
- datetime
- text
- boolean

輸出：

- schema report

例如：

```yaml
column_summary:
  age: numeric
  gender: categorical
  wage: numeric
  education: numeric
```

---

## Step 2 - 資料品質檢查（Data Quality Audit）

必須檢查：

### Missing values

輸出：

```text
missing_ratio[column]
```

規則：

```text
if missing_ratio > 30%
    flag column
```

### Duplicate rows

```text
duplicate_ratio
```

### Outliers

數值變數：

```text
zscore > 3
```

或：

```text
IQR method
```

輸出：

```text
outlier_summary
```

---

## Step 3 - 資料清理（Data Cleaning）

必須根據規則處理：

### Missing values

```text
numeric -> median
categorical -> mode
```

或標記：

```text
missing_flag
```

### Outliers

規則：

```text
if extreme_outlier:
    remove
else:
    winsorize
```

### Type correction

例如：

```text
string -> datetime
string -> categorical
```

輸出：

```text
clean_dataset
```

---

## Step 4 - 探索式分析（EDA）

必須產生：

### 單變量統計

對所有 numeric variable 計算：

```text
mean
median
std
min
max
skewness
kurtosis
```

### 分布圖

建議生成：

```text
histogram
density
boxplot
```

### 類別統計

對 categorical variable 計算：

```text
frequency
proportion
```

輸出：

```text
eda_report
```

---

## Step 5 - 關係探索（Relationship Analysis）

必須分析變數關係。

### Numeric vs Numeric

計算：

```text
correlation matrix
```

生成：

```text
scatter plots
```

### Categorical vs Numeric

計算：

```text
group mean
ANOVA
```

### Categorical vs Categorical

計算：

```text
contingency table
chi-square
```

輸出：

```text
relationship_report
```

---

## Step 6 - 任務判定（Task Identification）

必須判斷分析類型：

```text
if target_variable exists:
    supervised learning
else:
    unsupervised learning
```

Target type：

```text
numeric -> regression
categorical -> classification
none -> clustering / segmentation
```

輸出：

```text
analysis_task
```

---

## Step 7 - 特徵工程（Feature Engineering）

可自動建立：

```text
log transforms
ratios
interaction terms
date features
```

例如：

```text
income_per_person
purchase_frequency
customer_lifetime
```

輸出：

```text
feature_dataset
```

---

## Step 8 - 建模（Modeling）

根據任務自動選擇模型。

### Regression 候選

```text
OLS
Ridge
RandomForest
GradientBoosting
```

### Classification 候選

```text
Logistic
RandomForest
XGBoost
SVM
```

### Clustering 候選

```text
KMeans
Hierarchical
DBSCAN
```

---

## Step 9 - 模型評估（Evaluation）

必須使用：

### Regression

```text
R²
RMSE
MAE
```

### Classification

```text
accuracy
precision
recall
F1
AUC
```

### Clustering

```text
silhouette score
cluster size distribution
```

輸出：

```text
model_performance
```

---

## Step 10 - 解釋與洞察（Insight Extraction）

必須產生：

- 重要變數
- 影響方向
- 商業意義

例如：

```text
education increases wage
age negatively correlates with churn
```

輸出：

```text
insight_summary
```

---

## Step 11 - 視覺化（Visualization）

必須生成必備圖表：

```text
distribution plots
correlation heatmap
feature importance
model diagnostics
```

輸出：

```text
visualization_set
```

---

## Step 12 - 最終報告（Report Generation）

必須整合：

```text
dataset overview
data quality
EDA findings
model results
key insights
recommendations
```

輸出：

```text
analysis_report
```

---

# 簡化版流程

最核心的流程只有六步：

```text
1 Load Data
2 Inspect Schema
3 Clean Data
4 EDA
5 Model
6 Interpret Results
```

---

# 更進階的版本

```text
1. Understand Dataset
2. Audit Data Quality
3. Clean Data
4. Perform EDA
5. Detect Relationships
6. Determine Analysis Task
7. Feature Engineering
8. Train Models
9. Evaluate Models
10. Generate Insights
11. Visualize Results
12. Produce Report
```
