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
本次正式數據使用 AMPS/助教 C++ DBTable.cpp。cpp/benchmark_ta_dbtable.cpp 負責把 ClassBench rules/trace 轉成 DBT::Rule 和 DBT::Packet，然後建立 DBT::DBTable 並量測 build、lookup、memory。scripts/run_ta_dbtable_experiment.py 會自動編譯並跑 5 次。

## 14:00-17:00 實驗結果
有效規則數 99,330，測試封包 100,000，重複 5 次。Build time avg 0.3777 秒，average lookup avg 59.902 ns，記憶體約 4.017 MiB。

## 17:00-19:00 比較分析
組員一 HybridTSS：build time 0.0249 秒、average lookup 133.987 ns、memory 709.45 MiB。組員二 CutSplit：build time 0.424338 秒、average lookup 285.687 ns、memory 537.38 MiB。更新後 DBTable C++ 實測 lookup 約 59.902 ns，是三者中最快；memory 約 4.017 MiB，也是三者最低。因此 DBTable 適合追求極低查詢延遲，並希望記憶體成本明顯低於其他對照方法的情境。

## 19:00-20:00 結論
DBTable 的核心是一句話：先用有辨識力的 bit 快速定位候選 bucket，再用完整五元組驗證正確答案。本專案完成資料集、程式、實驗、報告與 PPT。
