```master```分支下有3个文件夹，```DS```、```Merge-Cross```、```trim```文件夹。

**Introduction**

* ```DS```目的是协助处理本地化部署的DeepSeek。将```Dify```中生成的```抗生素浓度数据.txt```先用```txt2json_new4.py```进行处理，生成```抗生素浓度数据1.json```等3个```.json```文件。3个```.json```文件经过```json2excel_new4.py```处理后生成3个```抗生素浓度数据1.xlsx```等3个excel，表示3篇```PaperID```不同的文献经过4个迭代（deepseek_chat、deepseek_coder、ChatGPT_4o_mini、ChatGPT_41_mini）在话术一、话术二下的结果统计表。
* ```Merge-Cross```用于将5种AI模型的输出结果进行交叉验证。```json2excel.py```与```docx2excel.py```将存放在```.docx```或```.json```中的AI输出结果转化为excel。```Merge-Cross.py```则作用于一种话术下某一篇文献的所有输出结果的excel，生成一个```merge-cross-validation.xlsx```。```1永定河``是生成excel的一个示例。
* ```trim```通过去除科学文献pdf中参考文献部分来缩短文献篇幅，提高信息提取效率。```trim_pdf.ipynb```作用于```MXenes```文件夹中子文件夹```9篇文献```中的pdf，将去除参考文献后的文献存放在```trimm```文件夹中。

