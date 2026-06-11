# DBTable 20 分鐘投影片報告講稿

## 0:00-1:30 封面與研究目標
本次選擇 DBTable 作為 packet classification 演算法。我的重點不是只展示程式結果，而是說清楚論文方法：DBTable 如何用 discriminative bitsets 把十萬筆規則切成較小的候選集合。

## 1:30-4:00 Packet Classification 問題
封包分類要看五元組：來源 IP、目的 IP、來源埠、目的埠、協定。每條規則有 prefix、range、mask 與 priority。查詢時必須找最高優先權的匹配規則。

## 4:00-8:30 DBTable 白話版
DBTable 像圖書館索引。沒有索引時要一本一本找；DBTable 先從規則中挑出最能分辨位置的 bit，做成索引。封包進來時先用這些 bit 找到小 bucket，再在 bucket 中做完整比對。這樣不會漏掉正確答案，因為最後仍然做 exact match。

## 8:30-11:30 為什麼會快、代價是什麼
快的原因是候選規則變少。代價是建表需要先分析 ruleset，而且 wildcard prefix 可能讓規則被放到多個 bucket，增加記憶體。也就是用建表成本和記憶體換查詢速度。

## 11:30-14:00 程式實作
src/classbench.py 解析 ClassBench 規則與 trace；src/dbtable_classifier.py 選 discriminative bits、建立 bucket table、查詢時做 exact match。這是 DBTable-inspired 教學版，不是 AMPS C++ 的完整逐行移植。

## 14:00-17:00 實驗結果
有效規則數 99,330，測試封包 100,000。Build time 1.5531 秒，average lookup 9780.5 ns，P99 lookup 35100.0 ns，記憶體約 20.55 MiB。

## 17:00-19:00 比較分析
DBTable 適合 IP prefix 分布有可分辨性的 ruleset。若和 tuple-space 類方法比，DBTable 查詢候選集合較小，但 wildcard replication 是成本。若和 decision-tree 類方法比，DBTable 架構較像查表，較容易解釋，但完整最佳化仍有複雜度。

## 19:00-20:00 結論
DBTable 的核心是一句話：先用有辨識力的 bit 快速定位候選 bucket，再用完整五元組驗證正確答案。本專案完成資料集、程式、實驗、報告與 PPT。
