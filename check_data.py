import json
from pyArango.connection import Connection


class HotpotArangoDB:
    def __init__(self, url='http://127.0.0.1:8529', user='root', password='12345'):
        self.conn = Connection(arangoURL=url, username=user, password=password)

        # 创建数据库
        if not self.conn.hasDatabase('hotpot_multihop'):
            self.conn.createDatabase(name='hotpot_multihop')
        self.db = self.conn['hotpot_multihop']

        # 创建集合（如果不存在）
        for name in ['questions', 'documents']:
            if not self.db.hasCollection(name):
                self.db.createCollection(name=name)

        # 创建边集合
        for name in ['supports', 'follows']:
            if not self.db.hasCollection(name):
                self.db.createCollection(name=name, className='Edges')

        print("✅ 数据库初始化完成")

    def import_data(self, jsonl_path):
        """导入数据"""
        count = 0

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:

                data = json.loads(line.strip())
                q_id = data['_id']

                # 1. 创建 Question 节点
                try:
                    q_doc = self.db['questions'].createDocument({
                        '_key': q_id,
                        'question': data['question'],
                        'answer': data['answer'],
                        'type': data['type'],
                        'level': data['level']
                    })
                    q_doc.save()
                except Exception as e:
                    print(f"Question {q_id} 已存在或错误: {e}")
                    continue

                # 2. 创建 Document 节点 + supports 边 + follows 链
                prev_doc_key = None
                for fact in data['supporting_facts']:
                    doc_title, sent_idx = fact[0], fact[1]
                    d_key = f"{doc_title.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')[:50]}_{sent_idx}"

                    # 获取句子文本
                    sent_text = ""
                    if doc_title in data['context'] and sent_idx < len(data['context'][doc_title]):
                        sent_text = data['context'][doc_title][sent_idx]

                    # 创建 Document 节点（MERGE 避免重复）
                    try:
                        d_doc = self.db['documents'].createDocument({
                            '_key': d_key,
                            'title': doc_title,
                            'sentence_idx': sent_idx,
                            'sentence_text': sent_text[:500]  # 截断避免过大
                        })
                        d_doc.save()
                    except:
                        pass  # 已存在

                    # 边：Question -> Document (supports)
                    try:
                        self.db['supports'].createDocument({
                            '_from': f'questions/{q_id}',
                            '_to': f'documents/{d_key}',
                            'sentence_idx': sent_idx
                        }).save()
                    except:
                        pass
                    # 边：Document -> Document (follows，多跳顺序)
                    if prev_doc_key:
                        try:
                            self.db['follows'].createDocument({
                                '_from': f'documents/{prev_doc_key}',
                                '_to': f'documents/{d_key}',
                                'q_id': q_id
                            }).save()
                        except:
                            pass

                    prev_doc_key = d_key

                count += 1
                if count % 500 == 0:
                    print(f"已导入 {count} 条...")

        print(f"✅ 导入完成，共 {count} 条问题")


if __name__ == '__main__':
    db = HotpotArangoDB()
    db.import_data('hotpot_processed.jsonl')