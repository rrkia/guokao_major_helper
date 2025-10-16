import csv
import argparse
import pandas as pd
import os

major_list=[{}, {}, {}]   # 第一个，第二个和第三个分别为1级（工学）、2级（电子信息类）、3级（电子信息工程），从代码映射到Major类
reverse_list=[{}, {}, {}] # 同上，但是从名字映射到Major类

class Major:
    def __init__(self, code, name, syn_list, regex=None):
        self.code = code
        self.name = name
        self.regex = regex
        self.syn_list = syn_list
        if len(code)==2:
            self.level = 1
            self.father = None
        elif len(code)==4:
            self.level = 2
            self.father = code[0:2]
        elif len(code)>=6:
            self.level = 3
            self.father = code[0:4]

with open(file=f"{os.path.dirname(os.path.realpath(__file__))}/专业目录2.csv") as csvfile:
    reader = csv.DictReader(csvfile)
    csvfile.seek(0)
    for row in reader:
        regex=None
        if row[f"准确正则"]!='':
            regex=(row[f"准确正则"]) # 例如，理学和心理学、管理学，因此在csv文件里写了避免这种情况的正则表达式
        syn_list=[]
        for i in range(1, 3):
            if row[f"等效{i}"]!='':
                syn_list.append(row[f"等效{i}"]) # 处理“可授予（*1）或（*2）学位”
        major = Major(row['代码'], row['专业'], syn_list, regex)
        # 实现第5行的映射
        major_list[major.level-1][row['代码']]=major
        # 实现第六行的映射
        if len(row["代码"])==2:
            reverse_list[0][row['专业']]=major
        elif len(row["代码"])==4:
            reverse_list[1][row['专业']]=major
        elif len(row["代码"])>=6:
            reverse_list[2][row['专业']]=major

def name_to_major(name):
    target = None
    for i in range(0, 3): # 为了防止“哲学”同时对应01和0101的情况
        if name in reverse_list[i]:
            target = reverse_list[i][name]
            return target
            break

def add_regex(result:str, major:Major): # 用‘|’将专业可能满足的多个正则表达式连接在一起
    if major.regex==None:
        result = result + f"|{major.name}"
    else:
        result = result + f"|{major.regex}"
    return result

def find_code(code=None):
    if code!=None:
        level=0
        code1=code
        result="不限"
        if len(code)==2:
            level=1
        elif len(code)==4:
            level=2
        elif len(code)>=6:
            level=3
        while level>0:
            target = major_list[level-1][code1]
            result = add_regex(result, target)
            for i in range(0, len(target.syn_list)):
                friend = name_to_major(target.syn_list[i])
                if friend==None:
                    raise FileNotFoundError("未找到专业，请检查你的输入或csv文件")
                result = add_regex(result, friend)
            code1=target.father
            level=level-1
        return result

def find_name(name=None):
    if name!=None:
        result="不限"# 同上
        target = name_to_major(name)
        if target==None:
            raise FileNotFoundError("未找到专业，请检查你的输入或csv文件")
        level = target.level
        while level>0:
            result = add_regex(result, target)
            for i in range(0, len(target.syn_list)):
                friend = name_to_major(target.syn_list[i])
                if friend==None:
                    raise FileNotFoundError("未找到专业，请检查你的输入或csv文件")
                result = add_regex(result, friend)
            code1=target.father
            level=level-1
            if level==0:
                break
            target = major_list[level-1][code1]
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", default=None, help="专业代码，将优先使用这个信息", required=False)
    parser.add_argument("--name", default=None, help="专业名称，如果你不输入专业代码将使用这个信息", required=False)
    parser.add_argument("--input", default=None, help="删除了第一行的国考岗位表", required=False)
    # parser.add_argument("--edu", default=None, help="学历", required=False) # 准备适配硕士学历
    parser.add_argument("--output", default="output.xlsx", help="输出文件", required=False)
    # parser.add_argument("--political", default=None, help="政治面貌", required=False) # 准备做
    # parser.add_argument("--project", default=None, help="参与基层服务项目", required=False)
    args = parser.parse_args()

    result = None
    if args.code!=None:
        result=find_code(args.code)
    elif args.name!=None:
        result=find_name(args.name)
    else:
        raise ValueError("请输入专业代码(--code)或完整的专业名称(--name)")
    
    if args.input!=None:
        if result==None:
            raise RuntimeError("未成功生成正则表达式")
        dfs=pd.read_excel(io=args.input, sheet_name=None, dtype={'部门代码':str, '职位代码':str})
        with pd.ExcelWriter(args.output) as writer:
            for sheet_name, df in dfs.items():
                df = df[df['专业'].str.contains(result, regex=True)]
                df.to_excel(writer, sheet_name=sheet_name)
    else:
        print(result)

