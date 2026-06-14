import pandas as pd
import json
import numpy as np


def parse_supporting_facts(facts):
    """解析 supporting_facts 字段，兼容 numpy 和字符串"""
    title = facts['title']
    sent_id = facts['sent_id']

    # 统一转换为字符串再解析
    if isinstance(title, np.ndarray):
        title = title.tolist()
    if isinstance(sent_id, np.ndarray):
        sent_id = sent_id.tolist()

    # 如果是字符串，去掉 numpy array 的格式前缀
    if isinstance(title, str):
        title = title.replace('array(', '[').replace(', dtype=object)', ']')
        try:
            import ast
            title = ast.literal_eval(title)
        except:
            title = [title]

    if isinstance(sent_id, str):
        sent_id = sent_id.replace('array(', '[').replace(', dtype=object)', ']')
        try:
            import ast
            sent_id = ast.literal_eval(sent_id)
        except:
            sent_id = [sent_id]

    # 确保是列表
    if not isinstance(title, list):
        title = [title]
    if not isinstance(sent_id, list):
        sent_id = [sent_id]

    # 处理嵌套列表
    result = []
    for t, s in zip(title, sent_id):
        if isinstance(t, list):
            t = t[0] if t else ''
        if isinstance(s, list):
            s = s[0] if s else 0
        result.append((str(t), int(s)))

    return result


def parse_context(context):
    """解析 context 字段"""
    titles = context['title']
    sentences = context['sentences']

    # 处理 titles
    if isinstance(titles, np.ndarray):
        titles = titles.tolist()
    if isinstance(titles, str):
        titles = titles.replace('array(', '[').replace(', dtype=object)', ']')
        try:
            import ast
            titles = ast.literal_eval(titles)
        except:
            titles = [titles]

    # 处理 sentences（可能是 numpy array 的列表）
    if isinstance(sentences, np.ndarray):
        sentences = sentences.tolist()

    # 确保 sentences 是列表的列表
    if not isinstance(sentences, list):
        sentences = [sentences]

    # 构建文档映射
    doc_map = {}
    for i, title in enumerate(titles):
        if i < len(sentences):
            sents = sentences[i]
            if isinstance(sents, np.ndarray):
                sents = sents.tolist()
            doc_map[str(title)] = sents

    return doc_map


def preprocess():
    df = pd.read_parquet('train-00000-of-00002.parquet')
    print(f"原始数据: {len(df)} 条")

    processed = []
    for idx, row in df.iterrows():
        try:
            supporting_facts = parse_supporting_facts(row['supporting_facts'])
            context = parse_context(row['context'])
            entities = list(set([fact[0] for fact in supporting_facts]))

            item = {
                '_id': str(row['id']),
                'question': row['question'],
                'answer': row['answer'],
                'type': row['type'],
                'level': row['level'],
                'entities': entities,
                'supporting_facts': supporting_facts,
                'context': context
            }
            processed.append(item)

            if (idx + 1) % 1000 == 0:
                print(f"已处理 {idx + 1} 条，成功 {len(processed)} 条...")

        except Exception as e:
            print(f"跳过第 {idx} 条: {e}")
            continue

    with open('hotpot_processed.jsonl', 'w', encoding='utf-8') as f:
        for item in processed:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 预处理完成，共 {len(processed)} 条")

    if processed:
        print("\n样例数据:")
        print(json.dumps(processed[0], ensure_ascii=False, indent=2)[:2000])


if __name__ == '__main__':
    preprocess()