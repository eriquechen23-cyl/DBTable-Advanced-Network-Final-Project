# DBTable 20 分鐘投影片報告講稿

## 0:00-1:30 封面與研究目標
本次選擇 DBTable 作為 packet classification 演算法，目標是理解它如何用 discriminative bits 降低 lookup 時的候選規則數，並用 ClassBench ACL1 100K 資料做實驗。

## 1:30-4:00 Packet Classification 問題
說明五元組、priority、IP prefix、port range、protocol mask。強調查詢必須找最高優先權相符規則，因此不能只做近似分類。

## 4:00-8:00 DBTable 核心概念
介紹 discriminative bit ranking：選出能讓規則分布較平均、覆蓋率較高的 IP bit。規則依 selected bits 放入 bucket；wildcard prefix 會複製到多個 bucket。

## 8:00-11:00 架構與查詢流程
建表流程是 parser -> bit ranking -> bucket table。查詢流程是 packet key extraction -> candidate bucket -> exact five-tuple match -> best priority。

## 11:00-14:00 程式實作
說明 src/classbench.py、src/dbtable_classifier.py、scripts/run_experiment.py。強調本實作是 DBTable-inspired 教學版，不是 AMPS C++ 的完整逐行移植。

## 14:00-17:00 實驗結果
資料集有效可解析 rules: 99,330；packets tested: 100,000。Build time 1.5531 秒，average lookup 9780.5 ns，P99 35100.0 ns，memory 約 20.55 MiB。

## 17:00-19:00 比較分析
先說 DBTable 適合 IP bits 有明顯可分性的 ruleset。與 tuple-space 類方法相比，DBTable 查詢候選集合更小但 wildcard replication 是成本；與 decision-tree/cut 類方法相比，DBTable 結構較直接，但完整最佳化仍比簡單 hash table 複雜。

## 19:00-20:00 結論
總結 DBTable 的重點是把 ruleset 分布轉成快速 bucket index，降低平均 lookup 成本。後續可將 AMPS C++ 的 subset、prefix_tuple、port_node 與 SIMD/hash 最佳化納入。
