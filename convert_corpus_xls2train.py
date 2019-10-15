# -*- coding:utf-8 -*-
# 作者    : 高菲
# 创建时间: 2019/10/14 15:10
# 文件    : convert_corpus_xls2train.py
# IDE     : PyCharm   
# FUNCTION:
""" 用于将固定格式的xls文档，转换为实体识别和关系抽取模型的原始数据 """
import argparse
import json

from excel_handing import ExcelReader, ExcelWriter

parser = argparse.ArgumentParser('Parameter settings')
parser.add_argument('--algorithmic', default='', type=str, required=True, help='确认后的xls文件')
parser.add_argument('--entity_extract_dir', default='', type=str, required=False, help='生成的实体识别语料文件夹')
parser.add_argument('--relation_extract_dir', default='', type=str, required=False, help='生成的关系识别语料文件夹')
parser.add_argument('--entity_extract_rate', default=[7, 2, 1], type=list, required=False, help='生成训练测试文件的比例')
parser.add_argument('--relation_extract_rate', default=[8, 2], type=list, required=False, help='生成训练测试文件的比例')
args = parser.parse_args()


# 将固定格式内容，解析为json对象
def content2obj(content):
    content = content.replace('##', r'\n')
    print('*' * 100)
    print(content)
    content_obj = json.loads(content)
    print(content_obj['content'])
    for k, v in content_obj.items():
        print(k, ': ', v)
    return content_obj


# --- 提取excel文件内容 ---
ew = ExcelWriter(args.algorithmic)
contents = ew.read_all()
print('contents:', contents)
if len(contents) > 1:
    contents = [con[1] for con in contents[1:]]
    for con in contents:
        print('con: ', con)
        con_obj = content2obj(con)
        # - 生成实体识别文件：example.train, example.dev, example.test
        #     -- 提取内容、实体位置、实体类型
        #     -- 将实体内容打标为BIE类型
        content = con_obj.get('content', '')  # 内容
        labels_arr = ['O' for _ in content]  # 初始化标记
        print('*' * 100)
        print(len(content), content)
        print(len(labels_arr), labels_arr)
        print('*' * 100)
        # print(content)
        annotations = con_obj.get('annotations', [])
        details = con_obj.get('details', [])
        # 构建标签
        for i, ann in enumerate(annotations):
            startIndex = ann['startIndex']
            endIndex = ann['endIndex']
            chinese = details[i]['chinese']
            conceptType = details[i]['conceptType']
            for j, v in enumerate(range(startIndex, endIndex)):
                if j == 0:
                    labels_arr[v] = 'B-' + conceptType
                elif v == endIndex - 1:
                    labels_arr[v] = 'E-' + conceptType
                else:
                    labels_arr[v] = 'I-' + conceptType
        # 写入文件
        # 提取实体
        rate = args.entity_extract_rate
        with open('example.train', 'w', encoding='utf-8') as fw:
            for index, con in enumerate(content):
                if con != '\n':
                    fw.write(con + ' ' + labels_arr[index] + '\n')
                if con in ['！', '。', '；', '!', '.', ';', '?', '\n']:
                    fw.write('\n')

        # 提取关系
        relations = con_obj.get('relations', [])
        with open('train.txt', 'w', encoding='utf-8') as fw:
            for index, relation in enumerate(relations):
                source = relation['source']
                target = relation['target']
                rel = relation['relation']
                text = relation['from']
                text = text.replace(' ', '').replace('\n', '')
                fw.write(' '.join([source, target, rel, text]) + '\n')

# - 生成关系识别文件：train.txt, test.txt
#     -- 提取实体1、实体2以及出现的文段
#     -- 同时获取relation2id
# 测试
if __name__ == '__main__':
    pass
