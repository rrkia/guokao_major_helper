# 使用方式
1. `git clone https://github.com/rrkia/guokao_major_helper.git`
2. 准备好每一页都去掉了第一行的国考岗位表
3. 查找你的本科专业代码或名称
4. `python guokao_filter2.py --code $专业代码 --input xxxxxx.xls`
   或 `python guokao_filter2.py --name $专业名称 --input xxxxxx.xls`
5. 查看output.xlsx并做进一步筛选
# 注意事项
- 本项目只对本科专业做了处理，尚未处理研究生专业
- 对于类似于`（注：可授经济学或管理学学士学位）`的岗位，本项目认为可以报可授范围的专业，具体情况请自行咨询
- 本项目仍然可能有筛选不准确的风险，如有改进方案欢迎提出
